"""
Match Controller - Lista de jogos (lê do CACHE)

Matches agora vêm com odds embutidas do cache bulk.
Ligas são dinâmicas (extraídas dos fixtures carregados).
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
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
from config.settings import settings

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

    Matches vêm com odds embutidas do cache bulk.
    Ligas são dinâmicas (extraídas dos fixtures carregados).

    Modos de uso:
    - Sem parâmetros: Retorna toda a semana (hoje até domingo)
    - date=YYYY-MM-DD: Retorna apenas essa data específica
    - date_from + date_to: Retorna range de datas
    """
    dates_to_fetch = []

    if date:
        try:
            match_date = datetime.strptime(date, "%Y-%m-%d").date()
            dates_to_fetch = [match_date]
        except ValueError:
            match_date = settings.today()
            dates_to_fetch = [match_date]
    elif date_from and date_to:
        try:
            start_date = datetime.strptime(date_from, "%Y-%m-%d").date()
            end_date = datetime.strptime(date_to, "%Y-%m-%d").date()

            current = start_date
            while current <= end_date:
                dates_to_fetch.append(current)
                current += timedelta(days=1)
        except ValueError:
            dates_to_fetch = _get_week_dates()
    else:
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
        date=dates_to_fetch[0].isoformat() if dates_to_fetch else settings.today().isoformat(),
        count=len(matches_response),
        matches=matches_response
    )


def _get_week_dates():
    """Retorna lista de datas desde hoje até o próximo domingo (mínimo 7 dias)."""
    today = settings.today()
    dates = [today]

    current = today
    days_added = 0
    max_days = 7

    while days_added < max_days or current.weekday() != 6:
        current += timedelta(days=1)
        dates.append(current)
        days_added += 1
        if days_added >= 14:
            break

    return dates


@router.get("/matches/live")
async def get_live_matches():
    """
    Retorna updates de jogos ao vivo (placar, status, minuto).

    Busca GET /fixtures?live=all na API-Football e filtra apenas
    fixtures que estão carregados no cache (período selecionado).

    Usado pelo frontend para polling a cada 5 segundos.
    """
    try:
        updates = await match_service.get_live_updates()
        return {
            "success": True,
            "count": len(updates),
            "updates": updates,
        }
    except Exception as e:
        logger.error(f"❌ Erro ao buscar jogos ao vivo: {e}")
        return {
            "success": False,
            "count": 0,
            "updates": [],
            "error": str(e)
        }


@router.get("/leagues", response_model=LeaguesListResponse)
async def get_leagues():
    """
    Lista campeonatos disponíveis.
    Retorna ligas DINÂMICAS extraídas dos fixtures carregados.
    """
    leagues_data = match_service.get_leagues()

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


@router.get("/matches/{fixture_id}/odds")
async def get_match_odds(fixture_id: str):
    """
    Busca odds de uma partida específica (cache ou API).
    Retorna apenas bookmakers suportadas.
    """
    try:
        odds = await match_service.get_odds_for_match(int(fixture_id))
        return {
            "success": True,
            "fixture_id": fixture_id,
            "odds": odds
        }
    except Exception as e:
        logger.error(f"❌ Erro ao buscar odds do fixture {fixture_id}: {e}")
        return {
            "success": False,
            "fixture_id": fixture_id,
            "odds": {},
            "error": str(e)
        }


@router.post("/matches/{fixture_id}/odds/refresh")
async def refresh_match_odds(fixture_id: str):
    """
    Força refresh das odds e status de uma partida.
    Deleta cache de odds, busca odds e status atualizados da API.
    """
    try:
        odds = await match_service.refresh_odds_for_match(int(fixture_id))
        live_status = await match_service.get_fixture_live_status(int(fixture_id))

        return {
            "success": True,
            "fixture_id": fixture_id,
            "odds": odds,
            "status": live_status.get("status", "Not Started"),
            "status_short": live_status.get("status_short", "NS"),
            "elapsed": live_status.get("elapsed"),
            "goals": live_status.get("goals", {"home": None, "away": None}),
            "message": "Odds e status atualizados com sucesso"
        }
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar odds do fixture {fixture_id}: {e}")
        return {
            "success": False,
            "fixture_id": fixture_id,
            "odds": {},
            "error": str(e)
        }
