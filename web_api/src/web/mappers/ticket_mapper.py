"""
Mapper para Ticket - converte entre DTO e Domain
"""
from typing import Dict, Any, List
from datetime import datetime
from domain.models.ticket_model import Ticket
from domain.models.bet_model import Bet
from domain.enums.market_type_enum import MarketType
from domain.enums.ticket_status_enum import TicketStatus
from web.dtos.responses.ticket_response import (
    TicketResponse,
    TicketBetResponse,
    TicketStatusEnum
)


def map_market_dto_to_domain(market: str) -> MarketType:
    """
    Mapeia o valor do mercado do DTO para o enum do domínio.

    Args:
        market: Valor do mercado no DTO (ex: "BTTS", "MATCH_WINNER")

    Returns:
        MarketType correspondente
    """
    market_mapping = {
        "MATCH_WINNER": MarketType.MATCH_WINNER,
        "OVER_UNDER": MarketType.OVER_UNDER,
        "BTTS": MarketType.BOTH_TEAMS_SCORE,
        "BOTH_TEAMS_SCORE": MarketType.BOTH_TEAMS_SCORE,  # Aceita ambos
    }

    if market not in market_mapping:
        raise ValueError(f"Market type '{market}' não é válido. Valores aceitos: {list(market_mapping.keys())}")

    return market_mapping[market]


def map_market_domain_to_dto(market: MarketType) -> str:
    """
    Mapeia o enum do domínio para o valor usado no DTO.

    Args:
        market: MarketType do domínio

    Returns:
        String do mercado para o DTO
    """
    domain_to_dto = {
        MarketType.MATCH_WINNER: "MATCH_WINNER",
        MarketType.OVER_UNDER: "OVER_UNDER",
        MarketType.BOTH_TEAMS_SCORE: "BTTS",
    }

    return domain_to_dto.get(market, market.value)


def map_status_domain_to_dto(status: TicketStatus) -> TicketStatusEnum:
    """
    Mapeia status do domínio para DTO.

    Args:
        status: TicketStatus do domínio

    Returns:
        TicketStatusEnum do DTO
    """
    mapping = {
        TicketStatus.PENDING: TicketStatusEnum.PENDING,
        TicketStatus.WON: TicketStatusEnum.WON,
        TicketStatus.LOST: TicketStatusEnum.LOST,
    }
    return mapping.get(status, TicketStatusEnum.PENDING)


def map_bet_domain_to_response(bet: Bet) -> TicketBetResponse:
    """
    Converte Bet do domínio para TicketBetResponse.

    Args:
        bet: Bet do domínio

    Returns:
        TicketBetResponse
    """
    return TicketBetResponse(
        match_id=bet.match_id,
        home_team=bet.home_team,
        away_team=bet.away_team,
        league=bet.league,
        market=map_market_domain_to_dto(bet.market),
        predicted_outcome=bet.predicted_outcome,
        odds=bet.odds,
        confidence=bet.confidence,
        result=bet.result,
        final_score=bet.final_score,
        status=bet.status,
        status_short=bet.status_short
    )


def map_ticket_domain_to_response(ticket: Ticket) -> TicketResponse:
    """
    Converte Ticket do domínio para TicketResponse.

    Args:
        ticket: Ticket do domínio

    Returns:
        TicketResponse
    """
    return TicketResponse(
        id=ticket.id,
        name=ticket.name,
        bets=[map_bet_domain_to_response(bet) for bet in ticket.bets],
        stake=ticket.stake,
        combined_odds=ticket.combined_odds(),
        potential_return=ticket.potential_return(),
        bookmaker_id=ticket.bookmaker_id,
        status=map_status_domain_to_dto(ticket.status),
        created_at=ticket.created_at.isoformat() if isinstance(ticket.created_at, datetime) else ticket.created_at,
        profit=ticket.potential_profit()
    )

