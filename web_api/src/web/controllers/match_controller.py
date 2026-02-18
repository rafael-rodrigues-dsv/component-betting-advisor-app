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
    date: Optional[str] = Query(None, description="Data específica no formato YYYY-MM-DD"),
    date_from: Optional[str] = Query(None, description="Data inicial do range (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Data final do range (YYYY-MM-DD)"),
    league_id: Optional[str] = Query(None, description="Filtrar por ID da liga")
):
    """
    Lista jogos disponíveis para análise.

    Lê do cache preload_service preencheu no startup.

    Modos de uso:
    - Sem parâmetros: Retorna toda a semana (hoje até domingo)
    - date=YYYY-MM-DD: Retorna apenas essa data específica
    - date_from + date_to: Retorna range de datas
    """
    # Determina quais datas buscar
    dates_to_fetch = []

    if date:
        # Modo 1: Data específica
        try:
            match_date = datetime.strptime(date, "%Y-%m-%d").date()
            dates_to_fetch = [match_date]
        except ValueError:
            match_date = date_type.today()
            dates_to_fetch = [match_date]
    elif date_from and date_to:
        # Modo 2: Range de datas
        try:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

            current = start_date
            while current <= end_date:
                dates_to_fetch.append(current)
                current += timedelta(days=1)
        except ValueError:
            # Fallback para semana toda
            dates_to_fetch = _get_week_dates()
    else:
        # Modo 3: Semana toda (padrão)
        dates_to_fetch = _get_week_dates()

    # Busca matches para todas as datas
    all_matches = []

    for fetch_date in dates_to_fetch:
        if league_id:
            try:
                league_id_int = int(league_id)
                matches_data = match_service.get_matches_by_league_and_date(league_id_int, fetch_date)
            except ValueError:
                matches_data = match_service.get_all_matches_by_date(fetch_date)
        else:
            matches_data = match_service.get_all_matches_by_date(fetch_date)

        all_matches.extend(matches_data)

    logger.info(f"📊 GET /matches: {len(all_matches)} jogos retornados ({len(dates_to_fetch)} datas, league={league_id})")

    # Mapeia para DTOs
    matches_response = MatchMapper.to_matches_list(all_matches)

    return MatchesListResponse(
        success=True,
        date=dates_to_fetch[0].isoformat() if dates_to_fetch else date_type.today().isoformat(),
        count=len(matches_response),
        matches=matches_response
    )


def _get_week_dates():
    """
    Retorna lista de datas desde hoje até o próximo domingo (mínimo 7 dias).
    """
    today = date_type.today()
    dates = [today]

    current = today
    days_added = 0
    max_days = 7

    while days_added < max_days or current.weekday() != 6:  # 6 = Domingo
        current += timedelta(days=1)
        dates.append(current)
        days_added += 1

        if days_added >= 14:  # Limite de segurança
            break

    return dates


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



