"""
Ticket Updater Service - Atualiza bilhetes com resultados das partidas.

Responsável por:
- Buscar bilhetes pendentes
- Consultar resultados das partidas
- Atualizar status de cada aposta
- Calcular status final do bilhete
"""

from typing import Dict, Any
import logging

from domain.models.ticket_model import Ticket
from domain.models.bet_model import Bet
from domain.enums.ticket_status_enum import TicketStatus
from domain.enums.market_type_enum import MarketType
from infrastructure.database.repositories.ticket_repository import TicketRepository
from infrastructure.external.api_football.service import APIFootballService

logger = logging.getLogger(__name__)


class TicketUpdaterService:
    """
    Serviço de atualização de bilhetes.

    Verifica resultados das partidas e atualiza status dos bilhetes.
    """

    def __init__(self):
        self.repository = TicketRepository()
        self.api_service = APIFootballService()
        logger.info("🔄 TicketUpdaterService inicializado")

    async def update_pending_tickets(self) -> Dict[str, Any]:
        """
        Atualiza todos os bilhetes pendentes.

        Returns:
            Estatísticas da atualização
        """
        logger.info("🔍 Buscando bilhetes pendentes...")

        # Busca apenas tickets pendentes
        pending_tickets = self.repository.find_pending()

        logger.info(f"📋 {len(pending_tickets)} bilhetes pendentes encontrados")

        updated_count = 0
        won_count = 0
        lost_count = 0

        for ticket in pending_tickets:
            try:
                if await self._update_ticket_result(ticket):
                    updated_count += 1
                    if ticket.status == TicketStatus.WON:
                        won_count += 1
                    elif ticket.status == TicketStatus.LOST:
                        lost_count += 1
            except Exception as e:
                logger.error(f"❌ Erro ao atualizar ticket {ticket.id}: {e}")

        logger.info(f"✅ Atualização concluída: {updated_count} bilhetes atualizados ({won_count} ganhos, {lost_count} perdidos)")

        return {
            "total_pending": len(pending_tickets),
            "updated": updated_count,
            "won": won_count,
            "lost": lost_count
        }

    async def update_ticket(self, ticket_id: str) -> bool:
        """
        Atualiza um bilhete específico.

        Args:
            ticket_id: ID do bilhete

        Returns:
            True se atualizado com sucesso
        """
        ticket = self.repository.find_by_id(ticket_id)
        if not ticket:
            logger.warning(f"⚠️ Ticket {ticket_id} não encontrado")
            return False

        if ticket.status != TicketStatus.PENDING:
            logger.warning(f"⚠️ Ticket {ticket_id} não está pendente (status: {ticket.status.value})")
            return False

        return await self._update_ticket_result(ticket)

    async def _update_ticket_result(self, ticket: Ticket) -> bool:
        """
        Atualiza resultado de um ticket baseado nos resultados das partidas.

        Args:
            ticket: Ticket a ser atualizado

        Returns:
            True se atualizado com sucesso
        """
        logger.info(f"🔄 Atualizando ticket {ticket.id} ({len(ticket.bets)} apostas)")

        all_finished = True
        all_won = True
        any_lost = False

        # Atualiza cada aposta
        for bet in ticket.bets:
            try:
                logger.info(f"   📍 Processando aposta: {bet.match_id} ({bet.home_team} vs {bet.away_team})")
                logger.info(f"      Market: {bet.market.value}, Predicted: {bet.predicted_outcome}, Odds: {bet.odds}")

                # Busca resultado da partida
                logger.info(f"   🔍 Chamando get_fixture_result({bet.match_id})...")
                match_result = await self.api_service.get_fixture_result(bet.match_id)

                logger.info(f"   📥 Resultado recebido: {match_result is not None}")
                if match_result:
                    logger.info(f"   📄 Conteúdo: {match_result}")

                if not match_result:
                    logger.warning(f"   ⏳ Partida {bet.match_id} ainda sem resultado (retornou None)")
                    all_finished = False
                    continue

                # Extrai dados do resultado
                fixture_data = match_result.get("fixture", {})
                status_data = fixture_data.get("status", {})
                status = status_data.get("short", "NS")

                logger.info(f"   📊 Status da partida: {status}")
                logger.info(f"   📊 Status completo: {status_data}")

                # Atualiza status da partida na aposta
                bet.status = status_data.get("long", status)
                bet.status_short = status

                # Só processa se a partida finalizou
                if status not in ["FT", "AET", "PEN"]:  # Full Time, After Extra Time, Penalties
                    logger.debug(f"   ⏳ Partida {bet.match_id} ainda não finalizou (status: {status})")
                    all_finished = False
                    continue

                # Extrai placar
                goals = match_result.get("goals", {})
                home_score = goals.get("home", 0)
                away_score = goals.get("away", 0)
                bet.final_score = f"{home_score} x {away_score}"

                # Verifica se a aposta foi ganha
                bet_won = self._check_bet_result(bet, home_score, away_score, match_result)

                if bet_won:
                    bet.result = "WON"
                    logger.info(f"✅ Aposta {bet.match_id} GANHOU ({bet.market.value}: {bet.predicted_outcome})")
                else:
                    bet.result = "LOST"
                    any_lost = True
                    all_won = False
                    logger.info(f"❌ Aposta {bet.match_id} PERDEU ({bet.market.value}: {bet.predicted_outcome})")

            except Exception as e:
                logger.error(f"❌ Erro ao processar aposta {bet.match_id}: {e}")
                all_finished = False

        # Se nem todas as partidas finalizaram, não atualiza status do ticket
        if not all_finished:
            logger.debug(f"⏳ Ticket {ticket.id} ainda tem partidas pendentes")
            return False

        # Define status final do ticket
        if all_won:
            ticket.status = TicketStatus.WON
            logger.info(f"🎉 Ticket {ticket.id} GANHOU! (Retorno: R$ {ticket.potential_return():.2f})")
        elif any_lost:
            ticket.status = TicketStatus.LOST
            logger.info(f"💔 Ticket {ticket.id} PERDEU")

        # Atualiza no banco
        self.repository.update_bet_results(ticket.id, ticket.bets)
        self.repository.update_status(ticket.id, ticket.status)

        return True

    def _check_bet_result(self, bet: Bet, home_score: int, away_score: int, match_result: Dict[str, Any]) -> bool:
        """
        Verifica se uma aposta foi ganha baseado no resultado da partida.

        Args:
            bet: Aposta a verificar
            home_score: Gols do time da casa
            away_score: Gols do time visitante
            match_result: Resultado completo da API

        Returns:
            True se a aposta foi ganha
        """
        market = bet.market
        outcome = bet.predicted_outcome

        # MATCH_WINNER
        if market == MarketType.MATCH_WINNER:
            if outcome == "HOME" and home_score > away_score:
                return True
            if outcome == "DRAW" and home_score == away_score:
                return True
            if outcome == "AWAY" and away_score > home_score:
                return True
            return False

        # OVER_UNDER (padrão 2.5 gols)
        elif market == MarketType.OVER_UNDER:
            total_goals = home_score + away_score
            if outcome == "OVER" and total_goals > 2.5:
                return True
            if outcome == "UNDER" and total_goals < 2.5:
                return True
            return False

        # BTTS (Both Teams To Score)
        elif market == MarketType.BOTH_TEAMS_SCORE:
            both_scored = home_score > 0 and away_score > 0
            if outcome == "YES" and both_scored:
                return True
            if outcome == "NO" and not both_scored:
                return True
            return False

        # Market desconhecido
        logger.warning(f"⚠️ Market desconhecido: {market}")
        return False

