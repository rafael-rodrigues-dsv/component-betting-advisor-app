"""
DTOs de Request para Prediction (Previsões)
"""
from pydantic import BaseModel, Field
from typing import List
from enum import Enum


class StrategyEnum(str, Enum):
    """Estratégias de análise disponíveis"""
    BALANCED = "BALANCED"
    CONSERVATIVE = "CONSERVATIVE"
    VALUE_BET = "VALUE_BET"
    AGGRESSIVE = "AGGRESSIVE"


class AnalyzeMatchesRequest(BaseModel):
    """Request para analisar partidas"""
    match_ids: List[str] = Field(..., min_items=1, description="Lista de IDs das partidas para analisar")
    strategy: StrategyEnum = Field(
        default=StrategyEnum.BALANCED,
        description="Estratégia de análise: BALANCED, CONSERVATIVE, VALUE_BET, AGGRESSIVE"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "match_ids": [
                    "uuid-match-1",
                    "uuid-match-2",
                    "uuid-match-3"
                ],
                "strategy": "BALANCED"
            }
        }

