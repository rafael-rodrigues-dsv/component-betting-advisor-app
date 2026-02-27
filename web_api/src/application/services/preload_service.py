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
                    "has_statistics_fixtures": False,  # Default, será enriquecido depois
                })
        leagues.sort(key=lambda l: (l["country"], l["name"]))
        logger.info(f"🏆 {len(leagues)} ligas distintas extraídas dos fixtures")
        return leagues

    async def _enrich_leagues_with_coverage(self, leagues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filtra ligas mantendo APENAS as que possuem statistics_fixtures: true.

        Busca GET /leagues?season={year} — cacheia por 7 dias.
        Busca SEMPRE season atual E anterior para cobrir todas as ligas:
        - Ligas brasileiras: season = ano corrente (ex: 2026)
        - Ligas europeias: season = ano anterior (ex: 2025 para 2025/2026)

        Ligas sem statistics_fixtures são REMOVIDAS (não entram no cache).
        """
        try:
            season = settings.today().year

            # Busca ambas as seasons para máxima cobertura
            coverage_current = await self.api_service.get_leagues_coverage(season)
            coverage_previous = await self.api_service.get_leagues_coverage(season - 1)

            # Merge: prioridade para season atual, fallback para anterior
            coverage_map = {**coverage_previous, **coverage_current}

            filtered_leagues = []
            removed = 0

            for league in leagues:
                lid = league["id"]
                cov = coverage_map.get(lid)

                if cov and cov.get("statistics_fixtures", False):
                    league["has_statistics_fixtures"] = True
                    # Atualiza type da API (mais preciso que o fallback do fixture)
                    if cov.get("type"):
                        league["type"] = cov["type"]
                    filtered_leagues.append(league)
                else:
                    removed += 1

            logger.info(
                f"📊 Coverage filtrado: {len(filtered_leagues)} ligas com statistics_fixtures "
                f"(removidas: {removed}, mapa total: {len(coverage_map)})"
            )
            return filtered_leagues
        except Exception as e:
            logger.error(f"⚠️ Erro ao filtrar coverage: {e} — retornando todas as ligas")
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
            self.cache.delete_by_prefix("odds_league:")
            dates_to_fetch = all_dates
            logger.info(f"🗑️ Cache limpo (fixtures + odds_league), carregando {len(dates_to_fetch)} dias de fixtures")

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

        # Extrai ligas e enriquece com coverage
        dynamic_leagues = self._extract_leagues(all_loaded_fixtures)
        dynamic_leagues = await self._enrich_leagues_with_coverage(dynamic_leagues)
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
    # FASE 2: Odds de uma data (lento, paginado) — LEGACY
    # ========================================

    async def preload_odds_for_date(self, odds_date_str: str) -> Dict[str, Any]:
        """
        Carrega odds de UMA data específica (com paginação).
        Chamado pelo frontend data por data, em background.
        LEGACY — preferir preload_odds_for_league para buscar sob demanda.

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

    # ========================================
    # FASE 2b: Odds por liga (sob demanda, equilibrado)
    # ========================================

    async def preload_odds_for_league(self, league_id: str, dates: List[str]) -> Dict[str, Any]:
        """
        Carrega odds de uma LIGA específica para múltiplas datas.
        Usa GET /odds?league={id}&season={year}&date={date}.

        Extrai o season dos fixtures cacheados (necessário para a API-Football).

        Args:
            league_id: ID da liga (string)
            dates: Lista de datas no formato YYYY-MM-DD

        Returns:
            Dict com total_odds e detalhes por data
        """
        from datetime import date as date_cls

        league_id_int = int(league_id)
        total_odds = 0
        dates_loaded = []
        all_from_cache = True

        # Extrai season dos fixtures cacheados para esta liga
        season = self._get_league_season(league_id, dates)
        if season:
            logger.info(f"🏆 Liga {league_id}: season={season}")
        else:
            logger.warning(f"⚠️ Liga {league_id}: season não encontrada nos fixtures")

        for date_str in dates:
            cache_key = f"odds_league:{league_id}:{date_str}"
            cached = self.cache.get(cache_key)

            if cached:
                count = len(cached)
                total_odds += count
                dates_loaded.append({"date": date_str, "count": count, "from_cache": True})
                logger.debug(f"✅ Odds liga {league_id} em {date_str}: {count} (cache)")
                continue

            # Verifica se esta liga tem fixtures nesta data (evita requests desnecessários)
            has_fixtures = self._league_has_fixtures_on_date(league_id, date_str)
            if not has_fixtures:
                dates_loaded.append({"date": date_str, "count": 0, "from_cache": False})
                logger.debug(f"⏭️ Liga {league_id} sem fixtures em {date_str}, pulando odds")
                continue

            all_from_cache = False

            try:
                parts = date_str.split("-")
                odds_date = date_cls(int(parts[0]), int(parts[1]), int(parts[2]))

                # Tenta com season principal
                league_odds = await self.api_service.get_odds_by_league_and_date(
                    league_id_int, odds_date, season=season
                )

                # Se não encontrou odds e season é do ano corrente, tenta ano anterior
                # (ligas europeias usam season do ano anterior, ex: 2025/2026)
                if not league_odds and season:
                    alt_season = season - 1
                    logger.info(f"🔄 Liga {league_id}: tentando season alternativa {alt_season}...")
                    league_odds = await self.api_service.get_odds_by_league_and_date(
                        league_id_int, odds_date, season=alt_season
                    )
                    if league_odds:
                        logger.info(f"✅ Liga {league_id}: season correta é {alt_season}")

                count = len(league_odds) if league_odds else 0
                total_odds += count
                dates_loaded.append({"date": date_str, "count": count, "from_cache": False})
                logger.info(f"📊 Odds liga {league_id} em {date_str}: {count} fixtures")
            except Exception as e:
                logger.error(f"❌ Erro odds liga {league_id} em {date_str}: {e}")
                dates_loaded.append({"date": date_str, "count": 0, "from_cache": False})

        logger.info(f"✅ Odds liga {league_id}: {total_odds} fixtures em {len(dates)} datas")

        return {
            "league_id": league_id,
            "total_odds": total_odds,
            "dates_loaded": dates_loaded,
            "from_cache": all_from_cache,
        }

    def _league_has_fixtures_on_date(self, league_id: str, date_str: str) -> bool:
        """Verifica se uma liga tem fixtures em uma data específica."""
        cached_fixtures = self.cache.get(f"fixtures:{date_str}")
        if not cached_fixtures:
            return False
        return any(
            str(f.get("league", {}).get("id", "")) == str(league_id)
            for f in cached_fixtures
        )

    def _get_league_season(self, league_id: str, dates: List[str]) -> int:
        """
        Extrai o season (ano) de uma liga a partir dos fixtures cacheados.

        Percorre as datas e busca o primeiro fixture da liga para extrair o season.
        Fallback: usa o ano da primeira data como season.

        Args:
            league_id: ID da liga
            dates: Lista de datas YYYY-MM-DD

        Returns:
            Ano da season (ex: 2026) ou None
        """
        for date_str in dates:
            cached_fixtures = self.cache.get(f"fixtures:{date_str}")
            if not cached_fixtures:
                continue
            for fixture in cached_fixtures:
                fixture_league = fixture.get("league", {})
                if str(fixture_league.get("id", "")) == str(league_id):
                    season = fixture_league.get("season")
                    if season:
                        return int(season)

        # Fallback: extrai ano da primeira data
        if dates:
            try:
                year = int(dates[0].split("-")[0])
                logger.info(f"⚠️ Liga {league_id}: season fallback para {year}")
                return year
            except (ValueError, IndexError):
                pass

        return None

