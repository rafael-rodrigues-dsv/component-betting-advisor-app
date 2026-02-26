"""
Bet Result Service - Lógica de avaliação de resultados de apostas.

Determina se uma aposta ganhou ou perdeu baseado no resultado real da partida.
"""
from typing import Dict, Any


class BetResultService:
    """
    Serviço de domínio para avaliação de resultados de apostas.

    Responsável por:
    - Determinar resultado de uma aposta (WON/LOST/PENDING)
    - Formatar placares para exibição
    """

    @staticmethod
    def determine_bet_result(
        fixture_result: Dict[str, Any],
        market: str,
        predicted_outcome: str
    ) -> str:
        """
        Determina se uma aposta ganhou ou perdeu baseado no resultado da partida.

        Args:
            fixture_result: Resultado da partida da API Football
            market: Mercado da aposta (MATCH_WINNER, OVER_UNDER, BOTH_TEAMS_SCORE)
            predicted_outcome: Resultado previsto

        Returns:
            "WON", "LOST" ou "PENDING"
        """
        status = fixture_result.get("fixture", {}).get("status", {}).get("short")
        if status != "FT":
            return "PENDING"

        home_goals = fixture_result.get("goals", {}).get("home")
        away_goals = fixture_result.get("goals", {}).get("away")

        if home_goals is None or away_goals is None:
            return "PENDING"

        # Match Winner (1X2)
        if market == "MATCH_WINNER":
            if predicted_outcome == "HOME":
                return "WON" if home_goals > away_goals else "LOST"
            elif predicted_outcome == "DRAW":
                return "WON" if home_goals == away_goals else "LOST"
            elif predicted_outcome == "AWAY":
                return "WON" if away_goals > home_goals else "LOST"

        # Over/Under 2.5
        elif market == "OVER_UNDER":
            total_goals = home_goals + away_goals
            if predicted_outcome == "OVER":
                return "WON" if total_goals > 2.5 else "LOST"
            elif predicted_outcome == "UNDER":
                return "WON" if total_goals < 2.5 else "LOST"

        # Both Teams To Score (BTTS)
        elif market in ("BOTH_TEAMS_SCORE", "BTTS"):
            both_scored = home_goals > 0 and away_goals > 0
            if predicted_outcome == "YES":
                return "WON" if both_scored else "LOST"
            elif predicted_outcome == "NO":
                return "WON" if not both_scored else "LOST"

        return "PENDING"

    @staticmethod
    def format_score(home_goals: int, away_goals: int) -> str:
        """
        Formata placar para exibição.

        Args:
            home_goals: Gols do time da casa
            away_goals: Gols do time visitante

        Returns:
            String formatada (ex: "2 x 1")
        """
        return f"{home_goals} x {away_goals}"

