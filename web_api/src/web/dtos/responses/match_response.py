"""
DTOs de Response para Match (Partidas)
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from .logo_dto import LogoDTO


class TeamResponse(BaseModel):
    """Time"""
    id: str
    name: str
    logo: LogoDTO
    country: str = "Brazil"


class LeagueResponse(BaseModel):
    """Liga/Campeonato"""
    id: str
    name: str
    country: str
    logo: str  # Mantém como string (emoji)
    type: str  # "league" ou "cup"


class BookmakerResponse(BaseModel):
    """Casa de apostas"""
    id: str
    name: str
    logo: str  # Mantém como string (emoji)


class VenueResponse(BaseModel):
    """Estádio/Local da partida"""
    name: str
    city: str


class RoundInfoResponse(BaseModel):
    """Informação da rodada/fase"""
    type: str  # "round" ou "phase"
    number: Optional[int] = None
    name: str


class OddsResponse(BaseModel):
    """Odds (cotações) da partida"""
    home: float = Field(..., description="Odd vitória mandante")
    draw: float = Field(..., description="Odd empate")
    away: float = Field(..., description="Odd vitória visitante")
    over_25: float = Field(..., description="Odd mais de 2.5 gols")
    under_25: float = Field(..., description="Odd menos de 2.5 gols")
    btts_yes: float = Field(..., description="Odd ambos marcam - Sim")
    btts_no: float = Field(..., description="Odd ambos marcam - Não")


class MatchResponse(BaseModel):
    """Partida completa"""
    id: str
    league: LeagueResponse
    home_team: TeamResponse
    away_team: TeamResponse
    date: str
    timestamp: str  # Data no formato YYYY-MM-DD
    status: str  # "NS" (Not Started), "LIVE", "FT" (Full Time)
    round: RoundInfoResponse
    venue: VenueResponse
    odds: Dict[str, OddsResponse]  # Dicionário com bookmaker como chave


class MatchesListResponse(BaseModel):
    """Lista de partidas"""
    success: bool = True
    date: str
    count: int
    matches: List[MatchResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "date": "2026-02-16",
                "count": 10,
                "matches": [
                    {
                        "id": "uuid-here",
                        "league": {
                            "id": "l1",
                            "name": "Brasileirão Série A",
                            "country": "Brazil",
                            "logo": "🇧🇷",
                            "type": "league"
                        },
                        "home_team": {
                            "id": "t1",
                            "name": "Flamengo",
                            "logo": "/escudos/flamengo.png",
                            "country": "Brazil"
                        },
                        "away_team": {
                            "id": "t2",
                            "name": "Palmeiras",
                            "logo": "/escudos/palmeiras.png",
                            "country": "Brazil"
                        },
                        "date": "2026-02-16T19:00:00Z",
                        "timestamp": "2026-02-16",
                        "status": "NS",
                        "round": {
                            "type": "round",
                            "number": 5,
                            "name": "Rodada 5"
                        },
                        "venue": {
                            "name": "Maracanã",
                            "city": "Rio de Janeiro"
                        },
                        "odds": {
                            "home": 2.10,
                            "draw": 3.20,
                            "away": 2.80,
                            "over_25": 1.85,
                            "under_25": 1.90,
                            "btts_yes": 1.75,
                            "btts_no": 1.95
                        }
                    }
                ]
            }
        }


class LeaguesListResponse(BaseModel):
    """Lista de ligas disponíveis"""
    success: bool = True
    count: int
    leagues: List[LeagueResponse]


class BookmakersListResponse(BaseModel):
    """Lista de casas de apostas"""
    success: bool = True
    count: int
    bookmakers: List[BookmakerResponse]

