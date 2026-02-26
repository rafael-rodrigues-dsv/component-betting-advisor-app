"""
Fixture Parser - Parseia response da API-Football /fixtures
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class FixtureParser:
    """Parser para fixtures da API-Football"""

    @staticmethod
    def parse(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parseia response da API-Football /fixtures.

        Transforma JSON da API para formato simplificado.
        """
        fixtures = api_response.get("response", [])
        parsed_fixtures = []

        for fixture in fixtures:
            try:
                parsed = FixtureParser._parse_single(fixture)
                parsed_fixtures.append(parsed)
            except Exception as e:
                logger.error(f"Erro ao parsear fixture: {e}")
                continue

        logger.info(f"✅ {len(parsed_fixtures)} fixtures parseados")
        return parsed_fixtures

    @staticmethod
    def _parse_single(fixture: Dict[str, Any]) -> Dict[str, Any]:
        """Parseia um único fixture"""
        fixture_data = fixture.get("fixture", {})
        teams_data = fixture.get("teams", {})
        league_data = fixture.get("league", {})

        # Mapeia logos
        home_logo = FixtureParser._map_logo(teams_data.get("home", {}).get("name", ""),
                                           teams_data.get("home", {}).get("logo", ""))
        away_logo = FixtureParser._map_logo(teams_data.get("away", {}).get("name", ""),
                                           teams_data.get("away", {}).get("logo", ""))

        # Timestamp: API retorna Unix timestamp (int), converte para YYYY-MM-DD
        raw_timestamp = fixture_data.get("timestamp")
        if isinstance(raw_timestamp, int):
            timestamp_str = datetime.fromtimestamp(raw_timestamp, tz=timezone.utc).strftime("%Y-%m-%d")
        elif isinstance(raw_timestamp, str):
            timestamp_str = raw_timestamp[:10]  # Pega só YYYY-MM-DD
        else:
            # Fallback: extrai da date
            date_str = fixture_data.get("date", "")
            timestamp_str = date_str[:10] if date_str else ""

        return {
            "id": str(fixture_data.get("id") or ""),
            "date": fixture_data.get("date") or "",
            "timestamp": timestamp_str,
            "status": (fixture_data.get("status") or {}).get("long") or "Not Started",
            "league": {
                "id": str(league_data.get("id") or ""),
                "name": league_data.get("name") or "",
                "country": league_data.get("country") or "",
                "logo": league_data.get("logo") or "",
                "type": "league"
            },
            "home_team": {
                "id": str((teams_data.get("home") or {}).get("id") or ""),
                "name": (teams_data.get("home") or {}).get("name") or "",
                "logo": home_logo
            },
            "away_team": {
                "id": str((teams_data.get("away") or {}).get("id") or ""),
                "name": (teams_data.get("away") or {}).get("name") or "",
                "logo": away_logo
            },
            "round": {
                "type": "round",
                "name": league_data.get("round") or ""
            },
            "venue": {
                "name": (fixture_data.get("venue") or {}).get("name") or "",
                "city": (fixture_data.get("venue") or {}).get("city") or ""
            }
        }

    @staticmethod
    def _map_logo(team_name: str, api_url: str) -> Dict[str, str]:
        """Mapeia logo para escudo local se disponível"""
        team_logo_map = {
            "Flamengo": "flamengo.png", "Palmeiras": "palmeiras.png", "São Paulo": "sao-paulo.png",
            "Corinthians": "corinthians.png", "Atlético-MG": "atletico-mineiro.png",
            "Fluminense": "fluminense.png", "Internacional": "internacional.png", "Grêmio": "gremio.png",
            "Botafogo": "botafogo.png", "Santos": "santos.png", "Cruzeiro": "cruzeiro.png",
            "Vasco": "vasco.png", "Manchester City": "manchester-city.png", "Arsenal": "arsenal.png",
            "Liverpool": "liverpool.png", "Manchester United": "manchester-united.png",
            "Newcastle": "newcastle.png", "Tottenham": "tottenham.png", "Chelsea": "chelsea.png",
            "Brighton": "brighton.png", "Aston Villa": "aston-villa.png", "West Ham": "west-ham.png",
            "Wolves": "wolverhampton.png",
        }

        local_logo = team_logo_map.get(team_name)
        if local_logo:
            return {"url": f"http://localhost:8000/static/escudos/{local_logo}", "type": "LOCAL"}
        else:
            return {"url": api_url, "type": "EXT"}

