"""
Market Type Enum - Tipos de mercados de apostas
"""

from enum import Enum


class MarketType(Enum):
    """Tipos de mercados de apostas disponíveis"""

    MATCH_WINNER = "MATCH_WINNER"
    """Resultado do jogo (1X2): Casa, Empate, Fora"""

    OVER_UNDER = "OVER_UNDER"
    """Total de gols (Over/Under 2.5)"""

    BOTH_TEAMS_SCORE = "BOTH_TEAMS_SCORE"
    """Ambos os times marcam (BTTS)"""

    DOUBLE_CHANCE = "DOUBLE_CHANCE"
    """Chance dupla (1X, 12, X2)"""

    CORRECT_SCORE = "CORRECT_SCORE"
    """Placar exato"""

