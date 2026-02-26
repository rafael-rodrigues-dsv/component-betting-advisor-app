"""
API-Football HTTP Client

Cliente HTTP para comunicação com a API-Football.
Suporta paginação automática para endpoints que retornam múltiplas páginas.
"""

from typing import Dict, Any, List
import httpx
import logging

logger = logging.getLogger(__name__)


class APIFootballClient:
    """
    Cliente HTTP para API-Football.

    Faz chamadas diretas à API-Football via HTTP.
    Suporta paginação automática (endpoint /odds retorna max 10 por página).
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://v3.football.api-sports.io"
    ):
        if not api_key:
            raise ValueError("API key é obrigatória para API-Football")

        self.api_key = api_key
        self.base_url = base_url
        logger.info("🌐 APIFootballClient inicializado")

    async def get(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        """
        GET request à API-Football (sem paginação — retorna 1ª página).

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

    async def get_all_pages(self, endpoint: str, params: dict = None) -> Dict[str, Any]:
        """
        GET request com paginação automática.

        A API-Football retorna max ~10 items por página para /odds.
        Este método itera por todas as páginas e concatena os responses.

        Args:
            endpoint: Endpoint da API
            params: Query parameters

        Returns:
            Response JSON com TODOS os items (response[] concatenado)
        """
        params = params or {}
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }

        url = f"{self.base_url}{endpoint}"
        all_responses: List[Any] = []
        current_page = 1

        async with httpx.AsyncClient() as client:
            while True:
                page_params = {**params, "page": current_page}

                response = await client.get(
                    url,
                    headers=headers,
                    params=page_params,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()

                # Acumula responses
                page_items = data.get("response", [])
                all_responses.extend(page_items)

                # Verifica paginação
                paging = data.get("paging", {})
                total_pages = paging.get("total", 1)
                current = paging.get("current", 1)

                logger.debug(f"📄 Página {current}/{total_pages} — {len(page_items)} items")

                if current >= total_pages:
                    break

                current_page += 1

        logger.info(f"📄 Paginação completa: {current_page} páginas, {len(all_responses)} items total")

        # Retorna no mesmo formato da API, mas com TODOS os items
        return {
            "response": all_responses,
            "paging": {"current": current_page, "total": current_page},
            "results": len(all_responses),
        }

