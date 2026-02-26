"""
Odds Parser - Parseia response da API-Football /odds

Suporta dois modos:
- parse(): Single fixture (GET /odds?fixture={id})
- parse_bulk(): Todas as odds de uma data (GET /odds?date={date})
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class OddsParser:
    """Parser para odds da API-Football"""

    @staticmethod
    def parse(api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parseia response da API-Football /odds para um único fixture.

        Transforma de formato API para formato frontend:
        {
          "bet365": {"home": 2.10, "draw": 3.20, ...},
          "betano": {"home": 2.15, "draw": 3.25, ...}
        }
        """
        odds_data = api_response.get("response", [])

        if not odds_data:
            logger.warning("Nenhuma odd encontrada")
            return {}

        fixture_odds = odds_data[0]
        bookmakers = fixture_odds.get("bookmakers", [])

        parsed_odds = {}
        for bookmaker in bookmakers:
            bookmaker_name = bookmaker.get("name", "").lower().replace(" ", "").replace("-", "")
            bookmaker_odds = OddsParser._parse_bookmaker(bookmaker)

            if bookmaker_odds:
                parsed_odds[bookmaker_name] = bookmaker_odds

        logger.info(f"✅ Odds parseadas para {len(parsed_odds)} casas")
        return parsed_odds

    @staticmethod
    def parse_bulk(api_response: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Parseia response BULK da API-Football /odds?date={date}.

        Retorna dicionário fixture_id → odds_by_bookmaker.
        Cada fixture_id mapeia para {"bet365": {...}, "betano": {...}}.

        Args:
            api_response: JSON da API-Football /odds?date=...

        Returns:
            Dict[fixture_id_str, Dict[bookmaker_name, bookmaker_odds]]
        """
        odds_data = api_response.get("response", [])

        if not odds_data:
            logger.warning("Nenhuma odd encontrada no bulk")
            return {}

        result: Dict[str, Dict[str, Any]] = {}

        for fixture_entry in odds_data:
            fixture_info = fixture_entry.get("fixture", {})
            fixture_id = str(fixture_info.get("id", ""))

            if not fixture_id:
                continue

            bookmakers = fixture_entry.get("bookmakers", [])
            parsed_odds = {}

            for bookmaker in bookmakers:
                bookmaker_name = bookmaker.get("name", "").lower().replace(" ", "").replace("-", "")
                bookmaker_odds = OddsParser._parse_bookmaker(bookmaker)
                if bookmaker_odds:
                    parsed_odds[bookmaker_name] = bookmaker_odds

            if parsed_odds:
                result[fixture_id] = parsed_odds

        logger.info(f"✅ Odds bulk parseadas: {len(result)} fixtures com odds")
        return result

    @staticmethod
    def _parse_bookmaker(bookmaker: Dict[str, Any]) -> Dict[str, float]:
        """Parseia odds de uma casa"""
        odds = {}
        bets = bookmaker.get("bets", [])

        for bet in bets:
            bet_name = bet.get("name", "")
            values = bet.get("values", [])

            if bet_name == "Match Winner":
                for value in values:
                    bet_type = value.get("value", "").lower()
                    odd_value = float(value.get("odd", 0))
                    if bet_type == "home":
                        odds["home"] = odd_value
                    elif bet_type == "draw":
                        odds["draw"] = odd_value
                    elif bet_type == "away":
                        odds["away"] = odd_value

            elif bet_name == "Goals Over/Under":
                for value in values:
                    bet_type = value.get("value", "").lower()
                    odd_value = float(value.get("odd", 0))
                    if "over" in bet_type:
                        odds["over_25"] = odd_value
                    elif "under" in bet_type:
                        odds["under_25"] = odd_value

            elif bet_name == "Both Teams Score":
                for value in values:
                    bet_type = value.get("value", "").lower()
                    odd_value = float(value.get("odd", 0))
                    if bet_type == "yes":
                        odds["btts_yes"] = odd_value
                    elif bet_type == "no":
                        odds["btts_no"] = odd_value

        return odds

