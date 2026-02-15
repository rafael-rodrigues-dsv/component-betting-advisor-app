"""
Ticket Controller - Gerenciamento de bilhetes (MOCK)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import uuid

router = APIRouter()

# Mock DB
TICKETS_DB = {}


class TicketBet(BaseModel):
    match_id: str
    home_team: str
    away_team: str
    market: str
    predicted_outcome: str
    odds: float
    confidence: float


class CreateTicketRequest(BaseModel):
    name: Optional[str] = None
    stake: float
    bets: List[TicketBet]


class UpdateTicketRequest(BaseModel):
    name: Optional[str] = None
    stake: Optional[float] = None


@router.post("/tickets")
async def create_ticket(request: CreateTicketRequest):
    """Cria bilhete"""
    if not request.bets:
        raise HTTPException(400, "Bilhete precisa ter apostas")
    if request.stake <= 0:
        raise HTTPException(400, "Stake deve ser maior que zero")

    combined_odds = 1.0
    for bet in request.bets:
        combined_odds *= bet.odds

    ticket_id = str(uuid.uuid4())
    ticket = {
        "id": ticket_id,
        "name": request.name or f"Bilhete {datetime.now().strftime('%d/%m %H:%M')}",
        "stake": request.stake,
        "combined_odds": round(combined_odds, 2),
        "potential_return": round(request.stake * combined_odds, 2),
        "status": "PENDING",
        "result": None,
        "bets": [b.model_dump() for b in request.bets],
        "created_at": datetime.now().isoformat()
    }

    TICKETS_DB[ticket_id] = ticket
    return {"success": True, "ticket": ticket}


@router.get("/tickets")
async def get_tickets(status: Optional[str] = None, limit: int = 20):
    """Lista bilhetes"""
    tickets = list(TICKETS_DB.values())

    if status:
        tickets = [t for t in tickets if t["status"] == status]

    tickets = sorted(tickets, key=lambda x: x["created_at"], reverse=True)[:limit]

    return {
        "success": True,
        "count": len(tickets),
        "stats": {
            "total_stake": round(sum(t["stake"] for t in tickets), 2),
            "total_potential": round(sum(t["potential_return"] for t in tickets), 2),
            "pending": len([t for t in tickets if t["status"] == "PENDING"]),
            "won": len([t for t in tickets if t["status"] == "WON"]),
            "lost": len([t for t in tickets if t["status"] == "LOST"]),
        },
        "tickets": tickets
    }


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Detalhes do bilhete"""
    ticket = TICKETS_DB.get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Bilhete não encontrado")
    return {"success": True, "ticket": ticket}


@router.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, request: UpdateTicketRequest):
    """Atualiza bilhete"""
    ticket = TICKETS_DB.get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Bilhete não encontrado")
    if ticket["status"] != "PENDING":
        raise HTTPException(400, "Bilhete já finalizado")

    if request.name:
        ticket["name"] = request.name
    if request.stake and request.stake > 0:
        ticket["stake"] = request.stake
        ticket["potential_return"] = round(request.stake * ticket["combined_odds"], 2)

    TICKETS_DB[ticket_id] = ticket
    return {"success": True, "ticket": ticket}


@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: str):
    """Remove bilhete"""
    if ticket_id not in TICKETS_DB:
        raise HTTPException(404, "Bilhete não encontrado")
    del TICKETS_DB[ticket_id]
    return {"success": True, "message": "Bilhete removido"}


@router.post("/tickets/{ticket_id}/simulate")
async def simulate_result(ticket_id: str):
    """Simula resultado (para testes)"""
    ticket = TICKETS_DB.get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Bilhete não encontrado")
    if ticket["status"] != "PENDING":
        raise HTTPException(400, "Bilhete já finalizado")

    avg_conf = sum(b["confidence"] for b in ticket["bets"]) / len(ticket["bets"])
    won = random.random() < (avg_conf * 0.9)

    ticket["status"] = "WON" if won else "LOST"
    ticket["result"] = "WIN" if won else "LOSS"
    ticket["profit"] = round(ticket["potential_return"] - ticket["stake"], 2) if won else -ticket["stake"]

    TICKETS_DB[ticket_id] = ticket
    return {"success": True, "ticket": ticket}

