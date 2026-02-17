"""
Preload Mapper - Converte dados de pré-carregamento para DTOs
"""
from datetime import date
from typing import Dict, Any, List

from domain.constants.constants import LEAGUE_NAMES


def map_preload_status(cache_valid: bool, last_date: str = None) -> Dict[str, Any]:
    """
    Mapeia status do pré-carregamento para response.

    Args:
        cache_valid: Se o cache está válido
        last_date: Data do último pré-carregamento

    Returns:
        Dicionário com status do preload
    """
    today = date.today().isoformat()

    # Lista de ligas pré-carregadas (baseado nas constantes)
    leagues = list(LEAGUE_NAMES.values())

    return {
        "hasCache": cache_valid,
        "leagues": leagues,
        "timestamp": last_date or today,
        "cacheValid": cache_valid,
        "expiresAt": "23:59:59"  # Cache expira à meia-noite
    }


def map_preload_stats(
    total_fixtures: int,
    total_odds: int,
    leagues_loaded: List[int],
    date_range: tuple
) -> Dict[str, Any]:
    """
    Mapeia estatísticas do pré-carregamento.

    Args:
        total_fixtures: Total de fixtures carregados
        total_odds: Total de odds carregadas
        leagues_loaded: IDs das ligas carregadas
        date_range: Tupla (data_inicio, data_fim)

    Returns:
        Dicionário com estatísticas
    """
    leagues_names = [LEAGUE_NAMES.get(league_id, f"Liga {league_id}") for league_id in leagues_loaded]

    return {
        "total_fixtures": total_fixtures,
        "total_odds": total_odds,
        "leagues": leagues_names,
        "date_range": {
            "start": date_range[0],
            "end": date_range[1]
        }
    }

