"""
Fixture Parser - Parseia response da API-Football /fixtures

Filtra partidas inconsistentes: status "NS" (não iniciado) cujo
horário já passou há mais de 3 horas são descartadas.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

# Partidas NS com horário passado há mais de X horas são descartadas
STALE_NS_THRESHOLD_HOURS = 3


class FixtureParser:
    """Parser para fixtures da API-Football"""

    @staticmethod
    def parse(api_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parseia response da API-Football /fixtures.

        Filtra partidas inconsistentes:
        - Status "NS" cujo horário já passou há mais de 3h → descartada
        - Partidas em andamento ou finalizadas → mantidas normalmente
        """
        fixtures = api_response.get("response", [])
        parsed_fixtures = []
        skipped = 0

        now = datetime.now(tz=settings.tz)
        stale_cutoff = now - timedelta(hours=STALE_NS_THRESHOLD_HOURS)

        for fixture in fixtures:
            try:
                # Verifica se é NS fantasma ANTES de parsear (mais eficiente)
                fixture_data = fixture.get("fixture", {})
                status_short = (fixture_data.get("status") or {}).get("short") or "NS"
                raw_timestamp = fixture_data.get("timestamp")

                if status_short in ("NS", "TBD") and isinstance(raw_timestamp, int):
                    fixture_dt = datetime.fromtimestamp(raw_timestamp, tz=settings.tz)
                    if fixture_dt < stale_cutoff:
                        skipped += 1
                        continue

                parsed = FixtureParser._parse_single(fixture)
                parsed_fixtures.append(parsed)
            except Exception as e:
                logger.error(f"Erro ao parsear fixture: {e}")
                continue

        if skipped > 0:
            logger.info(f"⚠️ {skipped} partidas NS descartadas (horário passado há +{STALE_NS_THRESHOLD_HOURS}h)")

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

        # Timestamp: API retorna Unix timestamp (int), converte para YYYY-MM-DD na timezone local
        raw_timestamp = fixture_data.get("timestamp")
        if isinstance(raw_timestamp, int):
            timestamp_str = datetime.fromtimestamp(raw_timestamp, tz=settings.tz).strftime("%Y-%m-%d")
        elif isinstance(raw_timestamp, str):
            timestamp_str = raw_timestamp[:10]  # Pega só YYYY-MM-DD
        else:
            # Fallback: extrai da date
            date_str = fixture_data.get("date", "")
            timestamp_str = date_str[:10] if date_str else ""

        # Converte date para timezone local para agrupamento correto no frontend
        raw_date = fixture_data.get("date") or ""
        if isinstance(raw_timestamp, int):
            # Converte timestamp Unix para datetime na timezone local
            local_dt = datetime.fromtimestamp(raw_timestamp, tz=settings.tz)
            local_date_str = local_dt.isoformat()
        else:
            local_date_str = raw_date

        # Goals (placar)
        goals_data = fixture.get("goals", {})

        # Elapsed (minuto do jogo)
        elapsed = (fixture_data.get("status") or {}).get("elapsed")

        return {
            "id": str(fixture_data.get("id") or ""),
            "date": local_date_str,
            "timestamp": timestamp_str,
            "status": (fixture_data.get("status") or {}).get("long") or "Not Started",
            "status_short": (fixture_data.get("status") or {}).get("short") or "NS",
            "elapsed": elapsed,
            "goals": {
                "home": goals_data.get("home"),
                "away": goals_data.get("away"),
            },
            "league": {
                "id": str(league_data.get("id") or ""),
                "name": league_data.get("name") or "",
                "country": league_data.get("country") or "",
                "logo": league_data.get("logo") or "",
                "season": league_data.get("season"),
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

