"""
Match Service - Lógica de negócio para matches.

Lê fixtures do cache. Odds são carregadas sob demanda por partida.
"""

from datetime import date, datetime, timedelta
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

    Busca fixtures do cache (preload).
    Odds são carregadas sob demanda via get_odds_for_match / refresh_odds_for_match.
    """

    def __init__(self):
        self.cache = get_cache()
        self.api_service = APIFootballService()

    def _filter_active(self, fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtra apenas partidas ativas (não encerradas)."""
        return [f for f in fixtures if f.get("status_short", "NS") in ACTIVE_STATUSES]

    def get_matches_by_league_and_date(
        self,
        league_id: int,
        match_date: date
    ) -> List[Dict[str, Any]]:
        """
        Busca matches de uma liga em uma data específica.
        Retorna SEM odds — odds são carregadas sob demanda.
        Filtra apenas partidas ativas (não encerradas).
        """
        cache_key = f"fixtures:{league_id}:{match_date.isoformat()}"
        fixtures = self.cache.get(cache_key)

        if not fixtures:
            logger.warning(f"Nenhum fixture encontrado para {cache_key}")
            return []

        # Filtra partidas encerradas
        active_fixtures = self._filter_active(fixtures)

        # Monta matches SEM odds (odds são carregadas sob demanda)
        matches = []
        for fixture in active_fixtures:
            match = {
                **fixture,
                "odds": {}  # Vazio — frontend carrega sob demanda
            }
            matches.append(match)

        logger.info(f"✅ {len(matches)} matches ativos para liga {league_id} em {match_date} (total: {len(fixtures)})")
        return matches

    def get_all_matches_by_date(self, match_date: date) -> List[Dict[str, Any]]:
        """
        Busca todos os matches de todas as ligas em uma data.

        Args:
            match_date: Data dos matches

        Returns:
            Lista de todos os matches
        """
        # Ligas pré-carregadas
        league_ids = [71, 73, 39, 140, 78, 61, 135]

        all_matches = []

        for league_id in league_ids:
            matches = self.get_matches_by_league_and_date(league_id, match_date)
            all_matches.extend(matches)

        logger.info(f"✅ Total: {len(all_matches)} matches em {match_date}")
        return all_matches

    def get_match_by_id(self, fixture_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca um match específico por ID.
        Retorna SEM odds.
        """
        league_ids = [71, 73, 39, 140, 78, 61, 135]
        today = date.today()

        fixture = None
        for day_offset in range(15):
            search_date = today + timedelta(days=day_offset)
            for league_id in league_ids:
                cache_key = f"fixtures:{league_id}:{search_date.isoformat()}"
                fixtures = self.cache.get(cache_key)
                if fixtures:
                    for f in fixtures:
                        if str(f.get("id")) == str(fixture_id):
                            fixture = f
                            break
                if fixture:
                    break
            if fixture:
                break

        if not fixture:
            logger.warning(f"Fixture {fixture_id} não encontrado no cache")
            return None

        return {
            **fixture,
            "odds": {}
        }

    async def get_odds_for_match(self, fixture_id: int) -> Dict[str, Any]:
        """
        Busca odds de uma partida (cache ou API).
        Filtra apenas bookmakers suportadas.
        """
        raw_odds = await self.api_service.get_odds(fixture_id)
        odds = {k: v for k, v in (raw_odds or {}).items() if k in settings.supported_bookmakers_set}
        logger.info(f"📊 Odds carregadas para fixture {fixture_id}: {list(odds.keys())}")
        return odds

    async def get_odds_batch(self, fixture_ids: List[int]) -> Dict[str, Dict[str, Any]]:
        """
        Busca odds de múltiplas partidas (cache ou API).
        Retorna dict fixture_id → odds.
        """
        result = {}
        for fixture_id in fixture_ids:
            try:
                odds = await self.get_odds_for_match(fixture_id)
                result[str(fixture_id)] = odds
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar odds do fixture {fixture_id}: {e}")
                result[str(fixture_id)] = {}
        logger.info(f"📊 Odds em lote: {len(result)} fixtures processados")
        return result

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
            Dict com status e status_short, ou {} se não encontrou
        """
        result = await self.api_service.get_fixture_result(str(fixture_id))
        if not result:
            return {}

        status_data = (result.get("fixture") or {}).get("status") or {}
        return {
            "status": status_data.get("long") or "Not Started",
            "status_short": status_data.get("short") or "NS",
        }

    def get_leagues(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de ligas disponíveis.

        Returns:
            Lista de ligas
        """
        return [
            {
                "id": "71",
                "name": "Brasileirão Série A",
                "country": "Brazil",
                "logo": "🇧🇷",
                "type": "league"
            },
            {
                "id": "73",
                "name": "Copa do Brasil",
                "country": "Brazil",
                "logo": "🇧🇷",
                "type": "cup"
            },
            {
                "id": "39",
                "name": "Premier League",
                "country": "England",
                "logo": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                "type": "league"
            },
            {
                "id": "140",
                "name": "La Liga",
                "country": "Spain",
                "logo": "🇪🇸",
                "type": "league"
            },
            {
                "id": "78",
                "name": "Bundesliga",
                "country": "Germany",
                "logo": "🇩🇪",
                "type": "league"
            },
            {
                "id": "61",
                "name": "Ligue 1",
                "country": "France",
                "logo": "🇫🇷",
                "type": "league"
            },
            {
                "id": "135",
                "name": "Serie A",
                "country": "Italy",
                "logo": "🇮🇹",
                "type": "league"
            }
        ]


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

        Lê SUPPORTED_BOOKMAKERS do settings e monta a lista
        com metadados (nome, logo). A primeira da lista é o padrão.

        Returns:
            Lista de bookmakers
        """
        supported = list(settings.supported_bookmakers_set)
        # Ordena para manter consistência (primeiro da config = default)
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

