"""
Prediction Controller - Análise e previsões (lê do CACHE)
"""

from fastapi import APIRouter
import uuid
import asyncio

from application.services.match_application_service import MatchService
from web.dtos.requests.prediction_request import AnalyzeMatchesRequest
from web.dtos.responses.prediction_response import (
    PredictionResponse,
    PredictionDetailResponse
)
from web.mappers.prediction_mapper import (
    generate_mock_prediction,
    create_pre_ticket
)

router = APIRouter()

# Instância do serviço
match_service = MatchService()



@router.post("/analyze")
async def analyze_matches(request: AnalyzeMatchesRequest):
    """Analisa jogos e retorna previsões + pré-bilhete montado"""
    print(f"[DEBUG] Analisando {len(request.match_ids)} jogos com estratégia {request.strategy}")

    await asyncio.sleep(len(request.match_ids) * 0.3)  # Simula processamento

    # Gera previsões usando o mapper
    results = []
    for match_id in request.match_ids:
        # Busca dados do match no cache
        match_data = match_service.get_match_by_id(match_id)

        if not match_data:
            # Fallback: cria dados mínimos para gerar previsão
            print(f"[WARNING] Match {match_id} não encontrado no cache!")
            match_data = {"id": match_id}

        # Gera previsão usando mapper
        prediction = generate_mock_prediction(match_data, request.strategy.value)
        results.append(prediction)

    print(f"[DEBUG] Geradas {len(results)} previsões")

    # Cria pré-bilhete usando mapper
    pre_ticket = create_pre_ticket(results, request.strategy.value)

    response = {
        "success": True,
        "strategy": request.strategy.value,
        "count": len(results),
        "predictions": [pred.model_dump() for pred in results],
        "pre_ticket": pre_ticket
    }

    return response


@router.get("/predictions")
async def get_predictions(limit: int = 10):
    """Lista últimas previsões"""
    predictions = []
    for _ in range(limit):
        match_data = {"id": str(uuid.uuid4())}
        prediction = generate_mock_prediction(match_data, "BALANCED")
        predictions.append(prediction)

    return {"success": True, "count": len(predictions), "predictions": predictions}


@router.get("/predictions/{prediction_id}", response_model=PredictionDetailResponse)
async def get_prediction(prediction_id: str) -> PredictionDetailResponse:
    """Detalhes de uma previsão"""
    match_data = {"id": str(uuid.uuid4())}
    pred = generate_mock_prediction(match_data, "BALANCED")
    return PredictionDetailResponse(success=True, prediction=pred)

