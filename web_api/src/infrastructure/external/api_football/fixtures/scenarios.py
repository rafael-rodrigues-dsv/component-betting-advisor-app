"""
API-Football Scenarios - When/Then para virtualização de chamadas.

Este módulo implementa o padrão When/Then para mockar respostas da API-Football.

Exemplo:
    WHEN: GET /fixtures?league=71&date=2026-02-17
    THEN: Return fixtures do Brasileirão para essa data
"""

import json
import random
from pathlib import Path
from datetime import datetime, time, date
from typing import Dict, List, Any, Optional

from domain.constants import (
    LEAGUE_FIXTURE_FILES,
    BOOKMAKER_BET365_ID,
    BOOKMAKER_BET365_NAME,
    BOOKMAKER_BETANO_ID,
    BOOKMAKER_BETANO_NAME
)

# Caminho base dos fixtures
FIXTURES_PATH = Path(__file__).parent


class APIFootballScenarios:
    """
    Gerenciador de cenários mockados da API-Football.

    Implementa padrão When/Then para virtualização de chamadas HTTP.
    """

    # Cache de fixtures carregados
    _league_configs: Dict[int, dict] = {}

    @classmethod
    def load_league_config(cls, league_id: int) -> Optional[dict]:
        """Carrega configuração de uma liga"""
        if league_id in cls._league_configs:
            return cls._league_configs[league_id]

        # Usa mapeamento de constantes
        filename = LEAGUE_FIXTURE_FILES.get(league_id)
        if not filename:
            return None

        file_path = FIXTURES_PATH / "leagues" / filename
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            config = json.load(f)
            cls._league_configs[league_id] = config
            return config

    @classmethod
    def when_get_fixtures(cls, league_id: int, fixture_date: str) -> Dict[str, Any]:
        """
        WHEN: GET /fixtures?league={league_id}&date={date}
        THEN: Return fixtures mockados para essa liga e data

        Args:
            league_id: ID da liga (71=Brasileirão, 39=Premier, etc)
            fixture_date: Data no formato ISO (YYYY-MM-DD)

        Returns:
            Response mockado da API-Football
        """
        league_config = cls.load_league_config(league_id)

        if not league_config:
            return {"response": []}

        # Determina número de jogos baseado no dia da semana
        date_obj = date.fromisoformat(fixture_date)
        weekday = date_obj.weekday()  # 0=Monday, 6=Sunday

        weekday_names = {
            0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
            4: "friday", 5: "saturday", 6: "sunday"
        }

        day_name = weekday_names[weekday]
        match_days = league_config.get("match_days", {})
        num_matches = match_days.get(day_name, 0)

        if num_matches == 0:
            return {"response": []}

        # Gera fixtures mockados
        fixtures = cls._generate_fixtures(
            league_config=league_config,
            fixture_date=date_obj,
            num_matches=num_matches
        )

        return {
            "get": "fixtures",
            "parameters": {"league": str(league_id), "date": fixture_date},
            "errors": [],
            "results": len(fixtures),
            "response": fixtures
        }

    @classmethod
    def when_get_odds(cls, fixture_id: int) -> Dict[str, Any]:
        """
        WHEN: GET /odds?fixture={fixture_id}
        THEN: Return odds mockadas para esse fixture

        Args:
            fixture_id: ID do fixture

        Returns:
            Response mockado com odds
        """
        # Usa fixture_id como seed para consistência
        random.seed(fixture_id)

        # Carrega templates de odds
        bet365_template = cls._load_odds_template("bet365_template.json")
        betano_template = cls._load_odds_template("betano_template.json")

        # Gera odds baseadas nos templates
        odds_data = {
            "fixture": {"id": fixture_id},
            "bookmakers": [
                cls._generate_odds_from_template(bet365_template, BOOKMAKER_BET365_NAME, BOOKMAKER_BET365_ID),
                cls._generate_odds_from_template(betano_template, BOOKMAKER_BETANO_NAME, BOOKMAKER_BETANO_ID)
            ]
        }

        return {"response": [odds_data]}

    @classmethod
    def _generate_fixtures(
        cls,
        league_config: dict,
        fixture_date: date,
        num_matches: int
    ) -> List[Dict[str, Any]]:
        """Gera fixtures mockados para uma data"""
        teams = league_config["teams"]
        typical_hours = league_config.get("typical_hours", [16, 18, 19, 20, 21])

        # Embaralha times
        random.seed(int(fixture_date.strftime("%Y%m%d")))
        shuffled_teams = random.sample(teams, min(num_matches * 2, len(teams)))

        fixtures = []
        for i in range(num_matches):
            if i * 2 + 1 >= len(shuffled_teams):
                break

            home_team = shuffled_teams[i * 2]
            away_team = shuffled_teams[i * 2 + 1]

            # Gera horário
            hour = random.choice(typical_hours)
            minute = random.choice([0, 30])
            fixture_datetime = datetime.combine(fixture_date, time(hour, minute))

            # Gera ID único
            fixture_id = int(f"{league_config['id']}{fixture_date.strftime('%Y%m%d')}{i:02d}")

            # Timestamp como string de data (YYYY-MM-DD)
            timestamp_str = fixture_date.strftime('%Y-%m-%d')

            fixture = {
                "fixture": {
                    "id": fixture_id,
                    "referee": None,
                    "timezone": "UTC",
                    "date": fixture_datetime.isoformat() + "Z",
                    "timestamp": timestamp_str,
                    "periods": {"first": None, "second": None},
                    "venue": {
                        "id": None,
                        "name": f"Stadium {home_team['name']}",
                        "city": league_config["country"]
                    },
                    "status": {"long": "Not Started", "short": "NS", "elapsed": None}
                },
                "league": {
                    "id": league_config["id"],
                    "name": league_config["name"],
                    "country": league_config["country"],
                    "logo": f"https://media.api-sports.io/football/leagues/{league_config['id']}.png",
                    "flag": None,
                    "season": 2026,
                    "round": f"Regular Season - {i + 1}"
                },
                "teams": {
                    "home": {
                        "id": home_team["id"],
                        "name": home_team["name"],
                        "logo": f"https://media.api-sports.io/football/teams/{home_team['id']}.png",
                        "winner": None
                    },
                    "away": {
                        "id": away_team["id"],
                        "name": away_team["name"],
                        "logo": f"https://media.api-sports.io/football/teams/{away_team['id']}.png",
                        "winner": None
                    }
                },
                "goals": {"home": None, "away": None},
                "score": {
                    "halftime": {"home": None, "away": None},
                    "fulltime": {"home": None, "away": None},
                    "extratime": {"home": None, "away": None},
                    "penalty": {"home": None, "away": None}
                }
            }
            fixtures.append(fixture)

        return fixtures

    @classmethod
    def _load_odds_template(cls, filename: str) -> dict:
        """Carrega template de odds"""
        file_path = FIXTURES_PATH / "odds" / filename

        if not file_path.exists():
            # Template padrão se não existir
            return {
                "bookmaker": "Unknown",
                "id": 0,
                "odds_ranges": {
                    "home": [1.80, 2.50],
                    "draw": [3.00, 3.80],
                    "away": [2.20, 4.50],
                    "over_25": [1.70, 2.20],
                    "under_25": [1.65, 2.10],
                    "btts_yes": [1.75, 2.30],
                    "btts_no": [1.55, 1.95]
                }
            }

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)

    @classmethod
    def _generate_odds_from_template(
        cls,
        template: dict,
        bookmaker_name: str,
        bookmaker_id: int
    ) -> Dict[str, Any]:
        """Gera odds a partir de um template"""
        ranges = template["odds_ranges"]

        # Gera valores dentro dos ranges
        home = round(random.uniform(*ranges["home"]), 2)
        draw = round(random.uniform(*ranges["draw"]), 2)
        away = round(random.uniform(*ranges["away"]), 2)
        over_25 = round(random.uniform(*ranges["over_25"]), 2)
        under_25 = round(random.uniform(*ranges["under_25"]), 2)
        btts_yes = round(random.uniform(*ranges["btts_yes"]), 2)
        btts_no = round(random.uniform(*ranges["btts_no"]), 2)

        return {
            "id": bookmaker_id,
            "name": bookmaker_name,
            "bets": [
                {
                    "id": 1,
                    "name": "Match Winner",
                    "values": [
                        {"value": "Home", "odd": str(home)},
                        {"value": "Draw", "odd": str(draw)},
                        {"value": "Away", "odd": str(away)}
                    ]
                },
                {
                    "id": 5,
                    "name": "Goals Over/Under",
                    "values": [
                        {"value": "Over 2.5", "odd": str(over_25)},
                        {"value": "Under 2.5", "odd": str(under_25)}
                    ]
                },
                {
                    "id": 8,
                    "name": "Both Teams Score",
                    "values": [
                        {"value": "Yes", "odd": str(btts_yes)},
                        {"value": "No", "odd": str(btts_no)}
                    ]
                }
            ]
        }

