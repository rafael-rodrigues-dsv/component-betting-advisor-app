"""
Preload Controller - Endpoints de pré-carregamento sob demanda.

Três endpoints:
- POST /preload/fetch?days=N → carrega fixtures (rápido, mostra jogos)
- POST /preload/odds?date=YYYY-MM-DD → carrega odds de 1 data (LEGACY)
- POST /preload/odds/league → carrega odds de uma liga sob demanda (equilibrado)
"""

from datetime import timedelta
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List
import logging

from application.services.preload_service import PreloadService
from web.mappers.preload_mapper import map_preload_status
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Instância do serviço
preload_service = PreloadService()


@router.get("/preload/status")
async def get_preload_status():
    """
    Retorna o status do pré-carregamento.
    """
    has_cache = await preload_service.has_todays_cache()
    return map_preload_status(cache_valid=has_cache)


@router.post("/preload/fetch")
async def fetch_preload(
    days: int = Query(7, description="Número de dias a carregar (3, 7 ou 14)")
):
    """
    FASE 1: Carrega APENAS fixtures (rápido, 1 request/dia).

    O frontend chama isso primeiro para mostrar os jogos na tela.
    Depois dispara POST /preload/odds para cada data em background.

    Returns:
        - leagues: ligas dinâmicas
        - dates: lista de datas carregadas (para o frontend usar no /preload/odds)
    """
    allowed_days = [1, 3, 7]
    if days not in allowed_days:
        return {"success": False, "message": f"Valor inválido. Use: {allowed_days}"}

    logger.info(f"📥 FASE 1 — Carregando fixtures: {days} dias")

    try:
        result = await preload_service.preload_fixtures(days=days)

        today = settings.today()
        date_from = today.isoformat()
        date_to = (today + timedelta(days=days - 1)).isoformat()

        logger.info(f"✅ Fixtures concluído: {date_from} até {date_to}")

        return {
            "success": True,
            "message": f"Fixtures carregados para {days} dias",
            "days": days,
            "date_from": date_from,
            "date_to": date_to,
            "total_fixtures": result["total_fixtures"],
            "leagues": result["leagues"],
            "dates": result["dates"],
            "from_cache": result.get("from_cache", False),
        }

    except Exception as e:
        logger.error(f"❌ Erro no carregamento de fixtures: {e}")
        return {"success": False, "message": f"Erro: {str(e)}"}


@router.post("/preload/odds")
async def fetch_odds_for_date(
    date: str = Query(..., description="Data no formato YYYY-MM-DD")
):
    """
    FASE 2: Carrega odds de UMA data (lento, paginado).

    O frontend chama isso para cada data em background, uma por vez.
    Ao concluir, o frontend busca GET /matches novamente para essa data.

    Returns:
        - total_odds: quantidade de fixtures com odds carregadas
        - from_cache: se já estava cacheado
    """
    logger.info(f"📊 FASE 2 — Carregando odds para {date}")

    try:
        result = await preload_service.preload_odds_for_date(date)

        return {
            "success": True,
            "date": result["date"],
            "total_odds": result["total_odds"],
            "from_cache": result.get("from_cache", False),
        }

    except Exception as e:
        logger.error(f"❌ Erro ao carregar odds de {date}: {e}")
        return {"success": False, "date": date, "total_odds": 0, "error": str(e)}


class LeagueOddsRequest(BaseModel):
    """Request body para buscar odds de uma liga"""
    league_id: str
    dates: List[str]  # Lista de datas YYYY-MM-DD


@router.post("/preload/odds/league")
async def fetch_odds_for_league(request: LeagueOddsRequest):
    """
    Carrega odds de uma LIGA específica para as datas informadas.

    Usa GET /odds?league={id}&date={date} — busca APENAS odds da liga,
    muito mais eficiente que buscar todas as odds do dia.

    Chamado pelo frontend quando o usuário seleciona uma liga no carrossel.

    Body:
        - league_id: ID da liga
        - dates: Lista de datas YYYY-MM-DD que têm jogos dessa liga

    Returns:
        - total_odds: total de fixtures com odds carregadas
        - dates_loaded: detalhes por data
    """
    logger.info(f"📊 Carregando odds da liga {request.league_id} para {len(request.dates)} datas")

    try:
        result = await preload_service.preload_odds_for_league(
            league_id=request.league_id,
            dates=request.dates
        )

        return {
            "success": True,
            "league_id": result["league_id"],
            "total_odds": result["total_odds"],
            "dates_loaded": result["dates_loaded"],
            "from_cache": result.get("from_cache", False),
        }

    except Exception as e:
        logger.error(f"❌ Erro ao carregar odds da liga {request.league_id}: {e}")
        return {
            "success": False,
            "league_id": request.league_id,
            "total_odds": 0,
            "error": str(e)
        }

