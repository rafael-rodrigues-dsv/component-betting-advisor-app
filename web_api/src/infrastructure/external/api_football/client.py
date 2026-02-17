"""
API-Football HTTP Client

Cliente HTTP para comunicação com a API-Football.
Suporta modo MOCK (virtualizado) e HTTP (real).
"""

from datetime import date
from typing import Dict, Any, Literal
import httpx
import logging

from infrastructure.external.api_football.client_mock import APIFootballClientMock

logger = logging.getLogger(__name__)


class APIFootballClient:
    """
    Cliente HTTP para API-Football.
    
    Suporta dois modos:
    - MOCK: Virtualizado com when/then (sem requests HTTP)
    - HTTP: Chamadas diretas à API-Football

    Exemplo:
        # Modo Mock (padrão)
        client = APIFootballClient(mode="mock")

        # Modo HTTP
        client = APIFootballClient(mode="http", api_key="sua_chave")
    """

    def __init__(
        self,
        mode: Literal["mock", "http"] = "mock",
        api_key: str = None,
        base_url: str = "https://v3.football.api-sports.io"
    ):
        """
        Inicializa o client.

        Args:
            mode: "mock" (virtualizado) ou "http" (API real)
            api_key: Chave da API (obrigatório para modo http)
            base_url: URL base da API
        """
        self.mode = mode
        self.api_key = api_key
        self.base_url = base_url

        if mode == "mock":
            # Usa client mockado (when/then)
            self.mock_client = APIFootballClientMock()
            logger.info("🎭 APIFootballClient inicializado (MOCK mode)")
        else:
            # Modo HTTP direto
            if not api_key:
                raise ValueError("API key é obrigatória para modo 'http'")
            self.mock_client = None
            logger.info("🌐 APIFootballClient inicializado (HTTP mode)")

    async def get(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        """
        GET request (mock ou HTTP baseado no modo).

        Args:
            endpoint: Endpoint da API (/fixtures, /odds, etc)
            params: Query parameters

        Returns:
            Response da API (mockado ou HTTP)
        """
        params = params or {}

        if self.mode == "mock":
            # Delega para client mockado
            return await self._get_mock(endpoint, params)
        else:
            # Request HTTP direto
            return await self._get_http(endpoint, params)

    async def _get_mock(self, endpoint: str, params: dict) -> Dict[str, Any]:
        """GET mockado (virtualizado com when/then)"""
        if endpoint == "/fixtures":
            # Se tem ID, busca fixture específico (resultado)
            if "id" in params:
                fixture_id = params.get("id")
                return await self.mock_client.get_fixture_result(fixture_id)

            # Senão, busca fixtures por liga/data
            league_id = int(params.get("league", 71))
            date_str = params.get("date", date.today().isoformat())
            fixture_date = date.fromisoformat(date_str)

            return await self.mock_client.get_fixtures(league_id, fixture_date)

        elif endpoint == "/odds":
            fixture_id = int(params.get("fixture", 0))
            return await self.mock_client.get_odds(fixture_id)

        elif endpoint == "/leagues":
            return await self.mock_client.get_leagues()

        else:
            logger.warning(f"Endpoint não suportado em modo mock: {endpoint}")
            return {"response": []}

    async def _get_http(self, endpoint: str, params: dict) -> Dict[str, Any]:
        """GET via HTTP direto à API-Football"""
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

