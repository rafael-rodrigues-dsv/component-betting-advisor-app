"""
Ticket Repository - CRUD de tickets no SQLite.

Implementa operações de persistência para tickets e bets.
"""

from typing import List, Optional
from datetime import datetime
import logging

from infrastructure.database.connection import get_database
from domain.models.ticket_model import Ticket
from domain.models.bet_model import Bet
from domain.enums.ticket_status_enum import TicketStatus
from domain.enums.market_type_enum import MarketType

logger = logging.getLogger(__name__)

# Mapeamento de aliases de mercado armazenados no DB
_MARKET_ALIASES = {
    "BTTS": "BOTH_TEAMS_SCORE",
}


def _parse_market(value: str) -> MarketType:
    """Parse market string do banco, tratando aliases como BTTS → BOTH_TEAMS_SCORE."""
    normalized = _MARKET_ALIASES.get(value, value)
    return MarketType(normalized)


class TicketRepository:
    """
    Repositório de Tickets.

    Responsável por:
    - Salvar tickets no banco
    - Buscar tickets
    - Atualizar status
    - Deletar tickets
    """

    def __init__(self):
        self.db = get_database()

    def create(self, ticket: Ticket) -> str:
        """
        Cria um novo ticket no banco.

        Args:
            ticket: Ticket a ser salvo

        Returns:
            ID do ticket criado
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Insere ticket
            cursor.execute("""
                INSERT INTO tickets (id, name, stake, bookmaker_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                ticket.id,
                ticket.name,
                ticket.stake,
                ticket.bookmaker_id,
                ticket.status.value,
                ticket.created_at
            ))

            # Insere bets
            for bet in ticket.bets:
                cursor.execute("""
                    INSERT INTO bets (ticket_id, match_id, home_team, away_team, league,
                                    market, predicted_outcome, odds, confidence, result, final_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket.id,
                    bet.match_id,
                    bet.home_team,
                    bet.away_team,
                    bet.league,
                    bet.market.value,
                    bet.predicted_outcome,
                    bet.odds,
                    bet.confidence,
                    bet.result,
                    bet.final_score
                ))

            conn.commit()
            logger.info(f"✅ Ticket {ticket.id} criado com {len(ticket.bets)} apostas")

            return ticket.id

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao criar ticket: {e}")
            raise
        finally:
            conn.close()

    def find_by_id(self, ticket_id: str) -> Optional[Ticket]:
        """
        Busca ticket por ID.

        Args:
            ticket_id: ID do ticket

        Returns:
            Ticket ou None se não encontrado
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Busca ticket
            cursor.execute("""
                SELECT id, name, stake, bookmaker_id, status, created_at
                FROM tickets
                WHERE id = ?
            """, (ticket_id,))

            row = cursor.fetchone()
            if not row:
                return None

            # Busca bets do ticket
            cursor.execute("""
                SELECT match_id, home_team, away_team, league, market, predicted_outcome,
                       odds, confidence, result, final_score, status, status_short,
                       elapsed, goals_home, goals_away
                FROM bets
                WHERE ticket_id = ?
            """, (ticket_id,))

            bets = []
            for bet_row in cursor.fetchall():
                bets.append(Bet(
                    match_id=bet_row['match_id'],
                    home_team=bet_row['home_team'],
                    away_team=bet_row['away_team'],
                    league=bet_row['league'],
                    market=_parse_market(bet_row['market']),
                    predicted_outcome=bet_row['predicted_outcome'],
                    odds=bet_row['odds'],
                    confidence=bet_row['confidence'],
                    result=bet_row['result'],
                    final_score=bet_row['final_score'],
                    status=bet_row['status'],
                    status_short=bet_row['status_short'],
                    elapsed=bet_row['elapsed'],
                    goals_home=bet_row['goals_home'],
                    goals_away=bet_row['goals_away'],
                ))

            return Ticket(
                id=row['id'],
                name=row['name'],
                stake=row['stake'],
                bookmaker_id=row['bookmaker_id'],
                status=TicketStatus(row['status']),
                bets=bets,
                created_at=datetime.fromisoformat(row['created_at'])
            )

        finally:
            conn.close()

    def find_all(self, limit: int = 10, offset: int = 0) -> List[Ticket]:
        """
        Lista todos os tickets (paginado).

        Args:
            limit: Número máximo de tickets
            offset: Offset para paginação

        Returns:
            Lista de tickets
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, name, stake, bookmaker_id, status, created_at
                FROM tickets
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

            tickets = []
            for row in cursor.fetchall():
                ticket_id = row['id']

                # Busca bets
                cursor.execute("""
                    SELECT match_id, home_team, away_team, league, market, predicted_outcome,
                           odds, confidence, result, final_score, status, status_short,
                           elapsed, goals_home, goals_away
                    FROM bets
                    WHERE ticket_id = ?
                """, (ticket_id,))

                bets = []
                for bet_row in cursor.fetchall():
                    bets.append(Bet(
                        match_id=bet_row['match_id'],
                        home_team=bet_row['home_team'],
                        away_team=bet_row['away_team'],
                        league=bet_row['league'],
                        market=_parse_market(bet_row['market']),
                        predicted_outcome=bet_row['predicted_outcome'],
                        odds=bet_row['odds'],
                        confidence=bet_row['confidence'],
                        result=bet_row['result'],
                        final_score=bet_row['final_score'],
                        status=bet_row['status'],
                        status_short=bet_row['status_short'],
                        elapsed=bet_row['elapsed'],
                        goals_home=bet_row['goals_home'],
                        goals_away=bet_row['goals_away'],
                    ))

                tickets.append(Ticket(
                    id=row['id'],
                    name=row['name'],
                    stake=row['stake'],
                    bookmaker_id=row['bookmaker_id'],
                    status=TicketStatus(row['status']),
                    bets=bets,
                    created_at=datetime.fromisoformat(row['created_at'])
                ))

            return tickets

        finally:
            conn.close()

    def update_status(self, ticket_id: str, status: TicketStatus) -> bool:
        """
        Atualiza status de um ticket.

        Args:
            ticket_id: ID do ticket
            status: Novo status

        Returns:
            True se atualizado com sucesso
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE tickets
                SET status = ?
                WHERE id = ?
            """, (status.value, ticket_id))

            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"✅ Status do ticket {ticket_id} atualizado para {status.value}")
                return True

            return False

        finally:
            conn.close()

    def update_bet_results(self, ticket_id: str, bets: List[Bet]) -> bool:
        """
        Atualiza resultados das apostas de um ticket.

        Args:
            ticket_id: ID do ticket
            bets: Lista de apostas com resultados atualizados

        Returns:
            True se atualizado com sucesso
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            for bet in bets:
                cursor.execute("""
                    UPDATE bets
                    SET result = ?, final_score = ?, status = ?, status_short = ?,
                        elapsed = ?, goals_home = ?, goals_away = ?
                    WHERE ticket_id = ? AND match_id = ?
                """, (bet.result, bet.final_score, bet.status, bet.status_short,
                      bet.elapsed, bet.goals_home, bet.goals_away,
                      ticket_id, bet.match_id))

            conn.commit()
            logger.info(f"✅ Resultados das bets do ticket {ticket_id} atualizados")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Erro ao atualizar bets: {e}")
            return False

        finally:
            conn.close()

    def delete(self, ticket_id: str) -> bool:
        """
        Deleta um ticket (e suas bets em cascata).

        Args:
            ticket_id: ID do ticket

        Returns:
            True se deletado com sucesso
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            conn.commit()

            if cursor.rowcount > 0:
                logger.info(f"🗑️ Ticket {ticket_id} deletado")
                return True

            return False

        finally:
            conn.close()

    def count(self) -> int:
        """
        Conta total de tickets.

        Returns:
            Número total de tickets
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) FROM tickets")
            return cursor.fetchone()[0]
        finally:
            conn.close()

    def find_pending(self) -> List[Ticket]:
        """
        Busca todos os tickets pendentes.

        Returns:
            Lista de tickets pendentes
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, name, stake, bookmaker_id, status, created_at
                FROM tickets
                WHERE status = ?
                ORDER BY created_at DESC
            """, (TicketStatus.PENDING.value,))

            tickets = []
            for row in cursor.fetchall():
                ticket_id = row['id']

                # Busca bets
                cursor.execute("""
                    SELECT match_id, home_team, away_team, league, market, predicted_outcome,
                           odds, confidence, result, final_score, status, status_short,
                           elapsed, goals_home, goals_away
                    FROM bets
                    WHERE ticket_id = ?
                """, (ticket_id,))

                bets = []
                for bet_row in cursor.fetchall():
                    bets.append(Bet(
                        match_id=bet_row['match_id'],
                        home_team=bet_row['home_team'],
                        away_team=bet_row['away_team'],
                        league=bet_row['league'],
                        market=_parse_market(bet_row['market']),
                        predicted_outcome=bet_row['predicted_outcome'],
                        odds=bet_row['odds'],
                        confidence=bet_row['confidence'],
                        result=bet_row['result'],
                        final_score=bet_row['final_score'],
                        status=bet_row['status'],
                        status_short=bet_row['status_short'],
                        elapsed=bet_row['elapsed'],
                        goals_home=bet_row['goals_home'],
                        goals_away=bet_row['goals_away'],
                    ))

                tickets.append(Ticket(
                    id=row['id'],
                    name=row['name'],
                    stake=row['stake'],
                    bookmaker_id=row['bookmaker_id'],
                    status=TicketStatus(row['status']),
                    bets=bets,
                    created_at=datetime.fromisoformat(row['created_at'])
                ))

            return tickets

        finally:
            conn.close()

    def get_stats(self) -> dict:
        """
        Retorna estatísticas dos tickets.

        Returns:
            Dicionário com estatísticas
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Total por status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM tickets
                GROUP BY status
            """)

            stats_by_status = {row['status']: row['count'] for row in cursor.fetchall()}

            # Total investido
            cursor.execute("SELECT SUM(stake) FROM tickets")
            total_invested = cursor.fetchone()[0] or 0.0

            # Total de apostas
            cursor.execute("SELECT COUNT(*) FROM bets")
            total_bets = cursor.fetchone()[0] or 0

            return {
                "total_tickets": self.count(),
                "by_status": stats_by_status,
                "total_invested": total_invested,
                "total_bets": total_bets
            }

        finally:
            conn.close()

