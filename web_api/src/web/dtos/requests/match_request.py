"""
DTOs de Request para Match (Partidas)
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class MatchFilterRequest(BaseModel):
    """Filtros para buscar partidas"""
    date: Optional[str] = Field(None, description="Data no formato YYYY-MM-DD")
    league_id: Optional[str] = Field(None, description="ID da liga para filtrar")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-02-16",
                "league_id": "l1"
            }
        }

