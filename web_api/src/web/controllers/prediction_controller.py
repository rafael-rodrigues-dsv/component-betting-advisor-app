"""
Prediction Controller - Análise e previsões (MOCK)
"""

from fastapi import APIRouter
from typing import List
from datetime import datetime
import random
import uuid
import asyncio

from web.dtos.requests.prediction_request import AnalyzeMatchesRequest
from web.dtos.responses.prediction_response import (
    AnalyzePredictionsResponse,
    PredictionResponse,
    PredictionDetailResponse,
    MarketPredictionResponse,
    MarketEnum,
    RecommendationEnum
)

# Importa cache de matches
from web.controllers.match_controller import MATCHES_CACHE

router = APIRouter()



def _get_recommendation(ev: float, confidence: float) -> str:
    """Retorna recomendação baseada no EV e confiança"""
    if ev > 0.10 and confidence > 0.60:
        return "STRONG_BET"
    elif ev > 0.05 and confidence > 0.50:
        return "RECOMMENDED"
    elif ev > 0:
        return "CONSIDER"
    else:
        return "AVOID"


def _sort_predictions(predictions: List[MarketPredictionResponse], strategy: str) -> List[MarketPredictionResponse]:
    if strategy == "CONSERVATIVE":
        return sorted(predictions, key=lambda x: x.confidence, reverse=True)
    elif strategy == "VALUE_BET":
        return sorted(predictions, key=lambda x: x.expected_value, reverse=True)
    elif strategy == "AGGRESSIVE":
        return sorted(predictions, key=lambda x: x.odds * x.confidence, reverse=True)
    else:  # BALANCED
        return sorted(predictions, key=lambda x: (x.expected_value * 0.5) + (x.confidence * 0.5), reverse=True)


def _generate_prediction(match_id: str, strategy: str) -> PredictionResponse:
    """Gera previsão mockada usando dados reais do match"""

    # Busca o match no cache
    match = MATCHES_CACHE.get(match_id)

    if not match:
        # Fallback caso o match não esteja no cache
        print(f"[WARNING] Match {match_id} não encontrado no cache!")
        home = "Time A"
        away = "Time B"
        league = "Liga Desconhecida"
        date = datetime.now().isoformat()
    else:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        league = match["league"]["name"]
        date = match["date"]

    # Probabilidades
    home_prob = random.uniform(0.35, 0.55)
    draw_prob = random.uniform(0.20, 0.30)
    away_prob = 1 - home_prob - draw_prob

    # Odds
    home_odds = round(random.uniform(1.5, 3.0), 2)
    draw_odds = round(random.uniform(3.0, 4.0), 2)
    away_odds = round(random.uniform(2.0, 3.5), 2)
    over_odds = round(random.uniform(1.7, 2.2), 2)
    btts_odds = round(random.uniform(1.7, 2.0), 2)

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
        recommendation=RecommendationEnum(_get_recommendation(ev, best[1]))
    ))

    # Over/Under 2.5
    over_prob = random.uniform(0.45, 0.65)
    ev_over = (over_prob * over_odds) - 1
    predictions.append(MarketPredictionResponse(
        market=MarketEnum.OVER_UNDER,
        predicted_outcome="OVER" if over_prob > 0.5 else "UNDER",
        confidence=round(over_prob if over_prob > 0.5 else 1 - over_prob, 2),
        odds=over_odds,
        expected_value=round(ev_over, 3),
        recommendation=RecommendationEnum(_get_recommendation(ev_over, over_prob))
    ))

    # BTTS
    btts_prob = random.uniform(0.45, 0.60)
    ev_btts = (btts_prob * btts_odds) - 1
    predictions.append(MarketPredictionResponse(
        market=MarketEnum.BTTS,
        predicted_outcome="YES" if btts_prob > 0.5 else "NO",
        confidence=round(btts_prob if btts_prob > 0.5 else 1 - btts_prob, 2),
        odds=btts_odds,
        expected_value=round(ev_btts, 3),
        recommendation=RecommendationEnum(_get_recommendation(ev_btts, btts_prob))
    ))

    predictions = _sort_predictions(predictions, strategy)

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


@router.post("/analyze")
async def analyze_matches(request: AnalyzeMatchesRequest):
    """Analisa jogos e retorna previsões + pré-bilhete montado"""
    print(f"[DEBUG] Analisando {len(request.match_ids)} jogos com estratégia {request.strategy}")

    await asyncio.sleep(len(request.match_ids) * 0.3)  # Simula processamento

    results = [_generate_prediction(mid, request.strategy.value) for mid in request.match_ids]

    print(f"[DEBUG] Geradas {len(results)} previsões")

    # Monta pré-bilhete automaticamente com a melhor aposta de cada jogo
    pre_ticket_bets = []
    for prediction in results:
        # Pega a primeira aposta (já vem ordenada pela estratégia)
        if prediction.predictions:
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

    response = {
        "success": True,
        "strategy": request.strategy.value,
        "count": len(results),
        "predictions": [pred.model_dump() for pred in results],
        "pre_ticket": {
            "bets": pre_ticket_bets,
            "total_bets": len(pre_ticket_bets),
            "combined_odds": round(combined_odds, 2),
            "message": f"Pré-bilhete montado com {len(pre_ticket_bets)} apostas baseado na estratégia {request.strategy.value}"
        }
    }

    return response


@router.get("/predictions")
async def get_predictions(limit: int = 10):
    """Lista últimas previsões"""
    predictions = [_generate_prediction(str(uuid.uuid4()), "BALANCED") for _ in range(limit)]
    return {"success": True, "count": len(predictions), "predictions": predictions}


@router.get("/predictions/{prediction_id}", response_model=PredictionDetailResponse)
async def get_prediction(prediction_id: str) -> PredictionDetailResponse:
    """Detalhes de uma previsão"""
    pred = _generate_prediction(str(uuid.uuid4()), "BALANCED")
    return PredictionDetailResponse(success=True, prediction=pred)

