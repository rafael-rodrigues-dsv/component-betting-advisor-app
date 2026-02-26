"""
Preload Service - Pré-carregamento de fixtures e odds por data.

Dois fluxos separados:
1. preload_fixtures(days) — rápido, 1 request/dia, carrega fixtures
2. preload_odds_for_date(date) — lento (paginado), 1 data por vez, carrega odds

Cache incremental: 3 dias → 7 dias → 14 dias.
Ligas extraídas dinamicamente dos fixtures.
"""

from datetime import date, timedelta
from typing import List, Dict, Any
import logging

from infrastructure.cache.cache_manager import get_cache
from infrastructure.external.api_football.service import APIFootballService
from config.settings import settings

logger = logging.getLogger(__name__)


class PreloadService:
    """
    Serviço de pré-carregamento.

    Separado em duas fases:
    - Fase 1 (fixtures): rápido, mostra jogos na tela imediatamente
    - Fase 2 (odds): lento (paginado), roda em background data por data
    """

    def __init__(self):
        self.cache = get_cache()
        self.api_service = APIFootballService()

    def _get_dates(self, days: int = 7) -> List[date]:
        """Retorna lista de datas desde hoje até 'days' dias à frente."""
        today = settings.today()
        logger.info(f"📅 Hoje (timezone {settings.TIMEZONE}): {today.isoformat()}")
        return [today + timedelta(days=i) for i in range(days)]

    def _get_cached_period(self) -> int:
        cached_date = self.cache.get("preload:last_date")
        cached_days = self.cache.get("preload:last_days")
        today_str = settings.today().isoformat()
        if cached_date == today_str and cached_days:
            return int(cached_days)
        return 0

    async def has_todays_cache(self) -> bool:
        return self._get_cached_period() > 0

    def _extract_leagues(self, all_fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrai ligas únicas dos fixtures carregados."""
        seen = set()
        leagues = []
        for fixture in all_fixtures:
            league_data = fixture.get("league", {})
            league_id = str(league_data.get("id", ""))
            if league_id and league_id not in seen:
                seen.add(league_id)
                leagues.append({
                    "id": league_id,
                    "name": league_data.get("name", ""),
                    "country": league_data.get("country", ""),
                    "logo": league_data.get("logo", ""),
                    "type": league_data.get("type", "league"),
                })
        leagues.sort(key=lambda l: (l["country"], l["name"]))
        logger.info(f"🏆 {len(leagues)} ligas distintas extraídas dos fixtures")
        return leagues

    # ========================================
    # FASE 1: Fixtures (rápido)
    # ========================================

    async def preload_fixtures(self, days: int = 7) -> Dict[str, Any]:
        """
        Pré-carrega APENAS fixtures por data (sem odds).
        Rápido: 1 request por dia, sem paginação.

        Returns:
            Dict com total_fixtures, leagues, dates (lista de datas carregadas)
        """
        cached_days = self._get_cached_period()

        # Se já tem cache suficiente, retorna do cache
        if cached_days >= days:
            logger.info(f"✅ Cache de {cached_days} dias já existe para fixtures")
            cached_leagues = self.cache.get("leagues:dynamic") or []
            all_dates = self._get_dates(days)
            return {
                "total_fixtures": 0,
                "leagues": cached_leagues,
                "dates": [d.isoformat() for d in all_dates],
                "from_cache": True,
            }

        # Calcula datas incrementais
        all_dates = self._get_dates(days)
        if cached_days > 0:
            dates_to_fetch = all_dates[cached_days:]
            logger.info(f"📦 Cache incremental fixtures: já tem {cached_days} dias, carregando mais {len(dates_to_fetch)}")
        else:
            self.cache.delete_by_prefix("fixtures:")
            dates_to_fetch = all_dates
            logger.info(f"🗑️ Cache limpo, carregando {len(dates_to_fetch)} dias de fixtures")

        logger.info(f"🚀 Carregando fixtures: {len(dates_to_fetch)} dias...")

        total_fixtures = 0
        all_loaded_fixtures = []

        for fetch_date in dates_to_fetch:
            try:
                fixtures = await self.api_service.get_all_fixtures_by_date(fetch_date)
                count = len(fixtures) if fixtures else 0
                total_fixtures += count
                if fixtures:
                    all_loaded_fixtures.extend(fixtures)
                logger.info(f"  📅 {fetch_date.isoformat()}: {count} fixtures")
            except Exception as e:
                logger.error(f"  ❌ Erro fixtures {fetch_date}: {e}")

        # Inclui fixtures já cacheados para extrair ligas completas
        if cached_days > 0:
            for i in range(cached_days):
                cached_fixtures = self.cache.get(f"fixtures:{all_dates[i].isoformat()}")
                if cached_fixtures:
                    all_loaded_fixtures.extend(cached_fixtures)

        # Extrai ligas e salva no cache
        dynamic_leagues = self._extract_leagues(all_loaded_fixtures)
        self.cache.set("leagues:dynamic", dynamic_leagues, ttl_seconds=86400)

        # Marca período cacheado
        self.cache.set("preload:last_date", settings.today().isoformat(), ttl_seconds=86400)
        self.cache.set("preload:last_days", days, ttl_seconds=86400)

        logger.info(f"✅ Fixtures concluído! {total_fixtures} fixtures, {len(dynamic_leagues)} ligas")

        return {
            "total_fixtures": total_fixtures,
            "leagues": dynamic_leagues,
            "dates": [d.isoformat() for d in all_dates],
            "from_cache": False,
        }

    # ========================================
    # FASE 2: Odds de uma data (lento, paginado)
    # ========================================

    async def preload_odds_for_date(self, odds_date_str: str) -> Dict[str, Any]:
        """
        Carrega odds de UMA data específica (com paginação).
        Chamado pelo frontend data por data, em background.

        Args:
            odds_date_str: Data no formato YYYY-MM-DD

        Returns:
            Dict com total_odds para essa data
        """
        cache_key = f"odds_date:{odds_date_str}"

        # Já tem cache?
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"✅ Odds já cacheadas para {odds_date_str}: {len(cached)} fixtures")
            return {
                "date": odds_date_str,
                "total_odds": len(cached),
                "from_cache": True,
            }

        # Busca da API (paginado)
        from datetime import date as date_cls
        parts = odds_date_str.split("-")
        odds_date = date_cls(int(parts[0]), int(parts[1]), int(parts[2]))

        odds = await self.api_service.get_all_odds_by_date(odds_date)
        count = len(odds) if odds else 0

        logger.info(f"📊 Odds carregadas para {odds_date_str}: {count} fixtures")

        return {
            "date": odds_date_str,
            "total_odds": count,
            "from_cache": False,
        }
