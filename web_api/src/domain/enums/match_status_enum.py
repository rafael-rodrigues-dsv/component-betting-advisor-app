"""
Match Status Enum - Status de uma partida
"""

from enum import Enum


class MatchStatus(Enum):
    """Status de uma partida de futebol"""

    NOT_STARTED = "NOT_STARTED"
    """Partida ainda não começou"""

    LIVE = "LIVE"
    """Partida em andamento"""

    FINISHED = "FINISHED"
    """Partida finalizada"""

    POSTPONED = "POSTPONED"
    """Partida adiada"""

    CANCELLED = "CANCELLED"
    """Partida cancelada"""

    SUSPENDED = "SUSPENDED"
    """Partida suspensa"""

