"""
Ticket Controller - Gerenciamento de bilhetes (MOCK)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Optional
from datetime import datetime
import random
import uuid

from web.dtos.requests.ticket_request import CreateTicketRequest, SimulateTicketRequest
from web.dtos.responses.ticket_response import (
    CreateTicketResponse,
    TicketsListResponse,
    TicketDetailResponse,
    SimulateTicketResponse,
    DeleteTicketResponse,
    TicketResponse,
    TicketBetResponse,
    TicketStatusEnum
)

router = APIRouter()

# Mock DB
TICKETS_DB: Dict[str, TicketResponse] = {}


@router.post("/tickets")
async def create_ticket(request: CreateTicketRequest):
    """Cria bilhete"""
    print(f"[DEBUG] Recebido request para criar bilhete: {request.name}")
    print(f"[DEBUG] Apostas: {len(request.bets)}, Stake: {request.stake}")

    if not request.bets:
        raise HTTPException(400, "Bilhete precisa ter apostas")
    if request.stake <= 0:
        raise HTTPException(400, "Stake deve ser maior que zero")

    combined_odds = 1.0
    for bet in request.bets:
        combined_odds *= bet.odds

    ticket_id = str(uuid.uuid4())

    bets_response = [
        TicketBetResponse(
            match_id=bet.match_id,
            home_team=bet.home_team,
            away_team=bet.away_team,
            league=bet.league,
            market=bet.market,
            predicted_outcome=bet.predicted_outcome,
            odds=bet.odds,
            confidence=bet.confidence,
            result=None
        )
        for bet in request.bets
    ]

    ticket = TicketResponse(
        id=ticket_id,
        name=request.name,
        stake=request.stake,
        combined_odds=round(combined_odds, 2),
        potential_return=round(request.stake * combined_odds, 2),
        bookmaker_id=request.bookmaker_id,
        status=TicketStatusEnum.PENDING,
        bets=bets_response,
        created_at=datetime.now().isoformat()
    )

    TICKETS_DB[ticket_id] = ticket

    print(f"[DEBUG] Bilhete criado: {ticket_id}")

    return {
        "success": True,
        "message": "Bilhete criado com sucesso",
        "ticket": ticket.model_dump()
    }


@router.get("/tickets")
async def get_tickets(status: Optional[str] = None, limit: int = 20):
    """Lista bilhetes"""
    tickets = list(TICKETS_DB.values())

    if status:
        tickets = [t for t in tickets if t.status == status]

    tickets = sorted(tickets, key=lambda x: x.created_at, reverse=True)[:limit]

    return {
        "success": True,
        "count": len(tickets),
        "stats": {
            "total_stake": round(sum(t.stake for t in tickets), 2),
            "total_potential": round(sum(t.potential_return for t in tickets), 2),
            "pending": len([t for t in tickets if t.status == TicketStatusEnum.PENDING]),
            "won": len([t for t in tickets if t.status == TicketStatusEnum.WON]),
            "lost": len([t for t in tickets if t.status == TicketStatusEnum.LOST]),
        },
        "tickets": [t.model_dump() for t in tickets]
    }


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Detalhes do bilhete"""
    ticket = TICKETS_DB.get(ticket_id)
    if not ticket:
        raise HTTPException(404, "Bilhete não encontrado")
    return {"success": True, "ticket": ticket.model_dump()}


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
    if ticket.status != TicketStatusEnum.PENDING:
        raise HTTPException(400, "Bilhete já finalizado")

    # Calcula probabilidade média de sucesso
    avg_conf = sum(b.confidence for b in ticket.bets) / len(ticket.bets)
    won = random.random() < (avg_conf * 0.9)

    # Atualiza o ticket
    ticket.status = TicketStatusEnum.WON if won else TicketStatusEnum.LOST
    ticket.profit = round(ticket.potential_return - ticket.stake, 2) if won else -ticket.stake

    # Atualiza resultado de cada aposta
    for bet in ticket.bets:
        bet.result = "WON" if won else "LOST"

    TICKETS_DB[ticket_id] = ticket

    return {
        "success": True,
        "message": f"Resultado simulado: {'GANHOU! 🎉' if won else 'Perdeu 😔'}",
        "ticket": ticket.model_dump()
    }

