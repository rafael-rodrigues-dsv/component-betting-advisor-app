"""
Ticket Application Service - Lógica de aplicação para tickets.

Orquestra operações de criação, busca e gestão de tickets.
"""

from typing import List, Optional
import uuid
import logging

from domain.models.ticket_model import Ticket
from domain.models.bet_model import Bet
from domain.enums.ticket_status_enum import TicketStatus
from domain.enums.market_type_enum import MarketType
from infrastructure.database.repositories.ticket_repository import TicketRepository
from infrastructure.external.api_football.service import APIFootballService
from domain.services.bet_result_service import BetResultService
from web.mappers.ticket_mapper import map_market_dto_to_domain

logger = logging.getLogger(__name__)


class TicketApplicationService:
    """
    Application Service para Tickets.

    Responsável por:
    - Criar tickets
    - Buscar tickets
    - Atualizar status
    - Obter estatísticas
    """

    def __init__(self):
        self.repository = TicketRepository()
        self.api_service = APIFootballService()

    def create_ticket(
        self,
        name: str,
        bets_data: List[dict],
        stake: float,
        bookmaker_id: str
    ) -> Ticket:
        """
        Cria um novo ticket.

        Args:
            name: Nome do ticket
            bets_data: Lista de dicts com dados das apostas
            stake: Valor apostado
            bookmaker_id: ID da casa de apostas

        Returns:
            Ticket criado
        """
        # Cria ID único
        ticket_id = str(uuid.uuid4())

        # Converte bets_data para objetos Bet
        bets = []
        for bet_data in bets_data:
            bet = Bet(
                match_id=bet_data['match_id'],
                home_team=bet_data['home_team'],
                away_team=bet_data['away_team'],
                league=bet_data.get('league', ''),
                market=map_market_dto_to_domain(bet_data['market']),
                predicted_outcome=bet_data['predicted_outcome'],
                odds=bet_data['odds'],
                confidence=bet_data['confidence']
            )
            bets.append(bet)

        # Cria ticket
        ticket = Ticket(
            id=ticket_id,
            name=name,
            bets=bets,
            stake=stake,
            bookmaker_id=bookmaker_id,
            status=TicketStatus.PENDING
        )

        # Salva no banco
        self.repository.create(ticket)

        logger.info(f"🎫 Ticket criado: {ticket.name} ({len(bets)} apostas, R$ {stake})")

        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Busca ticket por ID.

        Args:
            ticket_id: ID do ticket

        Returns:
            Ticket ou None
        """
        return self.repository.find_by_id(ticket_id)

    def list_tickets(self, limit: int = 10, offset: int = 0) -> List[Ticket]:
        """
        Lista tickets (paginado).

        Args:
            limit: Número máximo de tickets
            offset: Offset para paginação

        Returns:
            Lista de tickets
        """
        return self.repository.find_all(limit=limit, offset=offset)

    def update_ticket_status(self, ticket_id: str, status: TicketStatus) -> bool:
        """
        Atualiza status de um ticket.

        Args:
            ticket_id: ID do ticket
            status: Novo status

        Returns:
            True se atualizado
        """
        return self.repository.update_status(ticket_id, status)

    def delete_ticket(self, ticket_id: str) -> bool:
        """
        Deleta um ticket.

        Args:
            ticket_id: ID do ticket

        Returns:
            True se deletado
        """
        return self.repository.delete(ticket_id)

    def get_stats(self) -> dict:
        """
        Retorna estatísticas dos tickets.

        Returns:
            Dicionário com estatísticas
        """
        return self.repository.get_stats()

    def simulate_ticket_result(self, ticket_id: str, results: List[str]) -> Ticket:
        """
        Simula resultado de um ticket (para testes manuais).

        Args:
            ticket_id: ID do ticket
            results: Lista de resultados para cada bet ("WON", "LOST")

        Returns:
            Ticket atualizado
        """
        ticket = self.repository.find_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} não encontrado")

        if len(results) != len(ticket.bets):
            raise ValueError(f"Número de resultados ({len(results)}) diferente de apostas ({len(ticket.bets)})")

        # Atualiza resultados das bets
        for bet, result in zip(ticket.bets, results):
            bet.result = result

        # Atualiza status do ticket
        ticket.update_status()

        # Salva no banco (status e bets)
        self.repository.update_status(ticket_id, ticket.status)
        self.repository.update_bet_results(ticket_id, ticket.bets)

        logger.info(f"🎲 Ticket {ticket_id} simulado: {ticket.status.value}")

        return ticket

    def simulate_ticket_with_api(self, ticket_id: str) -> Ticket:
        """
        Simula resultado de um ticket consultando a API Football.

        Consulta resultados das partidas via APIFootballService
        e determina automaticamente se cada aposta ganhou ou perdeu baseado no placar.

        Args:
            ticket_id: ID do ticket

        Returns:
            Ticket atualizado com resultados
        """
        ticket = self.repository.find_by_id(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} não encontrado")

        # Para cada aposta, consulta resultado da partida via API Football Service
        import asyncio

        async def process_bets():
            for bet in ticket.bets:
                # Consulta resultado da partida via API Football Service
                fixture_result = await self.api_service.get_fixture_result(bet.match_id)

                if not fixture_result:
                    logger.warning(f"⚠️ Não foi possível obter resultado da partida {bet.match_id}")
                    bet.result = "PENDING"
                    continue

                # Determina se a aposta ganhou/perdeu baseado no placar
                bet.result = BetResultService.determine_bet_result(
                    fixture_result,
                    bet.market.value,
                    bet.predicted_outcome
                )

                # Se partida terminou, salva o placar
                if fixture_result.get("fixture", {}).get("status", {}).get("short") == "FT":
                    home_goals = fixture_result.get("goals", {}).get("home")
                    away_goals = fixture_result.get("goals", {}).get("away")
                    if home_goals is not None and away_goals is not None:
                        bet.final_score = BetResultService.format_score(home_goals, away_goals)

        # Executa de forma assíncrona
        asyncio.run(process_bets())

        # Atualiza status do ticket baseado nos resultados das bets
        ticket.update_status()

        # Salva no banco
        self.repository.update_status(ticket_id, ticket.status)
        self.repository.update_bet_results(ticket_id, ticket.bets)

        won_bets = sum(1 for bet in ticket.bets if bet.result == "WON")
        total_bets = len(ticket.bets)

        logger.info(
            f"⚽ Ticket {ticket_id} simulado via API Football: "
            f"{ticket.status.value} ({won_bets}/{total_bets} certas)"
        )

        return ticket

