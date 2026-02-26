"""
API-Football HTTP Client

Cliente HTTP para comunicação com a API-Football.
"""

from typing import Dict, Any
import httpx
import logging

logger = logging.getLogger(__name__)


class APIFootballClient:
    """
    Cliente HTTP para API-Football.

    Faz chamadas diretas à API-Football via HTTP.

    Exemplo:
        client = APIFootballClient(api_key="sua_chave")
        response = await client.get("/fixtures", {"league": 71, "date": "2026-02-25"})
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://v3.football.api-sports.io"
    ):
        """
        Inicializa o client.

        Args:
            api_key: Chave da API-Football (obrigatória)
            base_url: URL base da API
        """
        if not api_key:
            raise ValueError("API key é obrigatória para API-Football")

        self.api_key = api_key
        self.base_url = base_url
        logger.info("🌐 APIFootballClient inicializado")

    async def get(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        """
        GET request à API-Football.

        Args:
            endpoint: Endpoint da API (/fixtures, /odds, /leagues, etc)
            params: Query parameters

        Returns:
            Response JSON da API
        """
        params = params or {}
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

