"""
DTOs de Request para Ticket (Bilhetes)
"""
from pydantic import BaseModel, Field
from typing import List


class TicketBetRequest(BaseModel):
    """Aposta individual para incluir no bilhete"""
    match_id: str
    home_team: str
    away_team: str
    league: str
    market: str = Field(..., description="Mercado da aposta (MATCH_WINNER, OVER_UNDER, BTTS)")
    predicted_outcome: str = Field(..., description="Resultado previsto")
    odds: float = Field(..., gt=1.0, description="Odd da aposta")
    confidence: float = Field(..., ge=0, le=1, description="Confiança da previsão")

    class Config:
        json_schema_extra = {
            "example": {
                "match_id": "match-uuid",
                "home_team": "Flamengo",
                "away_team": "Palmeiras",
                "league": "Brasileirão Série A",
                "market": "MATCH_WINNER",
                "predicted_outcome": "HOME",
                "odds": 2.10,
                "confidence": 0.72
            }
        }


class CreateTicketRequest(BaseModel):
    """Request para criar um novo bilhete"""
    name: str = Field(..., min_length=3, max_length=100, description="Nome do bilhete")
    bets: List[TicketBetRequest] = Field(..., min_items=1, description="Lista de apostas do bilhete")
    stake: float = Field(..., gt=0, description="Valor apostado em reais")
    bookmaker_id: str = Field(default="bet365", description="ID da casa de apostas")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Rodada 5 - Brasileirão",
                "bets": [
                    {
                        "match_id": "match-uuid-1",
                        "home_team": "Flamengo",
                        "away_team": "Palmeiras",
                        "league": "Brasileirão Série A",
                        "market": "MATCH_WINNER",
                        "predicted_outcome": "HOME",
                        "odds": 2.10,
                        "confidence": 0.72
                    },
                    {
                        "match_id": "match-uuid-2",
                        "home_team": "Corinthians",
                        "away_team": "São Paulo",
                        "league": "Brasileirão Série A",
                        "market": "OVER_UNDER",
                        "predicted_outcome": "OVER",
                        "odds": 1.85,
                        "confidence": 0.68
                    }
                ],
                "stake": 50.00,
                "bookmaker_id": "bet365"
            }
        }


class SimulateTicketRequest(BaseModel):
    """Request para simular resultado de um bilhete"""
    results: List[str] = Field(..., description="Lista de resultados para cada aposta ('WON', 'LOST')")

    class Config:
        json_schema_extra = {
            "example": {
                "results": ["WON", "LOST", "WON"]
            }
        }

