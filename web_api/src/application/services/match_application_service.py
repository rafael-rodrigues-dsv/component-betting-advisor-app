"""
Match Service - Lógica de negócio para matches.

Lê fixtures e odds do cache em memória.
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
import logging

from infrastructure.cache.cache_manager import get_cache

logger = logging.getLogger(__name__)


class MatchService:
    """
    Serviço de matches.

    Busca fixtures e odds do cache preload_service criou.
    """

    def __init__(self):
        self.cache = get_cache()

    def get_matches_by_league_and_date(
        self,
        league_id: int,
        match_date: date
    ) -> List[Dict[str, Any]]:
        """
        Busca matches de uma liga em uma data específica.

        Args:
            league_id: ID da liga
            match_date: Data dos matches

        Returns:
            Lista de matches com fixtures e odds
        """
        cache_key = f"fixtures:{league_id}:{match_date.isoformat()}"

        fixtures = self.cache.get(cache_key)

        if not fixtures:
            logger.warning(f"Nenhum fixture encontrado para {cache_key}")
            return []

        # Para cada fixture, busca as odds e mescla
        matches = []
        for fixture in fixtures:
            fixture_id = fixture["id"]

            # Busca odds do cache
            odds_cache_key = f"odds:{fixture_id}"
            odds = self.cache.get(odds_cache_key)

            # Adiciona odds ao fixture
            match = {
                **fixture,
                "odds": odds if odds else {}
            }

            matches.append(match)

        logger.info(f"✅ {len(matches)} matches encontrados para liga {league_id} em {match_date}")
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

        Args:
            fixture_id: ID do fixture

        Returns:
            Match completo ou None
        """
        # Busca odds do cache
        odds_cache_key = f"odds:{fixture_id}"
        odds = self.cache.get(odds_cache_key)

        # Tenta buscar fixture de todas as ligas e próximos dias até encontrar
        # (fixtures são cacheados por liga+data, não individualmente)
        league_ids = [71, 73, 39, 140, 78, 61, 135]
        today = date.today()

        fixture = None
        # Busca hoje até próximos 7 dias
        for day_offset in range(8):
            search_date = today
            if day_offset > 0:
                from datetime import timedelta
                search_date = today + timedelta(days=day_offset)

            for league_id in league_ids:
                cache_key = f"fixtures:{league_id}:{search_date.isoformat()}"
                fixtures = self.cache.get(cache_key)

                if fixtures:
                    # Procura o fixture na lista
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

        # Monta match completo com fixture + odds
        match_data = {
            "id": fixture_id,
            "home_team": fixture.get("home_team", {}),
            "away_team": fixture.get("away_team", {}),
            "league": fixture.get("league", {}),
            "date": fixture.get("date"),
            "odds": odds if odds else {}
        }

        return match_data

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

    def get_bookmakers(self) -> List[Dict[str, Any]]:
        """
        Retorna lista de casas de apostas disponíveis.

        Returns:
            Lista de bookmakers
        """
        return [
            {
                "id": "bet365",
                "name": "Bet365",
                "logo": "💰",
                "is_default": True
            },
            {
                "id": "betano",
                "name": "Betano",
                "logo": "💰",
                "is_default": False
            }
        ]

