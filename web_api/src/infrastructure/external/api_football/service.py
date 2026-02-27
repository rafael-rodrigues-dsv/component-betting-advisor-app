"""
API-Football Service - Camada de serviço para API-Football

Usa endpoints BULK por data:
- GET /fixtures?date={date} → todos os fixtures do dia (qualquer liga)
- GET /odds?date={date} → todas as odds do dia (qualquer liga)

Endpoints individuais mantidos para refresh sob demanda:
- GET /odds?fixture={id} → odds de um fixture específico
- GET /fixtures?id={id} → resultado de um fixture específico
"""

from datetime import date
from typing import List, Dict, Any
import logging

from infrastructure.cache.cache_manager import get_cache
from infrastructure.external.api_football.client import APIFootballClient
from infrastructure.external.api_football.parsers.fixture_parser import FixtureParser
from infrastructure.external.api_football.parsers.odds_parser import OddsParser
from config.settings import settings

logger = logging.getLogger(__name__)


class APIFootballService:
    """
    Serviço de integração com API-Football.

    Responsabilidades:
    - Buscar fixtures e odds por DATA (bulk)
    - Buscar odds por fixture (individual, para refresh)
    - Cachear com TTL apropriado
    - Parsear responses
    """

    def __init__(self):
        self.client = APIFootballClient(
            api_key=settings.API_FOOTBALL_KEY,
            base_url=settings.API_FOOTBALL_BASE_URL
        )
        self.cache = get_cache()
        logger.info("⚽ APIFootballService inicializado (modo BULK por data)")

    # ========================================
    # BULK: Fixtures por data
    # ========================================

    async def get_all_fixtures_by_date(self, fixture_date: date) -> List[Dict[str, Any]]:
        """
        Busca TODOS os fixtures de uma data (qualquer liga) com cache (6h).

        Usa GET /fixtures?date={date} — 1 request por dia.

        Args:
            fixture_date: Data dos jogos

        Returns:
            Lista de fixtures parseados (todas as ligas)
        """
        cache_key = f"fixtures:{fixture_date.isoformat()}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key} ({len(cached)} fixtures)")
            return cached

        # Cache MISS - busca da API
        logger.info(f"🌐 Buscando fixtures de {fixture_date.isoformat()} (BULK)...")

        api_response = await self.client.get("/fixtures", {
            "date": fixture_date.isoformat()
        })

        # Parse
        fixtures = FixtureParser.parse(api_response)

        # Cache (6 horas)
        if fixtures:
            self.cache.set(cache_key, fixtures, ttl_seconds=settings.CACHE_TTL_FIXTURES)

        logger.info(f"📥 {len(fixtures)} fixtures obtidos da API (data={fixture_date.isoformat()})")
        return fixtures

    # ========================================
    # BULK: Odds por data
    # ========================================

    async def get_all_odds_by_date(self, odds_date: date) -> Dict[str, Dict[str, Any]]:
        """
        Busca TODAS as odds de uma data (qualquer fixture) com cache (30min).

        Usa GET /odds?date={date} — 1 request por dia.
        Também popula cache individual odds:{fixture_id} para cada fixture.

        Args:
            odds_date: Data das odds

        Returns:
            Dict[fixture_id_str, Dict[bookmaker_name, bookmaker_odds]]
        """
        cache_key = f"odds_date:{odds_date.isoformat()}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key} ({len(cached)} fixtures com odds)")
            return cached

        # Cache MISS - busca da API (COM PAGINAÇÃO — /odds retorna max ~10 por página)
        logger.info(f"🌐 Buscando odds de {odds_date.isoformat()} (BULK com paginação)...")

        api_response = await self.client.get_all_pages("/odds", {
            "date": odds_date.isoformat()
        })

        # Parse bulk
        all_odds = OddsParser.parse_bulk(api_response)

        # Cache bulk (30 min)
        if all_odds:
            self.cache.set(cache_key, all_odds, ttl_seconds=settings.CACHE_TTL_ODDS)

            # Popula cache individual para cada fixture (usado por refresh)
            for fixture_id, odds in all_odds.items():
                individual_key = f"odds:{fixture_id}"
                self.cache.set(individual_key, odds, ttl_seconds=settings.CACHE_TTL_ODDS)

        logger.info(f"📊 {len(all_odds)} fixtures com odds obtidos da API (data={odds_date.isoformat()})")
        return all_odds

    # ========================================
    # BULK: Odds por liga + data (equilibrado)
    # ========================================

    async def get_odds_by_league_and_date(self, league_id: int, odds_date: date, season: int = None) -> Dict[str, Dict[str, Any]]:
        """
        Busca odds de uma LIGA específica em uma data com cache (30min).

        Usa GET /odds?league={id}&season={year}&date={date} — paginado, mas só fixtures da liga.
        Muito mais eficiente que buscar TODAS as odds do dia.
        Também popula cache individual odds:{fixture_id} para cada fixture.

        Args:
            league_id: ID da liga na API-Football
            odds_date: Data das odds
            season: Ano da season (obrigatório para a API-Football retornar dados)

        Returns:
            Dict[fixture_id_str, Dict[bookmaker_name, bookmaker_odds]]
        """
        cache_key = f"odds_league:{league_id}:{odds_date.isoformat()}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key} ({len(cached)} fixtures com odds)")
            return cached

        # Cache MISS - busca da API
        params = {
            "league": league_id,
            "date": odds_date.isoformat()
        }
        if season:
            params["season"] = season

        logger.info(f"🌐 Buscando odds da liga {league_id} season={season} em {odds_date.isoformat()}...")

        api_response = await self.client.get_all_pages("/odds", params)

        # Parse bulk
        league_odds = OddsParser.parse_bulk(api_response)

        # Cache por liga+data (30 min)
        if league_odds:
            self.cache.set(cache_key, league_odds, ttl_seconds=settings.CACHE_TTL_ODDS)

            # Popula cache individual para cada fixture
            for fixture_id, odds in league_odds.items():
                individual_key = f"odds:{fixture_id}"
                self.cache.set(individual_key, odds, ttl_seconds=settings.CACHE_TTL_ODDS)

        logger.info(f"📊 Liga {league_id}: {len(league_odds)} fixtures com odds em {odds_date.isoformat()}")
        return league_odds

    # ========================================
    # Individual: Odds por fixture (para refresh)
    # ========================================

    async def get_odds(self, fixture_id: int) -> Dict[str, Any]:
        """
        Busca odds de um fixture específico com cache (30min).

        Primeiro tenta cache individual (populado pelo bulk).
        Se miss, busca via GET /odds?fixture={id}.

        Args:
            fixture_id: ID do fixture

        Returns:
            Odds parseadas por bookmaker
        """
        cache_key = f"odds:{fixture_id}"

        # Cache HIT (pode ter sido populado pelo bulk ou por um refresh anterior)
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key}")
            return cached

        # Cache MISS - busca da API
        logger.debug(f"❌ Cache MISS: {cache_key}")

        api_response = await self.client.get("/odds", {
            "fixture": fixture_id
        })

        # Parse single
        odds = OddsParser.parse(api_response)

        # Cache (30 minutos)
        self.cache.set(cache_key, odds, ttl_seconds=settings.CACHE_TTL_ODDS)

        logger.info(f"📊 Odds obtidas da API para fixture {fixture_id}")
        return odds

    # ========================================
    # Individual: Resultado/status de fixture
    # ========================================

    async def get_fixture_result(self, fixture_id: str) -> Dict[str, Any]:
        """
        Busca resultado de uma partida específica (sem cache).

        GET /fixtures?id={fixture_id}

        Args:
            fixture_id: ID do fixture

        Returns:
            Resultado da partida com placar e status
        """
        logger.info(f"🔍 Buscando resultado da partida {fixture_id}")

        api_response = await self.client.get("/fixtures", {
            "id": fixture_id
        })

        results = api_response.get("response", [])

        if results:
            result = results[0]
            status = result.get("fixture", {}).get("status", {}).get("short", "NS")
            goals = result.get("goals", {})
            logger.info(f"⚽ Resultado: {fixture_id} (status: {status}, placar: {goals.get('home')} x {goals.get('away')})")
            return result

        logger.warning(f"⚠️ Partida {fixture_id} não encontrada")
        return None

    # ========================================
    # Leagues coverage (statistics_fixtures)
    # ========================================

    async def get_leagues_coverage(self, season: int = None) -> Dict[str, Dict[str, Any]]:
        """
        Busca coverage de TODAS as ligas para uma season.

        Usa GET /leagues?season={year} — retorna coverage.fixtures.statistics_fixtures.
        Cacheado por 7 dias (não muda durante a temporada).

        Args:
            season: Ano da temporada (default: ano atual)

        Returns:
            Dict[league_id_str, { statistics_fixtures: bool, events: bool, lineups: bool, ... }]
        """
        if not season:
            season = settings.today().year

        cache_key = f"leagues_coverage:{season}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key} ({len(cached)} ligas)")
            return cached

        # Cache MISS
        logger.info(f"🌐 Buscando coverage de ligas (season={season})...")

        api_response = await self.client.get("/leagues", {
            "season": season
        })

        leagues_data = api_response.get("response", [])
        coverage_map: Dict[str, Dict[str, Any]] = {}

        for item in leagues_data:
            league = item.get("league", {})
            league_id = str(league.get("id", ""))
            seasons = item.get("seasons", [])

            # Encontra a season solicitada
            for s in seasons:
                if s.get("year") == season:
                    fixtures_coverage = s.get("coverage", {}).get("fixtures", {})
                    coverage_map[league_id] = {
                        "statistics_fixtures": fixtures_coverage.get("statistics_fixtures", False),
                        "statistics_players": fixtures_coverage.get("statistics_players", False),
                        "events": fixtures_coverage.get("events", False),
                        "lineups": fixtures_coverage.get("lineups", False),
                        "type": league.get("type", "league"),
                    }
                    break

        # Cache 7 dias
        if coverage_map:
            self.cache.set(cache_key, coverage_map, ttl_seconds=604800)

        logger.info(f"📊 Coverage obtido: {len(coverage_map)} ligas (season={season})")
        return coverage_map

    # ========================================
    # Live fixtures (polling)
    # ========================================

    async def get_live_fixtures(self) -> List[Dict[str, Any]]:
        """
        Busca todos os fixtures em andamento (ao vivo) direto da API.

        GET /fixtures?live=all

        Sem cache — sempre busca da API para ter dados atualizados.

        Returns:
            Lista de fixtures parseados (com goals, elapsed, status atualizado)
        """
        logger.info("🔴 Buscando fixtures ao vivo...")

        api_response = await self.client.get("/fixtures", {
            "live": "all"
        })

        fixtures = FixtureParser.parse(api_response)
        logger.info(f"🔴 {len(fixtures)} fixtures ao vivo encontrados")
        return fixtures
