"""
Prediction Controller - Análise e previsões usando OddsAnalyzer real.
"""

from fastapi import APIRouter
import uuid
import logging

from application.services.prediction_application_service import PredictionApplicationService
from web.dtos.requests.prediction_request import AnalyzeMatchesRequest
from web.dtos.responses.prediction_response import (
    PredictionResponse,
    MarketPredictionResponse,
    MarketEnum,
    RecommendationEnum,
)
from web.mappers.prediction_mapper import create_pre_ticket

router = APIRouter()
logger = logging.getLogger(__name__)

# Instância do serviço
prediction_service = PredictionApplicationService()


def _map_market_type(market_type) -> MarketEnum:
    """Converte domain MarketType → DTO MarketEnum."""
    mapping = {
        "MATCH_WINNER": MarketEnum.MATCH_WINNER,
        "OVER_UNDER": MarketEnum.OVER_UNDER,
        "BOTH_TEAMS_SCORE": MarketEnum.BTTS,
    }
    return mapping.get(market_type.value, MarketEnum.MATCH_WINNER)


def _map_recommendation(rec: str) -> RecommendationEnum:
    """Converte domain recommendation string → DTO RecommendationEnum."""
    mapping = {
        "STRONG_BUY": RecommendationEnum.STRONG_BET,
        "BUY": RecommendationEnum.RECOMMENDED,
        "HOLD": RecommendationEnum.CONSIDER,
        "AVOID": RecommendationEnum.AVOID,
    }
    return mapping.get(rec, RecommendationEnum.CONSIDER)


def _domain_to_dto(prediction) -> PredictionResponse:
    """Converte domain Prediction → DTO PredictionResponse."""
    market_responses = []
    for mp in prediction.predictions:
        market_responses.append(MarketPredictionResponse(
            market=_map_market_type(mp.market),
            predicted_outcome=mp.predicted_outcome,
            confidence=round(mp.confidence, 2),
            odds=round(mp.odds, 2),
            expected_value=round(mp.expected_value, 3),
            recommendation=_map_recommendation(mp.recommendation),
        ))

    return PredictionResponse(
        id=str(uuid.uuid4()),
        match_id=prediction.match_id,
        home_team=prediction.home_team,
        away_team=prediction.away_team,
        league=prediction.league,
        date=prediction.date,
        predictions=market_responses,
        strategy_used=prediction.strategy.value,
    )


@router.post("/analyze")
async def analyze_matches(request: AnalyzeMatchesRequest):
    """Analisa jogos com OddsAnalyzer real e retorna previsões + pré-bilhete."""
    logger.info(f"🔍 Analisando {len(request.match_ids)} jogos com estratégia {request.strategy}")

    try:
        # Converte string → enum
        from domain.enums.betting_strategy_enum import BettingStrategy
        strategy = BettingStrategy(request.strategy.value)

        # Usa o PredictionApplicationService (OddsAnalyzer real)
        domain_predictions = await prediction_service.analyze_matches(
            match_ids=request.match_ids,
            strategy=strategy,
        )

        # Filtra predictions sem market predictions (análise vazia)
        domain_predictions = [p for p in domain_predictions if p.predictions]

        # Converte domain → DTO
        results = [_domain_to_dto(p) for p in domain_predictions]

        logger.info(f"✅ {len(results)} previsões geradas (com markets)")

        # Busca odds por bookmaker para cada match (para comparação no frontend)
        odds_by_match = {}
        for p in domain_predictions:
            try:
                # Primeiro tenta odds do match_data (cache, sem request extra)
                match_data = prediction_service.match_service.get_match_by_id(p.match_id)
                if match_data and match_data.get("odds"):
                    odds_by_match[p.match_id] = match_data["odds"]
                else:
                    # Fallback: busca da API
                    odds_data = await prediction_service.match_service.get_odds_for_match(int(p.match_id))
                    if odds_data:
                        odds_by_match[p.match_id] = odds_data
            except Exception:
                pass

        # Injeta odds_by_bookmaker em cada resultado
        results_dicts = []
        for pred in results:
            pred_dict = pred.model_dump()
            pred_dict["odds_by_bookmaker"] = odds_by_match.get(pred.match_id, {})
            results_dicts.append(pred_dict)

        # Cria pré-bilhete diversificado
        pre_ticket = create_pre_ticket(results, request.strategy.value)

        return {
            "success": True,
            "strategy": request.strategy.value,
            "count": len(results),
            "predictions": results_dicts,
            "pre_ticket": pre_ticket,
        }
    except Exception as e:
        logger.error(f"❌ Erro na análise: {e}", exc_info=True)
        return {
            "success": False,
            "strategy": request.strategy.value,
            "count": 0,
            "predictions": [],
            "pre_ticket": None,
            "error": str(e),
        }

