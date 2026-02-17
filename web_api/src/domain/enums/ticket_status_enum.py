"""
Ticket Status Enum - Status de um bilhete
"""

from enum import Enum


class TicketStatus(Enum):
    """Status de um bilhete de apostas"""

    PENDING = "PENDING"
    """Bilhete pendente (jogos não finalizados)"""

    WON = "WON"
    """Bilhete vencedor (todas as apostas corretas)"""

    LOST = "LOST"
    """Bilhete perdido (pelo menos uma aposta errada)"""

    PARTIALLY_WON = "PARTIALLY_WON"
    """Bilhete parcialmente ganho (algumas apostas corretas)"""

