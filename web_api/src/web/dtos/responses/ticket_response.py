"""
DTOs de Response para Ticket (Bilhetes)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class TicketStatusEnum(str, Enum):
    """Status do bilhete"""
    PENDING = "PENDENTE"
    WON = "GANHOU"
    LOST = "PERDEU"


class TicketBetResponse(BaseModel):
    """Aposta individual do bilhete"""
    match_id: str
    home_team: str
    away_team: str
    league: str
    market: str
    predicted_outcome: str
    odds: float
    confidence: float
    result: Optional[str] = Field(None, description="Resultado da aposta: 'GANHOU', 'PERDEU' ou None se pendente")
    final_score: Optional[str] = Field(None, description="Placar final do jogo (ex: '2 x 1')")
    status: Optional[str] = Field(None, description="Status da partida (ex: 'Not Started')")
    status_short: Optional[str] = Field(None, description="Status curto da partida (ex: 'NS', '1H', 'FT')")


class TicketResponse(BaseModel):
    """Bilhete completo"""
    id: str
    name: str
    bets: List[TicketBetResponse]
    stake: float
    combined_odds: float
    potential_return: float
    bookmaker_id: str
    status: TicketStatusEnum
    created_at: str
    profit: Optional[float] = Field(None, description="Lucro/Prejuízo após resultado")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "ticket-uuid",
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
                        "confidence": 0.72,
                        "result": None
                    }
                ],
                "stake": 50.00,
                "combined_odds": 3.88,
                "potential_return": 194.00,
                "bookmaker_id": "bet365",
                "status": "PENDENTE",
                "created_at": "2026-02-16T18:30:00Z",
                "profit": None
            }
        }


class CreateTicketResponse(BaseModel):
    """Response da criação de bilhete"""
    success: bool = True
    message: str = "Bilhete criado com sucesso"
    ticket: TicketResponse


class TicketsListResponse(BaseModel):
    """Lista de bilhetes"""
    success: bool = True
    count: int
    tickets: List[TicketResponse]


class TicketDetailResponse(BaseModel):
    """Detalhes de um bilhete específico"""
    success: bool = True
    ticket: TicketResponse


class SimulateTicketResponse(BaseModel):
    """Response da simulação de resultado"""
    success: bool = True
    message: str
    ticket: TicketResponse

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Resultado simulado: GANHOU! 🎉",
                "ticket": {
                    "id": "ticket-uuid",
                    "name": "Rodada 5",
                    "status": "GANHOU",
                    "stake": 50.00,
                    "potential_return": 194.00,
                    "profit": 144.00
                }
            }
        }


class DeleteTicketResponse(BaseModel):
    """Response da exclusão de bilhete"""
    success: bool = True
    message: str = "Bilhete excluído com sucesso"

