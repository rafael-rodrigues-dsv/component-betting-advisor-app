"""
Match Controller - Lista de jogos (lê do CACHE)
"""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, date as date_type, timedelta
import logging

from application.services.match_application_service import MatchService
from web.dtos.responses.match_response import (
    MatchesListResponse,
    LeaguesListResponse,
    BookmakersListResponse,
    LeagueResponse,
    BookmakerResponse
)
from web.mappers.match_mapper import MatchMapper

router = APIRouter()
logger = logging.getLogger(__name__)

# Instância do serviço
match_service = MatchService()


@router.get("/matches", response_model=MatchesListResponse)
async def get_matches(
    date: Optional[str] = Query(None, description="Data no formato YYYY-MM-DD"),
    league_id: Optional[str] = Query(None, description="Filtrar por ID da liga")
):
    """
    Lista jogos disponíveis para análise.

    Lê do cache preload_service preencheu no startup.
    """
    # Usa data de hoje se não especificada
    if not date:
        match_date = date_type.today()
    else:
        try:
            match_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            match_date = date_type.today()

    # Busca matches do cache
    if league_id:
        try:
            league_id_int = int(league_id)
            matches_data = match_service.get_matches_by_league_and_date(league_id_int, match_date)
        except ValueError:
            matches_data = match_service.get_all_matches_by_date(match_date)
    else:
        matches_data = match_service.get_all_matches_by_date(match_date)

    logger.info(f"📊 GET /matches: {len(matches_data)} jogos retornados (date={match_date}, league={league_id})")

    # Mapeia para DTOs
    matches_response = MatchMapper.to_matches_list(matches_data)

    return MatchesListResponse(
        success=True,
        date=match_date.isoformat(),
        count=len(matches_response),
        matches=matches_response
    )


@router.get("/leagues", response_model=LeaguesListResponse)
async def get_leagues():
    """Lista campeonatos disponíveis"""
    leagues_data = match_service.get_leagues()

    # Mapeia para DTOs
    leagues_response = [
        LeagueResponse(
            id=league["id"],
            name=league["name"],
            country=league["country"],
            logo=league["logo"],
            type=league["type"]
        )
        for league in leagues_data
    ]

    return LeaguesListResponse(
        success=True,
        count=len(leagues_response),
        leagues=leagues_response
    )


@router.get("/bookmakers", response_model=BookmakersListResponse)
async def get_bookmakers():
    """Lista casas de apostas disponíveis"""
    bookmakers_data = match_service.get_bookmakers()

    # Mapeia para DTOs
    bookmakers_response = [
        BookmakerResponse(
            id=bookmaker["id"],
            name=bookmaker["name"],
            logo=bookmaker["logo"]
        )
        for bookmaker in bookmakers_data
    ]

    return BookmakersListResponse(
        success=True,
        count=len(bookmakers_response),
        bookmakers=bookmakers_response
    )



