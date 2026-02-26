"""
Ticket Controller - Gerenciamento de bilhetes
"""

from fastapi import APIRouter, HTTPException
import logging

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
from application.services.ticket_application_service import TicketApplicationService
from application.services.ticket_updater_service import TicketUpdaterService
from domain.enums.ticket_status_enum import TicketStatus
from web.mappers.ticket_mapper import map_ticket_domain_to_response

router = APIRouter()
logger = logging.getLogger(__name__)

# Instâncias dos serviços
ticket_service = TicketApplicationService()
updater_service = TicketUpdaterService()


@router.post("/tickets")
async def create_ticket(request: CreateTicketRequest) -> CreateTicketResponse:
    """
    Cria um novo bilhete de apostas.

    Salva no banco de dados SQLite.
    """
    try:
        # Validações
        if not request.bets:
            raise HTTPException(status_code=400, detail="Bilhete precisa ter apostas")
        if request.stake <= 0:
            raise HTTPException(status_code=400, detail="Stake deve ser maior que zero")

        # Converte bets do request para formato do service
        bets_data = [
            {
                'match_id': bet.match_id,
                'home_team': bet.home_team,
                'away_team': bet.away_team,
                'league': bet.league,
                'market': bet.market,
                'predicted_outcome': bet.predicted_outcome,
                'odds': bet.odds,
                'confidence': bet.confidence
            }
            for bet in request.bets
        ]

        # Cria ticket usando service
        ticket = ticket_service.create_ticket(
            name=request.name,
            bets_data=bets_data,
            stake=request.stake,
            bookmaker_id=request.bookmaker_id
        )

        # Converte para response usando mapper
        ticket_response = map_ticket_domain_to_response(ticket)

        logger.info(f"✅ Ticket criado: {ticket.id}")

        return {
            "success": True,
            "message": "Bilhete criado com sucesso!",
            "ticket": ticket_response.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao criar ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets")
async def list_tickets(limit: int = 10, offset: int = 0) -> TicketsListResponse:
    """Lista bilhetes (paginado)"""
    try:
        tickets = ticket_service.list_tickets(limit=limit, offset=offset)

        # Converte para response usando mapper
        tickets_response = [map_ticket_domain_to_response(ticket) for ticket in tickets]

        return {
            "success": True,
            "count": len(tickets_response),
            "tickets": tickets_response
        }

    except Exception as e:
        logger.error(f"❌ Erro ao listar tickets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str) -> TicketDetailResponse:
    """Busca detalhes de um bilhete"""
    try:
        ticket = ticket_service.get_ticket(ticket_id)

        if not ticket:
            raise HTTPException(status_code=404, detail="Bilhete não encontrado")

        # Converte para response usando mapper
        ticket_response = map_ticket_domain_to_response(ticket)

        return {
            "success": True,
            "ticket": ticket_response
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/{ticket_id}/simulate")
async def simulate_ticket(ticket_id: str, request: SimulateTicketRequest) -> SimulateTicketResponse:
    """Simula resultado de um bilhete manualmente (para testes)"""
    try:
        ticket = ticket_service.simulate_ticket_result(ticket_id, request.results)

        # Mapeia o status para mensagem amigável
        status_messages = {
            TicketStatus.WON: "GANHOU! 🎉",
            TicketStatus.LOST: "PERDEU 😢",
            TicketStatus.PENDING: "PENDENTE ⏳"
        }
        message = f"Resultado simulado: {status_messages.get(ticket.status, ticket.status.value)}"

        # Converte para response usando mapper
        ticket_response = map_ticket_domain_to_response(ticket)

        return {
            "success": True,
            "message": message,
            "ticket": ticket_response
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Erro ao simular ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/{ticket_id}/simulate-auto")
async def simulate_ticket_auto(ticket_id: str) -> SimulateTicketResponse:
    """
    Simula resultado de um bilhete automaticamente usando a API Football.

    Consulta os resultados reais das partidas e determina automaticamente
    se cada aposta ganhou ou perdeu.
    """
    try:
        ticket = ticket_service.simulate_ticket_with_api(ticket_id)

        # Mapeia o status para mensagem amigável
        status_messages = {
            TicketStatus.WON: "GANHOU! 🎉",
            TicketStatus.LOST: "PERDEU 😢",
            TicketStatus.PENDING: "PENDENTE ⏳"
        }
        message = f"Resultado simulado via API: {status_messages.get(ticket.status, ticket.status.value)}"

        # Converte para response usando mapper
        ticket_response = map_ticket_domain_to_response(ticket)

        return {
            "success": True,
            "message": message,
            "ticket": ticket_response
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Erro ao simular ticket automaticamente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: str) -> DeleteTicketResponse:
    """Deleta um bilhete"""
    try:
        deleted = ticket_service.delete_ticket(ticket_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Bilhete não encontrado")

        return {
            "success": True,
            "message": "Bilhete deletado com sucesso"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao deletar ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickets/stats/dashboard")
async def get_dashboard_stats():
    """Retorna estatísticas do dashboard"""
    try:
        stats = ticket_service.get_stats()

        total_tickets = stats.get("total_tickets", 0)
        won_tickets = stats.get("by_status", {}).get("WON", 0)
        lost_tickets = stats.get("by_status", {}).get("LOST", 0)
        pending_tickets = stats.get("by_status", {}).get("PENDING", 0)
        total_staked = stats.get("total_invested", 0.0)

        # Calcula success_rate (taxa de sucesso)
        success_rate = (won_tickets / total_tickets * 100) if total_tickets > 0 else 0.0

        # Calcula total_profit (lucro total)
        # TODO: Implementar cálculo real quando tivermos os valores de retorno
        total_profit = 0.0

        return {
            "success": True,
            "stats": {
                "total_tickets": total_tickets,
                "won_tickets": won_tickets,         # Frontend espera won_tickets
                "lost_tickets": lost_tickets,       # Frontend espera lost_tickets
                "pending_tickets": pending_tickets, # Frontend espera pending_tickets
                "success_rate": success_rate,       # Frontend espera success_rate
                "total_staked": total_staked,       # Frontend espera total_staked
                "total_profit": total_profit        # Frontend espera total_profit
            }
        }

    except Exception as e:
        logger.error(f"❌ Erro ao buscar stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/update-results")
async def update_tickets_results():
    """
    Atualiza resultados de todos os bilhetes pendentes.

    Consulta a API de futebol para obter resultados das partidas
    e atualiza status dos bilhetes automaticamente.
    """
    try:
        logger.info("🔄 Iniciando atualização de bilhetes pendentes...")

        stats = await updater_service.update_pending_tickets()

        return {
            "success": True,
            "message": f"Atualização concluída: {stats['updated']} bilhetes atualizados",
            "stats": stats
        }

    except Exception as e:
        logger.error(f"❌ Erro ao atualizar bilhetes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tickets/{ticket_id}/update-result")
async def update_ticket_result(ticket_id: str):
    """
    Atualiza resultado de um bilhete específico.

    Args:
        ticket_id: ID do bilhete
    """
    try:
        logger.info(f"🔄 Atualizando bilhete {ticket_id}...")

        updated = await updater_service.update_ticket(ticket_id)

        if not updated:
            raise HTTPException(status_code=404, detail="Bilhete não encontrado ou não está pendente")

        # Busca o bilhete atualizado
        ticket = ticket_service.get_ticket(ticket_id)
        ticket_response = map_ticket_domain_to_response(ticket)

        return {
            "success": True,
            "message": "Bilhete atualizado com sucesso",
            "ticket": ticket_response.model_dump()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar bilhete: {e}")
        raise HTTPException(status_code=500, detail=str(e))



