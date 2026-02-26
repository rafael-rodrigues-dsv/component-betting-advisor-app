"""
API-Football Service - Camada de serviço para API-Football

Orquestra client + cache + parsers conforme arquitetura.
"""

from datetime import date
from typing import List, Dict, Any, Optional
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
    - Buscar fixtures e odds
    - Cachear com TTL apropriado
    - Parsear responses
    """

    def __init__(self):
        # Inicializa client com configurações
        self.client = APIFootballClient(
            mode=settings.API_FOOTBALL_MODE,
            api_key=settings.API_FOOTBALL_KEY,
            base_url=settings.API_FOOTBALL_BASE_URL
        )
        self.cache = get_cache()
        logger.info("⚽ APIFootballService inicializado")

    async def get_fixtures(self, league_id: int, fixture_date: date) -> List[Dict[str, Any]]:
        """
        Busca fixtures com cache (6h).

        Args:
            league_id: ID da liga
            fixture_date: Data dos jogos

        Returns:
            Lista de fixtures parseados
        """
        cache_key = f"fixtures:{league_id}:{fixture_date.isoformat()}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key}")
            return cached

        # Cache MISS - busca da API
        logger.debug(f"❌ Cache MISS: {cache_key}")

        # Resolve a season correta para essa liga
        season = await self._get_current_season(league_id)

        params = {
            "league": league_id,
            "date": fixture_date.isoformat()
        }
        if season:
            params["season"] = season

        api_response = await self.client.get("/fixtures", params)

        # Parse
        fixtures = FixtureParser.parse(api_response)

        # Cache (6 horas) - não cacheia listas vazias para permitir retry
        if fixtures:
            self.cache.set(cache_key, fixtures, ttl_seconds=21600)

        logger.info(f"📥 {len(fixtures)} fixtures obtidos da API e cacheados (liga={league_id}, season={season})")
        return fixtures

    async def get_odds(self, fixture_id: int) -> Dict[str, Any]:
        """
        Busca odds com cache (30min).

        Args:
            fixture_id: ID do fixture

        Returns:
            Odds parseadas por bookmaker
        """
        cache_key = f"odds:{fixture_id}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached:
            logger.debug(f"✅ Cache HIT: {cache_key}")
            return cached

        # Cache MISS - busca da API
        logger.debug(f"❌ Cache MISS: {cache_key}")

        api_response = await self.client.get("/odds", {
            "fixture": fixture_id
        })

        # Parse
        odds = OddsParser.parse(api_response)

        # Cache (30 minutos = 1800 segundos)
        self.cache.set(cache_key, odds, ttl_seconds=1800)

        logger.info(f"📊 Odds obtidas da API e cacheadas")
        return odds

    async def get_fixture_result(self, fixture_id: str) -> Dict[str, Any]:
        """
        Busca resultado de uma partida específica (sem cache).

        Na API real: GET /fixtures?id={fixture_id}
        Retorna status da partida e placar final.

        Args:
            fixture_id: ID do fixture

        Returns:
            Resultado da partida com placar e status
        """
        logger.info(f"🔍 Buscando resultado da partida {fixture_id}")

        api_response = await self.client.get("/fixtures", {
            "id": fixture_id
        })

        logger.debug(f"📥 API Response keys: {api_response.keys() if api_response else 'None'}")

        # A API retorna array, pega o primeiro resultado
        results = api_response.get("response", [])
        logger.debug(f"📋 Response array length: {len(results)}")

        if results:
            result = results[0]
            status = result.get("fixture", {}).get("status", {}).get("short", "NS")
            goals = result.get("goals", {})
            logger.info(f"⚽ Resultado obtido: {fixture_id} (status: {status}, placar: {goals.get('home')} x {goals.get('away')})")
            return result

        logger.warning(f"⚠️ Partida {fixture_id} não encontrada (response vazio)")
        return None

    async def _get_current_season(self, league_id: int) -> Optional[int]:
        """
        Resolve a season atual de uma liga via API-Football.

        Busca GET /leagues?id={league_id}&current=true e cacheia por 7 dias.
        Ligas europeias usam o ano de início (ex: 2025 para 2025/2026).
        Ligas brasileiras usam o ano corrente (ex: 2026).

        Args:
            league_id: ID da liga

        Returns:
            Ano da season atual (ex: 2025, 2026) ou None se não encontrar
        """
        cache_key = f"season:{league_id}"

        # Cache HIT
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"✅ Season cache HIT: liga {league_id} = {cached}")
            return cached

        # Cache MISS - busca da API
        try:
            api_response = await self.client.get("/leagues", {
                "id": league_id,
                "current": "true"
            })

            leagues = api_response.get("response", [])
            if leagues:
                seasons = leagues[0].get("seasons", [])
                for season in seasons:
                    if season.get("current"):
                        year = season["year"]
                        # Cache por 7 dias (604800 segundos)
                        self.cache.set(cache_key, year, ttl_seconds=604800)
                        logger.info(f"📅 Season atual da liga {league_id}: {year}")
                        return year

            logger.warning(f"⚠️ Season não encontrada para liga {league_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar season da liga {league_id}: {e}")
            return None

