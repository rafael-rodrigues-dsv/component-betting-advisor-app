"""
Ticket Model - Representa um bilhete de apostas (múltipla)
"""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime
from domain.models.bet_model import Bet
from domain.enums.ticket_status_enum import TicketStatus


@dataclass
class Ticket:
    """
    Bilhete de apostas (múltipla).

    Agrupa várias apostas (bets) em um único bilhete.
    Calcula odd combinada e retorno potencial.
    """

    id: str
    """ID único do bilhete"""

    name: str
    """Nome/descrição do bilhete"""

    bets: List[Bet]
    """Lista de apostas no bilhete"""

    stake: float
    """Valor apostado (em R$)"""

    bookmaker_id: str
    """Casa de apostas usada (bet365, betano, etc)"""

    status: TicketStatus
    """Status do bilhete"""

    created_at: datetime = field(default_factory=datetime.now)
    """Data de criação"""

    def combined_odds(self) -> float:
        """
        Calcula odd combinada (produto de todas as odds).

        Exemplo: 3 apostas com odds 2.0, 1.5, 1.8
        Odd combinada = 2.0 × 1.5 × 1.8 = 5.4
        """
        if not self.bets:
            return 1.0

        result = 1.0
        for bet in self.bets:
            result *= bet.odds

        return result

    def potential_return(self) -> float:
        """
        Calcula retorno potencial.

        Retorno = Stake × Odd Combinada

        Exemplo: R$ 10 × 5.4 = R$ 54
        """
        return self.stake * self.combined_odds()

    def potential_profit(self) -> float:
        """
        Calcula lucro potencial.

        Lucro = Retorno - Stake

        Exemplo: R$ 54 - R$ 10 = R$ 44
        """
        return self.potential_return() - self.stake

    def total_bets(self) -> int:
        """Número total de apostas no bilhete"""
        return len(self.bets)

    def won_bets(self) -> int:
        """Número de apostas ganhas"""
        return sum(1 for bet in self.bets if bet.is_won())

    def lost_bets(self) -> int:
        """Número de apostas perdidas"""
        return sum(1 for bet in self.bets if bet.is_lost())

    def pending_bets(self) -> int:
        """Número de apostas pendentes"""
        return sum(1 for bet in self.bets if bet.is_pending())

    def average_confidence(self) -> float:
        """Confiança média das apostas"""
        if not self.bets:
            return 0.0
        return sum(bet.confidence for bet in self.bets) / len(self.bets)

    def update_status(self) -> TicketStatus:
        """
        Atualiza status do bilhete baseado nas apostas.

        Regras:
        - Se pelo menos 1 perdeu → LOST
        - Se todas ganharam → WON
        - Se ainda tem pendentes → PENDING
        """
        if self.lost_bets() > 0:
            self.status = TicketStatus.LOST
        elif self.pending_bets() > 0:
            self.status = TicketStatus.PENDING
        elif self.won_bets() == self.total_bets():
            self.status = TicketStatus.WON

        return self.status

