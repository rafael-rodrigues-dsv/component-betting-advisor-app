"""
Preload Service - Pré-carregamento de fixtures das ligas principais.

Executado sob demanda via POST /api/v1/preload/fetch?days=N.
O usuário escolhe o período (3, 7 ou 14 dias) na interface.

Cache incremental: 3 dias → 7 dias reaproveita cache → 14 dias reaproveita cache.
NÃO carrega odds — odds são carregadas sob demanda por partida.
"""

from datetime import date, timedelta
from typing import List
import logging

from infrastructure.cache.cache_manager import get_cache
from infrastructure.external.api_football.service import APIFootballService
from domain.constants.constants import MAIN_LEAGUES

logger = logging.getLogger(__name__)


class PreloadService:
    """
    Serviço de pré-carregamento de dados.

    Busca apenas fixtures (sem odds) das ligas principais via API-Football.
    Suporta cache incremental por período (3 → 7 → 14 dias).
    """

    def __init__(self):
        self.cache = get_cache()
        self.api_service = APIFootballService()

    def _get_dates(self, days: int = 7) -> List[date]:
        """Retorna lista de datas desde hoje até 'days' dias à frente."""
        today = date.today()
        return [today + timedelta(days=i) for i in range(days)]

    def _get_cached_period(self) -> int:
        """
        Retorna o período já cacheado (0 se nenhum ou de outro dia).
        """
        cached_date = self.cache.get("preload:last_date")
        cached_days = self.cache.get("preload:last_days")

        if cached_date == date.today().isoformat() and cached_days:
            return int(cached_days)

        return 0

    async def has_todays_cache(self) -> bool:
        """Verifica se já tem cache de fixtures do dia atual."""
        return self._get_cached_period() > 0

    async def preload_fixtures(self, league_ids: List[int], days: int = 7):
        """
        Pré-carrega fixtures de múltiplas ligas para o período solicitado.
        Cache incremental: se já tem 3 dias cacheados e pede 7, carrega só dias 4-7.
        NÃO carrega odds.

        Args:
            league_ids: Lista de IDs das ligas
            days: Número de dias a carregar (3, 7 ou 14)
        """
        cached_days = self._get_cached_period()

        # Se já tem cache suficiente para o período pedido, não faz nada
        if cached_days >= days:
            logger.info(f"✅ Cache de {cached_days} dias já existe, período de {days} dias coberto")
            return

        # Calcula datas incrementais (pula as que já estão cacheadas)
        all_dates = self._get_dates(days)
        if cached_days > 0:
            # Já tem cache dos primeiros N dias, pega só o restante
            dates_to_fetch = all_dates[cached_days:]
            logger.info(f"📦 Cache incremental: já tem {cached_days} dias, carregando mais {len(dates_to_fetch)} dias")
        else:
            # Limpa cache antigo (de outro dia) e carrega tudo
            self.cache.delete_by_prefix("fixtures:")
            dates_to_fetch = all_dates
            logger.info(f"🗑️ Cache limpo (novo dia), carregando {len(dates_to_fetch)} dias")

        logger.info(f"🚀 Pré-carregamento de {len(league_ids)} ligas × {len(dates_to_fetch)} dias...")
        logger.info(f"📅 Período: {dates_to_fetch[0]} até {dates_to_fetch[-1]}")

        total_fixtures = 0

        for league_id in league_ids:
            league_fixtures = 0
            try:
                for fixture_date in dates_to_fetch:
                    fixtures = await self.api_service.get_fixtures(league_id, fixture_date)
                    count = len(fixtures) if fixtures else 0
                    total_fixtures += count
                    league_fixtures += count

                logger.info(f"  ✅ Liga {league_id}: {league_fixtures} fixtures")
            except Exception as e:
                logger.error(f"  ❌ Erro ao pré-carregar liga {league_id}: {e}")

        # Marca período cacheado (hoje + total de dias)
        self.cache.set("preload:last_date", date.today().isoformat(), ttl_seconds=86400)
        self.cache.set("preload:last_days", days, ttl_seconds=86400)

        logger.info(f"✅ Pré-carregamento concluído! {total_fixtures} fixtures carregados")

    async def preload_main_leagues(self, days: int = 7):
        """
        Pré-carrega as ligas principais configuradas.

        Args:
            days: Número de dias a carregar (3, 7 ou 14)
        """
        await self.preload_fixtures(MAIN_LEAGUES, days)



