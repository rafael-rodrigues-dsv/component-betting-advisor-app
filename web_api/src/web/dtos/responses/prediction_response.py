"""
DTOs de Response para Prediction (Previsões)
"""
from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class MarketEnum(str, Enum):
    """Mercados de apostas disponíveis"""
    MATCH_WINNER = "MATCH_WINNER"  # 1X2
    OVER_UNDER = "OVER_UNDER"  # Mais/Menos 2.5 gols
    BTTS = "BTTS"  # Ambos marcam


class RecommendationEnum(str, Enum):
    """Nível de recomendação da aposta"""
    STRONG_BET = "STRONG_BET"
    RECOMMENDED = "RECOMMENDED"
    CONSIDER = "CONSIDER"
    AVOID = "AVOID"


class MarketPredictionResponse(BaseModel):
    """Previsão para um mercado específico"""
    market: MarketEnum
    predicted_outcome: str = Field(..., description="Resultado previsto (ex: 'HOME', 'OVER', 'YES')")
    confidence: float = Field(..., ge=0, le=1, description="Confiança da previsão (0-1)")
    odds: float = Field(..., description="Odd do mercado")
    expected_value: float = Field(..., description="Valor esperado (EV) em decimal")
    recommendation: RecommendationEnum

    class Config:
        json_schema_extra = {
            "example": {
                "market": "MATCH_WINNER",
                "predicted_outcome": "HOME",
                "confidence": 0.72,
                "odds": 2.10,
                "expected_value": 0.12,
                "recommendation": "RECOMMENDED"
            }
        }


class PredictionResponse(BaseModel):
    """Previsão completa de uma partida"""
    id: str
    match_id: str
    home_team: str
    away_team: str
    league: str
    date: str
    predictions: List[MarketPredictionResponse]
    strategy_used: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "pred-uuid",
                "match_id": "match-uuid",
                "home_team": "Flamengo",
                "away_team": "Palmeiras",
                "league": "Brasileirão Série A",
                "date": "2026-02-16T19:00:00Z",
                "predictions": [
                    {
                        "market": "MATCH_WINNER",
                        "predicted_outcome": "HOME",
                        "confidence": 0.72,
                        "odds": 2.10,
                        "expected_value": 0.12,
                        "recommendation": "RECOMMENDED"
                    },
                    {
                        "market": "OVER_UNDER",
                        "predicted_outcome": "OVER",
                        "confidence": 0.68,
                        "odds": 1.85,
                        "expected_value": 0.08,
                        "recommendation": "CONSIDER"
                    }
                ],
                "strategy_used": "BALANCED"
            }
        }


class AnalyzePredictionsResponse(BaseModel):
    """Response da análise de múltiplas partidas"""
    success: bool = True
    count: int
    strategy: str
    predictions: List[PredictionResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "count": 3,
                "strategy": "BALANCED",
                "predictions": []
            }
        }


class PredictionDetailResponse(BaseModel):
    """Detalhes de uma previsão específica"""
    success: bool = True
    prediction: PredictionResponse

