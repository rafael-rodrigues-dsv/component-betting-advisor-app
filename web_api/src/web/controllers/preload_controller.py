"""
Preload Controller - Endpoints de status do pré-carregamento.
"""

from fastapi import APIRouter
from web.mappers.preload_mapper import map_preload_status

router = APIRouter()


@router.get("/preload/status")
async def get_preload_status():
    """
    Retorna o status do pré-carregamento de ligas.

    Returns:
        Informações sobre cache e ligas pré-carregadas
    """
    # TODO: Buscar informação real do cache via PreloadService
    # Por enquanto retorna que está válido (mockado)

    return map_preload_status(cache_valid=True)

