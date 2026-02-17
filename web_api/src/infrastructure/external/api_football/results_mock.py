"""
Mock de resultados de jogos da API Football.

Simula a API que retorna os resultados finais das partidas.
Na API real seria algo como: GET /fixtures?id={fixture_id}&status=FT (Full Time)

SISTEMA DE SIMULAÇÃO AUTOMÁTICA:
- Resultados são gerados aleatoriamente na primeira consulta
- Após X segundos, a partida "termina" e o resultado é fixado
- Simula o ciclo de vida real de uma partida
"""
import random
import time
from typing import Dict, Any, Optional


# Cache global de resultados gerados (simula partidas ao longo do tempo)
_results_cache: Dict[str, Dict[str, Any]] = {}
_results_timestamp: Dict[str, float] = {}

# Tempo em segundos para uma partida "terminar" (0 = instantâneo para testes)
MATCH_DURATION_SECONDS = 0


class FixtureResultsMock:
    """
    Mock dos resultados de fixtures (partidas finalizadas).

    Simula a consulta à API Football para obter o placar final de uma partida.
    Na API real: GET /fixtures?id={fixture_id}
    """

    @staticmethod
    def get_fixture_result(fixture_id: str) -> Optional[Dict[str, Any]]:
        """
        Retorna resultado mockado de uma partida com simulação temporal.

        Na primeira consulta:
        - Gera resultado aleatório e salva no cache
        - Marca timestamp de criação
        - Retorna status "FT" se MATCH_DURATION = 0, senão "NS"

        Após MATCH_DURATION_SECONDS:
        - Retorna mesmo resultado mas com status "Match Finished"
        - Placar é o mesmo gerado inicialmente

        Args:
            fixture_id: ID da partida

        Returns:
            Dicionário com resultado da partida no formato da API Football
        """
        current_time = time.time()

        # Verifica se já existe resultado cacheado para esta partida
        if fixture_id in _results_cache:
            cached_result = _results_cache[fixture_id]
            creation_time = _results_timestamp[fixture_id]
            elapsed_seconds = current_time - creation_time

            # Se MATCH_DURATION = 0, sempre retorna FT (instantâneo)
            if MATCH_DURATION_SECONDS == 0:
                cached_result["fixture"]["status"] = {
                    "long": "Match Finished",
                    "short": "FT",
                    "elapsed": 90
                }
                return cached_result

            # Se passou mais que MATCH_DURATION_SECONDS, partida terminou
            if elapsed_seconds >= MATCH_DURATION_SECONDS:
                cached_result["fixture"]["status"] = {
                    "long": "Match Finished",
                    "short": "FT",
                    "elapsed": 90
                }
            else:
                # Ainda em andamento
                cached_result["fixture"]["status"] = {
                    "long": "Not Started",
                    "short": "NS"
                }

            return cached_result

        # Primeira consulta: gera e cacheia resultado
        home_goals = random.randint(0, 4)
        away_goals = random.randint(0, 4)

        # Se MATCH_DURATION = 0, já começa finalizada
        initial_status = {
            "long": "Match Finished" if MATCH_DURATION_SECONDS == 0 else "Not Started",
            "short": "FT" if MATCH_DURATION_SECONDS == 0 else "NS"
        }
        if MATCH_DURATION_SECONDS == 0:
            initial_status["elapsed"] = 90

        result = {
            "fixture": {
                "id": fixture_id,
                "status": initial_status
            },
            "goals": {
                "home": home_goals,
                "away": away_goals
            },
            "score": {
                "halftime": {
                    "home": home_goals // 2 if home_goals > 0 else 0,
                    "away": away_goals // 2 if away_goals > 0 else 0
                },
                "fulltime": {
                    "home": home_goals,
                    "away": away_goals
                }
            }
        }

        # Salva no cache com timestamp
        _results_cache[fixture_id] = result
        _results_timestamp[fixture_id] = current_time

        return result

    @staticmethod
    def determine_bet_result(
        fixture_result: Dict[str, Any],
        market: str,
        predicted_outcome: str
    ) -> str:
        """
        Determina se uma aposta ganhou ou perdeu baseado no resultado da partida.

        Args:
            fixture_result: Resultado da partida da API
            market: Mercado da aposta (MATCH_WINNER, OVER_UNDER, BOTH_TEAMS_SCORE)
            predicted_outcome: Resultado previsto

        Returns:
            "WON", "LOST" ou "PENDING"
        """
        # Se partida não terminou
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
        elif market == "BOTH_TEAMS_SCORE" or market == "BTTS":
            both_scored = home_goals > 0 and away_goals > 0
            if predicted_outcome == "YES":
                return "WON" if both_scored else "LOST"
            elif predicted_outcome == "NO":
                return "WON" if not both_scored else "LOST"

        # Se não conseguiu determinar
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

    @staticmethod
    def clear_cache():
        """
        Limpa o cache de resultados.

        Útil para testes ou para resetar o sistema de simulação.
        """
        global _results_cache, _results_timestamp
        _results_cache.clear()
        _results_timestamp.clear()

    @staticmethod
    def get_match_elapsed_time(fixture_id: str) -> Optional[float]:
        """
        Retorna quanto tempo passou desde que a partida foi consultada pela primeira vez.

        Args:
            fixture_id: ID da partida

        Returns:
            Segundos decorridos ou None se partida nunca foi consultada
        """
        if fixture_id not in _results_timestamp:
            return None

        current_time = time.time()
        creation_time = _results_timestamp[fixture_id]
        return current_time - creation_time

