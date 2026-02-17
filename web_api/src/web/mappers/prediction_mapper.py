"""
Prediction Mapper - Converte dados para DTOs de prediction
"""
from typing import List, Dict, Any
import random
import uuid
from datetime import datetime

from web.dtos.responses.prediction_response import (
    PredictionResponse,
    MarketPredictionResponse,
    MarketEnum,
    RecommendationEnum,
    AnalyzePredictionsResponse
)


def get_recommendation(ev: float, confidence: float) -> RecommendationEnum:
    """
    Retorna recomendação baseada no EV e confiança.

    Args:
        ev: Expected Value (valor esperado)
        confidence: Confiança na previsão (0-1)

    Returns:
        RecommendationEnum
    """
    if ev > 0.10 and confidence > 0.60:
        return RecommendationEnum.STRONG_BET
    elif ev > 0.05 and confidence > 0.50:
        return RecommendationEnum.RECOMMENDED
    elif ev > 0:
        return RecommendationEnum.CONSIDER
    else:
        return RecommendationEnum.AVOID


def sort_predictions_by_strategy(
    predictions: List[MarketPredictionResponse],
    strategy: str
) -> List[MarketPredictionResponse]:
    """
    Ordena previsões de acordo com a estratégia escolhida.

    Args:
        predictions: Lista de previsões de mercado
        strategy: Estratégia (CONSERVATIVE, BALANCED, VALUE_BET, AGGRESSIVE)

    Returns:
        Lista ordenada de previsões
    """
    if strategy == "CONSERVATIVE":
        return sorted(predictions, key=lambda x: x.confidence, reverse=True)
    elif strategy == "VALUE_BET":
        return sorted(predictions, key=lambda x: x.expected_value, reverse=True)
    elif strategy == "AGGRESSIVE":
        return sorted(predictions, key=lambda x: x.odds * x.confidence, reverse=True)
    else:  # BALANCED
        return sorted(
            predictions,
            key=lambda x: (x.expected_value * 0.5) + (x.confidence * 0.5),
            reverse=True
        )


def generate_mock_prediction(match_data: Dict[str, Any], strategy: str) -> PredictionResponse:
    """
    Gera previsão mockada a partir dos dados do match.

    Args:
        match_data: Dados do match (pode vir do cache ou service)
        strategy: Estratégia de análise

    Returns:
        PredictionResponse com previsões mockadas
    """
    match_id = match_data.get("id", str(uuid.uuid4()))
    home = match_data.get("home_team", {}).get("name", "Time Casa")
    away = match_data.get("away_team", {}).get("name", "Time Fora")
    league = match_data.get("league", {}).get("name", "Liga")
    date = match_data.get("date", datetime.now().isoformat())

    # Busca odds reais se existirem, senão usa mock
    odds_data = match_data.get("odds", {})
    bookmaker = odds_data.get("bet365", {}) if odds_data else {}

    home_odds = bookmaker.get("home", round(random.uniform(1.5, 3.0), 2))
    draw_odds = bookmaker.get("draw", round(random.uniform(3.0, 4.0), 2))
    away_odds = bookmaker.get("away", round(random.uniform(2.0, 3.5), 2))
    over_odds = bookmaker.get("over_25", round(random.uniform(1.7, 2.2), 2))
    under_odds = bookmaker.get("under_25", round(random.uniform(1.7, 2.2), 2))
    btts_yes_odds = bookmaker.get("btts_yes", round(random.uniform(1.7, 2.0), 2))
    btts_no_odds = bookmaker.get("btts_no", round(random.uniform(1.7, 2.0), 2))

    # Probabilidades mockadas (em produção viria do modelo de ML)
    home_prob = random.uniform(0.35, 0.55)
    draw_prob = random.uniform(0.20, 0.30)
    away_prob = 1 - home_prob - draw_prob

    predictions = []

    # 1X2 - Match Winner
    best = max([
        ("HOME", home_prob, home_odds),
        ("DRAW", draw_prob, draw_odds),
        ("AWAY", away_prob, away_odds)
    ], key=lambda x: (x[1] * x[2]) - 1)

    ev = (best[1] * best[2]) - 1
    predictions.append(MarketPredictionResponse(
        market=MarketEnum.MATCH_WINNER,
        predicted_outcome=best[0],
        confidence=round(best[1], 2),
        odds=best[2],
        expected_value=round(ev, 3),
        recommendation=get_recommendation(ev, best[1])
    ))

    # Over/Under 2.5
    over_prob = random.uniform(0.45, 0.65)
    under_prob = 1 - over_prob
    use_over = over_prob > under_prob
    selected_prob = over_prob if use_over else under_prob
    selected_odds = over_odds if use_over else under_odds

    ev_over = (selected_prob * selected_odds) - 1
    predictions.append(MarketPredictionResponse(
        market=MarketEnum.OVER_UNDER,
        predicted_outcome="OVER" if use_over else "UNDER",
        confidence=round(selected_prob, 2),
        odds=selected_odds,
        expected_value=round(ev_over, 3),
        recommendation=get_recommendation(ev_over, selected_prob)
    ))

    # BTTS (Both Teams To Score)
    btts_yes_prob = random.uniform(0.45, 0.60)
    btts_no_prob = 1 - btts_yes_prob
    use_yes = btts_yes_prob > btts_no_prob
    selected_btts_prob = btts_yes_prob if use_yes else btts_no_prob
    selected_btts_odds = btts_yes_odds if use_yes else btts_no_odds

    ev_btts = (selected_btts_prob * selected_btts_odds) - 1
    predictions.append(MarketPredictionResponse(
        market=MarketEnum.BTTS,
        predicted_outcome="YES" if use_yes else "NO",
        confidence=round(selected_btts_prob, 2),
        odds=selected_btts_odds,
        expected_value=round(ev_btts, 3),
        recommendation=get_recommendation(ev_btts, selected_btts_prob)
    ))

    # Ordena previsões pela estratégia
    predictions = sort_predictions_by_strategy(predictions, strategy)

    return PredictionResponse(
        id=str(uuid.uuid4()),
        match_id=match_id,
        home_team=home,
        away_team=away,
        league=league,
        date=date,
        predictions=predictions,
        strategy_used=strategy
    )


def create_pre_ticket(predictions: List[PredictionResponse], strategy: str) -> Dict[str, Any]:
    """
    Cria pré-bilhete automaticamente com a melhor aposta de cada jogo.

    Args:
        predictions: Lista de previsões
        strategy: Estratégia utilizada

    Returns:
        Dicionário com dados do pré-bilhete
    """
    pre_ticket_bets = []

    for prediction in predictions:
        if prediction.predictions:
            # Pega a primeira aposta (já vem ordenada pela estratégia)
            best_market = prediction.predictions[0]
            pre_ticket_bets.append({
                "match_id": prediction.match_id,
                "home_team": prediction.home_team,
                "away_team": prediction.away_team,
                "league": prediction.league,
                "market": best_market.market.value,
                "predicted_outcome": best_market.predicted_outcome,
                "odds": best_market.odds,
                "confidence": best_market.confidence
            })

    # Calcula odd combinada
    combined_odds = 1.0
    for bet in pre_ticket_bets:
        combined_odds *= bet["odds"]

    return {
        "bets": pre_ticket_bets,
        "total_bets": len(pre_ticket_bets),
        "combined_odds": round(combined_odds, 2),
        "message": f"Pré-bilhete montado com {len(pre_ticket_bets)} apostas baseado na estratégia {strategy}"
    }

