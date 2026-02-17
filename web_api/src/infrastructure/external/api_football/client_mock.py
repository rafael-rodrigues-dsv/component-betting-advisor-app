"""
API-Football Client Mock - Client mockado com when/then.

Este client virtualiza completamente a API-Football sem fazer requests HTTP.
"""

import logging
from typing import Dict, Any
from datetime import date

from infrastructure.external.api_football.fixtures.scenarios import APIFootballScenarios
from infrastructure.external.api_football.results_mock import FixtureResultsMock
from domain.constants import (
    LEAGUE_BRASILEIRAO,
    LEAGUE_COPA_BRASIL,
    LEAGUE_PREMIER_LEAGUE,
    LEAGUE_LA_LIGA,
    LEAGUE_BUNDESLIGA,
    LEAGUE_LIGUE_1,
    LEAGUE_SERIE_A,
    LEAGUE_NAMES,
    LEAGUE_COUNTRIES
)

logger = logging.getLogger(__name__)


class APIFootballClientMock:
    """
    Client mockado da API-Football.

    Usa o padrão When/Then através do APIFootballScenarios
    para simular responses realistas sem chamadas HTTP.

    Exemplo:
        client = APIFootballClientMock()

        # WHEN: Busco fixtures do Brasileirão
        fixtures = await client.get_fixtures(league_id=71, date="2026-02-17")

        # THEN: Retorna fixtures mockados realistas
    """

    def __init__(self):
        logger.info("🎭 APIFootballClientMock inicializado (modo virtualizado)")

    async def get_fixtures(self, league_id: int, fixture_date: date) -> Dict[str, Any]:
        """
        WHEN: GET /fixtures?league={league_id}&date={date}
        THEN: Return fixtures mockados

        Args:
            league_id: ID da liga
            fixture_date: Data dos fixtures

        Returns:
            Response mockado no formato da API-Football
        """
        date_str = fixture_date.isoformat()
        logger.debug(f"📡 WHEN: GET /fixtures?league={league_id}&date={date_str}")

        response = APIFootballScenarios.when_get_fixtures(league_id, date_str)

        logger.debug(f"✅ THEN: Return {len(response.get('response', []))} fixtures")
        return response

    async def get_odds(self, fixture_id: int) -> Dict[str, Any]:
        """
        WHEN: GET /odds?fixture={fixture_id}
        THEN: Return odds mockadas

        Args:
            fixture_id: ID do fixture

        Returns:
            Response mockado no formato da API-Football
        """
        logger.debug(f"📡 WHEN: GET /odds?fixture={fixture_id}")

        response = APIFootballScenarios.when_get_odds(fixture_id)

        logger.debug(f"✅ THEN: Return odds mockadas")
        return response

    async def get_leagues(self) -> Dict[str, Any]:
        """
        WHEN: GET /leagues
        THEN: Return ligas disponíveis

        Returns:
            Response mockado com ligas
        """
        logger.debug(f"📡 WHEN: GET /leagues")

        # Lista de ligas mockadas (usando constantes)
        leagues = [
            {"id": LEAGUE_BRASILEIRAO, "name": LEAGUE_NAMES[LEAGUE_BRASILEIRAO], "country": LEAGUE_COUNTRIES[LEAGUE_BRASILEIRAO]},
            {"id": LEAGUE_COPA_BRASIL, "name": LEAGUE_NAMES[LEAGUE_COPA_BRASIL], "country": LEAGUE_COUNTRIES[LEAGUE_COPA_BRASIL]},
            {"id": LEAGUE_PREMIER_LEAGUE, "name": LEAGUE_NAMES[LEAGUE_PREMIER_LEAGUE], "country": LEAGUE_COUNTRIES[LEAGUE_PREMIER_LEAGUE]},
            {"id": LEAGUE_LA_LIGA, "name": LEAGUE_NAMES[LEAGUE_LA_LIGA], "country": LEAGUE_COUNTRIES[LEAGUE_LA_LIGA]},
            {"id": LEAGUE_BUNDESLIGA, "name": LEAGUE_NAMES[LEAGUE_BUNDESLIGA], "country": LEAGUE_COUNTRIES[LEAGUE_BUNDESLIGA]},
            {"id": LEAGUE_LIGUE_1, "name": LEAGUE_NAMES[LEAGUE_LIGUE_1], "country": LEAGUE_COUNTRIES[LEAGUE_LIGUE_1]},
            {"id": LEAGUE_SERIE_A, "name": LEAGUE_NAMES[LEAGUE_SERIE_A], "country": LEAGUE_COUNTRIES[LEAGUE_SERIE_A]}
        ]

        logger.debug(f"✅ THEN: Return {len(leagues)} ligas")

        return {"response": leagues}

    async def get_fixture_result(self, fixture_id: str) -> Dict[str, Any]:
        """
        WHEN: GET /fixtures?id={fixture_id}
        THEN: Return resultado da partida mockado

        Args:
            fixture_id: ID do fixture

        Returns:
            Response mockado com resultado da partida
        """
        logger.debug(f"📡 WHEN: GET /fixtures?id={fixture_id}")

        # Usa o mock de resultados
        result = FixtureResultsMock.get_fixture_result(fixture_id)

        if result:
            logger.debug(f"✅ THEN: Return resultado mockado (status: {result.get('fixture', {}).get('status', {}).get('short')})")
            return {"response": [result]}
        else:
            logger.debug(f"⚠️ THEN: Fixture não encontrado")
            return {"response": []}

