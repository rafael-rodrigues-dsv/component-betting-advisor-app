"""
Preload Controller - Endpoints de pré-carregamento sob demanda.
"""

from datetime import timedelta
from fastapi import APIRouter, Query
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
    Retorna o status do pré-carregamento de ligas.

    Returns:
        Informações sobre cache e ligas pré-carregadas
    """
    has_cache = await preload_service.has_todays_cache()
    return map_preload_status(cache_valid=has_cache)


@router.post("/preload/fetch")
async def fetch_preload(
    days: int = Query(7, description="Número de dias a carregar (3, 7 ou 14)")
):
    """
    Dispara o pré-carregamento das ligas principais sob demanda.

    O usuário escolhe o período: 3, 7 ou 14 dias.

    Args:
        days: Quantidade de dias a partir de hoje (aceita 3, 7 ou 14)

    Returns:
        Status do carregamento com informações do período
    """
    # Valida o parâmetro
    allowed_days = [3, 7, 14]
    if days not in allowed_days:
        return {
            "success": False,
            "message": f"Valor inválido para 'days'. Use: {allowed_days}"
        }

    logger.info(f"📥 Pré-carregamento sob demanda: {days} dias")

    try:
        await preload_service.preload_main_leagues(days=days)

        today = settings.today()
        date_from = today.isoformat()
        date_to = (today + timedelta(days=days - 1)).isoformat()

        logger.info(f"✅ Pré-carregamento concluído: {date_from} até {date_to} (timezone: {settings.TIMEZONE})")

        return {
            "success": True,
            "message": f"Dados carregados com sucesso para {days} dias",
            "days": days,
            "date_from": date_from,
            "date_to": date_to,
        }

    except Exception as e:
        logger.error(f"❌ Erro no pré-carregamento sob demanda: {e}")
        return {
            "success": False,
            "message": f"Erro ao carregar dados: {str(e)}"
        }

