"""
Ticket Controller - Gerenciamento de bilhetes (MOCK)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
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


def simulate_ticket_result(ticket_id: str):
    """Webhook mocado - simula resultado após 5 segundos"""
    import time
    time.sleep(5)

    ticket = TICKETS_DB.get(ticket_id)
    if not ticket or ticket.status != TicketStatusEnum.PENDING:
        return

    print(f"[WEBHOOK] Processando resultado do bilhete: {ticket_id}")

    # Simula cada aposta individualmente baseado na confiança
    all_won = True

    for bet in ticket.bets:
        bet_won = random.random() < (bet.confidence * 0.85)
        bet.result = "GANHOU" if bet_won else "PERDEU"

        # Gera placar final do jogo
        home_goals = random.randint(0, 4)
        away_goals = random.randint(0, 4)
        bet.final_score = f"{home_goals} x {away_goals}"

        if not bet_won:
            all_won = False

    # Bilhete só ganha se TODAS as apostas ganharem
    ticket.status = TicketStatusEnum.WON if all_won else TicketStatusEnum.LOST
    ticket.profit = round(ticket.potential_return - ticket.stake, 2) if all_won else -ticket.stake

    TICKETS_DB[ticket_id] = ticket

    result_text = "GANHOU! 🎉" if all_won else "PERDEU 😔"
    print(f"[WEBHOOK] Bilhete {ticket_id}: {result_text}")


@router.post("/tickets")
async def create_ticket(request: CreateTicketRequest, background_tasks: BackgroundTasks):
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
            result=None,
            final_score=None
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

    # Agenda webhook mocado para simular resultado em 5 segundos
    background_tasks.add_task(simulate_ticket_result, ticket_id)

    print(f"[DEBUG] Bilhete criado: {ticket_id} - Resultado será processado em 5s")

    return {
        "success": True,
        "message": "Bilhete criado com sucesso! Resultado em 5 segundos...",
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


@router.get("/tickets/stats/dashboard")
async def get_dashboard_stats():
    """Retorna estatísticas para o dashboard"""
    all_tickets = list(TICKETS_DB.values())

    total_tickets = len(all_tickets)
    won_tickets = len([t for t in all_tickets if t.status == TicketStatusEnum.WON])
    lost_tickets = len([t for t in all_tickets if t.status == TicketStatusEnum.LOST])
    pending_tickets = len([t for t in all_tickets if t.status == TicketStatusEnum.PENDING])

    # Taxa de sucesso (apenas bilhetes finalizados)
    finalized_tickets = won_tickets + lost_tickets
    success_rate = round((won_tickets / finalized_tickets * 100), 1) if finalized_tickets > 0 else 0

    # Total apostado e ganho
    total_staked = round(sum(t.stake for t in all_tickets), 2)
    total_profit = round(sum(t.profit for t in all_tickets if t.profit is not None), 2)

    return {
        "success": True,
        "stats": {
            "total_tickets": total_tickets,
            "won_tickets": won_tickets,
            "lost_tickets": lost_tickets,
            "pending_tickets": pending_tickets,
            "success_rate": success_rate,
            "total_staked": total_staked,
            "total_profit": total_profit
        }
    }


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

    # Simula cada aposta individualmente baseado na confiança
    all_won = True
    lost_bets = []

    for bet in ticket.bets:
        # Cada aposta tem chance de ganhar baseada na sua confiança
        bet_won = random.random() < (bet.confidence * 0.85)
        bet.result = "GANHOU" if bet_won else "PERDEU"

        # Gera placar final do jogo
        home_goals = random.randint(0, 4)
        away_goals = random.randint(0, 4)
        bet.final_score = f"{home_goals} x {away_goals}"

        if not bet_won:
            all_won = False
            lost_bets.append(f"{bet.home_team} vs {bet.away_team}")

    # Bilhete só ganha se TODAS as apostas ganharem
    ticket.status = TicketStatusEnum.WON if all_won else TicketStatusEnum.LOST
    ticket.profit = round(ticket.potential_return - ticket.stake, 2) if all_won else -ticket.stake

    TICKETS_DB[ticket_id] = ticket

    if all_won:
        message = "GANHOU! 🎉 Todas as apostas deram green!"
    else:
        message = f"Perdeu 😔 - Não deu green: {', '.join(lost_bets)}"

    return {
        "success": True,
        "message": message,
        "ticket": ticket.model_dump()
    }
