"""
Match Service - Lógica de negócio para matches.

Lê fixtures do cache (key: fixtures:{date}).
Odds são pré-carregadas em bulk e embutidas nos matches.
Ligas são extraídas dinamicamente dos dados carregados.
"""

from datetime import date, timedelta
from typing import List, Optional, Dict, Any
import logging

from infrastructure.cache.cache_manager import get_cache
from infrastructure.external.api_football.service import APIFootballService
from config.settings import settings
from domain.constants.constants import ACTIVE_STATUSES

logger = logging.getLogger(__name__)


class MatchService:
    """
    Serviço de matches.

    Busca fixtures do cache (preload BULK por data).
    Odds são pré-carregadas em bulk e embutidas nos matches.
    Ligas são dinâmicas (extraídas dos dados carregados).
    """

    def __init__(self):
        self.cache = get_cache()
        self.api_service = APIFootballService()

    def _filter_active(self, fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtra apenas partidas ativas (não encerradas)."""
        return [f for f in fixtures if f.get("status_short", "NS") in ACTIVE_STATUSES]

    def _get_odds_for_fixture(self, fixture_id: str, fixture_date_str: str) -> Dict[str, Any]:
        """
        Busca odds de um fixture do cache.

        Primeiro tenta cache individual (odds:{fixture_id}).
        Se miss, tenta extrair do cache bulk (odds_date:{date}).

        Args:
            fixture_id: ID do fixture
            fixture_date_str: Data no formato YYYY-MM-DD (para lookup no bulk cache)

        Returns:
            Odds por bookmaker (filtrado por suportadas)
        """
        # 1. Cache individual
        individual_odds = self.cache.get(f"odds:{fixture_id}")
        if individual_odds:
            return {k: v for k, v in individual_odds.items() if k in settings.supported_bookmakers_set}

        # 2. Cache bulk por data
        bulk_odds = self.cache.get(f"odds_date:{fixture_date_str}")
        if bulk_odds and fixture_id in bulk_odds:
            odds = bulk_odds[fixture_id]
            return {k: v for k, v in odds.items() if k in settings.supported_bookmakers_set}

        return {}

    def _build_match(self, fixture: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constrói um match a partir de um fixture, embutindo odds do cache.
        """
        fixture_id = str(fixture.get("id", ""))
        # Extrai data YYYY-MM-DD do fixture
        fixture_date_str = fixture.get("timestamp", "") or fixture.get("date", "")[:10]

        odds = self._get_odds_for_fixture(fixture_id, fixture_date_str)

        return {
            **fixture,
            "odds": odds,
        }

    def get_all_matches_by_date(self, match_date: date) -> List[Dict[str, Any]]:
        """
        Busca todos os matches de uma data (todas as ligas).
        Lê do cache bulk: fixtures:{date}.
        Embute odds do cache.

        Args:
            match_date: Data dos matches

        Returns:
            Lista de todos os matches com odds embutidas
        """
        cache_key = f"fixtures:{match_date.isoformat()}"
        fixtures = self.cache.get(cache_key)

        if not fixtures:
            logger.warning(f"Nenhum fixture encontrado para {cache_key}")
            return []

        # Filtra partidas encerradas
        active_fixtures = self._filter_active(fixtures)

        # Monta matches com odds embutidas
        matches = [self._build_match(f) for f in active_fixtures]

        logger.info(f"✅ Total: {len(matches)} matches ativos em {match_date} (de {len(fixtures)} total)")
        return matches

    def get_matches_by_league_and_date(
        self,
        league_id: int,
        match_date: date
    ) -> List[Dict[str, Any]]:
        """
        Busca matches de uma liga específica em uma data.
        Filtra do cache bulk fixtures:{date} por league.id.

        Args:
            league_id: ID da liga
            match_date: Data dos matches

        Returns:
            Lista de matches da liga com odds embutidas
        """
        all_matches = self.get_all_matches_by_date(match_date)
        league_matches = [m for m in all_matches if str(m.get("league", {}).get("id", "")) == str(league_id)]

        logger.info(f"✅ {len(league_matches)} matches para liga {league_id} em {match_date}")
        return league_matches

    def get_match_by_id(self, fixture_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um match específico por ID.
        Procura em todas as datas cacheadas (até 15 dias à frente).
        """
        today = settings.today()

        for day_offset in range(15):
            search_date = today + timedelta(days=day_offset)
            cache_key = f"fixtures:{search_date.isoformat()}"
            fixtures = self.cache.get(cache_key)
            if fixtures:
                for f in fixtures:
                    if str(f.get("id")) == str(fixture_id):
                        return self._build_match(f)

        logger.warning(f"Fixture {fixture_id} não encontrado no cache")
        return None

    async def get_odds_for_match(self, fixture_id: int) -> Dict[str, Any]:
        """
        Busca odds de uma partida (cache ou API).
        Filtra apenas bookmakers suportadas.
        """
        raw_odds = await self.api_service.get_odds(fixture_id)
        odds = {k: v for k, v in (raw_odds or {}).items() if k in settings.supported_bookmakers_set}
        logger.info(f"📊 Odds carregadas para fixture {fixture_id}: {list(odds.keys())}")
        return odds

    async def refresh_odds_for_match(self, fixture_id: int) -> Dict[str, Any]:
        """
        Força refresh das odds de uma partida (deleta cache e busca da API).

        Args:
            fixture_id: ID do fixture

        Returns:
            Dict com odds atualizadas por bookmaker
        """
        # Deleta cache existente
        cache_key = f"odds:{fixture_id}"
        self.cache.delete(cache_key)
        logger.info(f"🔄 Cache de odds deletado para fixture {fixture_id}")

        # Busca novas odds da API
        return await self.get_odds_for_match(fixture_id)

    async def get_fixture_live_status(self, fixture_id: int) -> Dict[str, Any]:
        """
        Busca o status atualizado de uma partida direto da API (sem cache).

        Returns:
            Dict com status, status_short, elapsed, goals
        """
        result = await self.api_service.get_fixture_result(str(fixture_id))
        if not result:
            return {}

        fixture_data = result.get("fixture") or {}
        status_data = fixture_data.get("status") or {}
        goals_data = result.get("goals") or {}

        return {
            "status": status_data.get("long") or "Not Started",
            "status_short": status_data.get("short") or "NS",
            "elapsed": status_data.get("elapsed"),
            "goals": {
                "home": goals_data.get("home"),
                "away": goals_data.get("away"),
            },
        }

    def get_leagues(self) -> List[Dict[str, Any]]:
        """
        Retorna ligas DINÂMICAS extraídas dos fixtures carregados.
        Lê do cache: leagues:dynamic

        Returns:
            Lista de ligas disponíveis no período carregado
        """
        cached = self.cache.get("leagues:dynamic")
        if cached:
            return cached

        # Fallback: sem dados carregados
        logger.warning("⚠️ Nenhuma liga dinâmica no cache. Faça o preload primeiro.")
        return []

    # Metadados das casas de apostas (logo, nome, etc.)
    BOOKMAKER_META = {
        "bet365":      {"name": "Bet365",      "logo": "🟢"},
        "betano":      {"name": "Betano",      "logo": "🟡"},
        "1xbet":       {"name": "1xBet",       "logo": "🔵"},
        "williamhill": {"name": "William Hill", "logo": "🏴"},
        "unibet":      {"name": "Unibet",      "logo": "🟣"},
        "betfair":     {"name": "Betfair",     "logo": "🟠"},
        "pinnacle":    {"name": "Pinnacle",    "logo": "📊"},
        "marathonbet": {"name": "Marathonbet", "logo": "🏃"},
        "888sport":    {"name": "888sport",    "logo": "🎱"},
        "10bet":       {"name": "10Bet",       "logo": "🔟"},
        "188bet":      {"name": "188bet",      "logo": "💎"},
        "sbo":         {"name": "SBO",         "logo": "⚡"},
    }

    def get_bookmakers(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de casas de apostas disponíveis.
        """
        config_order = [b.strip() for b in settings.SUPPORTED_BOOKMAKERS.split(',') if b.strip()]

        result = []
        for i, bk_id in enumerate(config_order):
            if bk_id in settings.supported_bookmakers_set:
                meta = self.BOOKMAKER_META.get(bk_id, {"name": bk_id, "logo": "🎰"})
                result.append({
                    "id": bk_id,
                    "name": meta["name"],
                    "logo": meta["logo"],
                    "is_default": i == 0,
                })
        return result

    async def get_live_updates(self) -> List[Dict[str, Any]]:
        """
        Busca fixtures ao vivo da API e retorna updates de placar/status/minuto.

        Filtra apenas fixtures que estão no nosso cache (carregados pelo preload).
        Atualiza o cache de fixtures com dados atualizados.

        Returns:
            Lista de dicts com {id, status, status_short, elapsed, goals}
        """
        live_fixtures = await self.api_service.get_live_fixtures()

        if not live_fixtures:
            return []

        # Coleta IDs de fixtures carregados no cache
        loaded_ids = set()
        today = settings.today()
        for day_offset in range(15):
            search_date = today + timedelta(days=day_offset)
            cache_key = f"fixtures:{search_date.isoformat()}"
            cached = self.cache.get(cache_key)
            if cached:
                for f in cached:
                    loaded_ids.add(str(f.get("id")))

        # Filtra apenas fixtures que estão carregados E atualiza o cache
        updates = []
        for live in live_fixtures:
            fid = str(live.get("id"))
            if fid in loaded_ids:
                updates.append({
                    "id": fid,
                    "status": live.get("status", "Not Started"),
                    "status_short": live.get("status_short", "NS"),
                    "elapsed": live.get("elapsed"),
                    "goals": live.get("goals", {"home": None, "away": None}),
                })

                # Atualiza fixture no cache
                self._update_fixture_in_cache(fid, live)

        logger.info(f"🔴 {len(updates)} updates de jogos ao vivo (de {len(live_fixtures)} total da API)")
        return updates

    def _update_fixture_in_cache(self, fixture_id: str, live_data: Dict[str, Any]):
        """Atualiza um fixture no cache com dados ao vivo."""
        today = settings.today()
        for day_offset in range(15):
            search_date = today + timedelta(days=day_offset)
            cache_key = f"fixtures:{search_date.isoformat()}"
            cached = self.cache.get(cache_key)
            if cached:
                for i, f in enumerate(cached):
                    if str(f.get("id")) == fixture_id:
                        cached[i]["status"] = live_data.get("status", f.get("status"))
                        cached[i]["status_short"] = live_data.get("status_short", f.get("status_short"))
                        cached[i]["elapsed"] = live_data.get("elapsed")
                        cached[i]["goals"] = live_data.get("goals", f.get("goals", {}))
                        self.cache.set(cache_key, cached, ttl_seconds=settings.CACHE_TTL_FIXTURES)
                        return

