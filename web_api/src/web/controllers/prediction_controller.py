"""
Prediction Controller - Análise e previsões (MOCK)
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import uuid
import asyncio

router = APIRouter()


class AnalyzeRequest(BaseModel):
    match_ids: List[str]
    strategy: str = "BALANCED"


MOCK_TEAMS = [
    ("Flamengo", "Palmeiras"),
    ("Corinthians", "São Paulo"),
    ("Atlético Mineiro", "Fluminense"),
    ("Botafogo", "Vasco da Gama"),
    ("Grêmio", "Internacional"),
    ("Santos", "Cruzeiro"),
    ("Athletico Paranaense", "Bahia"),
    ("Fortaleza", "Bragantino"),
]


def _get_recommendation(ev: float, confidence: float) -> str:
    if ev > 0.10 and confidence > 0.60:
        return "STRONG_BET"
    elif ev > 0.05 and confidence > 0.50:
        return "VALUE_BET"
    elif ev > 0.05:
        return "RISKY"
    elif ev > 0:
        return "MARGINAL"
    return "SKIP"


def _sort_predictions(predictions: list, strategy: str) -> list:
    if strategy == "CONSERVATIVE":
        return sorted(predictions, key=lambda x: x["confidence"], reverse=True)
    elif strategy == "VALUE_BET":
        return sorted(predictions, key=lambda x: x["expected_value"], reverse=True)
    elif strategy == "AGGRESSIVE":
        return sorted(predictions, key=lambda x: x["odds"] * x["confidence"], reverse=True)
    else:  # BALANCED
        return sorted(predictions, key=lambda x: (x["expected_value"] * 0.5) + (x["confidence"] * 0.5), reverse=True)


def _generate_prediction(match_id: str, strategy: str) -> dict:
    """Gera previsão mockada"""
    home, away = random.choice(MOCK_TEAMS)

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

    # 1X2
    best = max([
        ("HOME", home_prob, home_odds),
        ("DRAW", draw_prob, draw_odds),
        ("AWAY", away_prob, away_odds)
    ], key=lambda x: (x[1] * x[2]) - 1)

    ev = (best[1] * best[2]) - 1
    predictions.append({
        "market": "1X2",
        "predicted_outcome": best[0],
        "confidence": round(best[1], 2),
        "odds": best[2],
        "expected_value": round(ev, 3),
        "recommendation": _get_recommendation(ev, best[1])
    })

    # Over/Under 2.5
    over_prob = random.uniform(0.45, 0.65)
    ev_over = (over_prob * over_odds) - 1
    predictions.append({
        "market": "OVER_UNDER_25",
        "predicted_outcome": "OVER" if over_prob > 0.5 else "UNDER",
        "confidence": round(over_prob if over_prob > 0.5 else 1 - over_prob, 2),
        "odds": over_odds,
        "expected_value": round(ev_over, 3),
        "recommendation": _get_recommendation(ev_over, over_prob)
    })

    # BTTS
    btts_prob = random.uniform(0.45, 0.60)
    ev_btts = (btts_prob * btts_odds) - 1
    predictions.append({
        "market": "BTTS",
        "predicted_outcome": "YES" if btts_prob > 0.5 else "NO",
        "confidence": round(btts_prob if btts_prob > 0.5 else 1 - btts_prob, 2),
        "odds": btts_odds,
        "expected_value": round(ev_btts, 3),
        "recommendation": _get_recommendation(ev_btts, btts_prob)
    })

    predictions = _sort_predictions(predictions, strategy)

    return {
        "id": str(uuid.uuid4()),
        "match_id": match_id,
        "home_team": home,
        "away_team": away,
        "league": "Brasileirão Série A",
        "match_date": datetime.now().isoformat(),
        "predictions": predictions,
        "best_bet": predictions[0] if predictions else None,
        "created_at": datetime.now().isoformat()
    }


@router.post("/analyze")
async def analyze_matches(request: AnalyzeRequest):
    """Analisa jogos e retorna previsões"""
    await asyncio.sleep(len(request.match_ids) * 0.3)  # Simula processamento

    results = [_generate_prediction(mid, request.strategy) for mid in request.match_ids]

    return {
        "success": True,
        "strategy": request.strategy,
        "count": len(results),
        "predictions": results
    }


@router.get("/predictions")
async def get_predictions(limit: int = 10):
    """Lista últimas previsões"""
    predictions = [_generate_prediction(str(uuid.uuid4()), "BALANCED") for _ in range(limit)]
    return {"success": True, "count": len(predictions), "predictions": predictions}


@router.get("/predictions/{prediction_id}")
async def get_prediction(prediction_id: str):
    """Detalhes de uma previsão"""
    pred = _generate_prediction(str(uuid.uuid4()), "BALANCED")
    pred["id"] = prediction_id
    return {"success": True, "prediction": pred}

