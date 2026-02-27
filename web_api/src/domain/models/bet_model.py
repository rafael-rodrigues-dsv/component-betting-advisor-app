"""
Bet Model - Representa uma aposta individual dentro de um bilhete
"""

from dataclasses import dataclass
from typing import Optional
from domain.enums.market_type_enum import MarketType


@dataclass
class Bet:
    """
    Aposta individual (parte de um Ticket).

    Representa uma previsão específica para um jogo dentro de um bilhete.
    """

    match_id: str
    """ID da partida"""

    home_team: str
    """Nome do time da casa"""

    away_team: str
    """Nome do time visitante"""

    league: str
    """Nome da liga/campeonato"""

    market: MarketType
    """Tipo de mercado (MATCH_WINNER, OVER_UNDER, etc)"""

    predicted_outcome: str
    """Resultado previsto (ex: "HOME", "OVER_2.5", "YES")"""

    odds: float
    """Odd da aposta"""

    confidence: float
    """Confiança na previsão (0.0 a 1.0)"""

    result: Optional[str] = None
    """Resultado real: "WON", "LOST", "PENDING", "VOID" """

    final_score: Optional[str] = None
    """Placar final do jogo (ex: "2 x 1")"""

    status: Optional[str] = None
    """Status da partida (ex: "Not Started", "First Half")"""

    status_short: Optional[str] = None
    """Status curto da partida (ex: "NS", "1H", "FT")"""

    elapsed: Optional[int] = None
    """Minuto do jogo (ex: 45, 67, 90)"""

    goals_home: Optional[int] = None
    """Gols do time da casa (placar parcial/final)"""

    goals_away: Optional[int] = None
    """Gols do time visitante (placar parcial/final)"""

    def is_won(self) -> bool:
        """Verifica se a aposta foi ganha"""
        return self.result == "WON"

    def is_lost(self) -> bool:
        """Verifica se a aposta foi perdida"""
        return self.result == "LOST"

    def is_pending(self) -> bool:
        """Verifica se a aposta está pendente"""
        return self.result is None or self.result == "PENDING"

