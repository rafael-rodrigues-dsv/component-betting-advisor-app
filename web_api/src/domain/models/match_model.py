"""
Match Model - Representa uma partida de futebol
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

from domain.models.team_model import Team
from domain.models.league_model import League
from domain.models.odds_model import Odds
from domain.enums.match_status_enum import MatchStatus


@dataclass
class Venue:
    """Local da partida"""
    name: str
    """Nome do estádio"""

    city: Optional[str] = None
    """Cidade"""


@dataclass
class Match:
    """
    Partida de futebol completa.

    Entidade principal que agrega todas as informações
    de um jogo: times, liga, odds, status, etc.
    """

    id: str
    """ID único da partida"""

    date: datetime
    """Data e hora do jogo"""

    home_team: Team
    """Time da casa"""

    away_team: Team
    """Time visitante"""

    league: League
    """Liga/competição"""

    status: MatchStatus
    """Status da partida"""

    odds: Optional[Odds] = None
    """Odds do jogo (todas as casas)"""

    venue: Optional[Venue] = None
    """Local do jogo"""

    round: Optional[str] = None
    """Rodada/Round"""

    timestamp: Optional[str] = None
    """Data no formato YYYY-MM-DD"""

    def is_finished(self) -> bool:
        """Verifica se a partida já terminou"""
        return self.status == MatchStatus.FINISHED

    def is_live(self) -> bool:
        """Verifica se a partida está ao vivo"""
        return self.status == MatchStatus.LIVE

    def is_not_started(self) -> bool:
        """Verifica se a partida ainda não começou"""
        return self.status == MatchStatus.NOT_STARTED

    def has_odds(self) -> bool:
        """Verifica se tem odds disponíveis"""
        return self.odds is not None and len(self.odds.bookmakers) > 0

