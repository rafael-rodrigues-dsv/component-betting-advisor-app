from typing import List
import logging
from domain.services.odds_analyzer import OddsAnalyzer
from domain.models.prediction_model import Prediction
from domain.models.odds_model import Odds, BookmakerOdds
from domain.enums.betting_strategy_enum import BettingStrategy
from application.services.match_application_service import MatchService
logger = logging.getLogger(__name__)
class PredictionApplicationService:
    """Application Service para análise de previsões"""
    def __init__(self):
        self.odds_analyzer = OddsAnalyzer()
        self.match_service = MatchService()
    async def analyze_matches(
        self, 
        match_ids: List[str], 
        strategy: BettingStrategy
    ) -> List[Prediction]:
        """
        Analisa múltiplos jogos com uma estratégia.
        Args:
            match_ids: Lista de IDs dos jogos
            strategy: Estratégia de análise
        Returns:
            Lista de previsões
        """
        logger.info(f"Analisando {len(match_ids)} jogos com estratégia {strategy.value}")
        predictions = []
        for match_id in match_ids:
            # Busca dados do match
            match_data = await self.match_service.get_match_with_odds(match_id)
            if not match_data or 'odds' not in match_data:
                logger.warning(f"Match {match_id} sem odds, pulando...")
                continue
            # Converte odds para domain model
            odds_data = match_data['odds']
            bookmakers = {}
            for bookie_name, bookie_odds in odds_data.items():
                bookmakers[bookie_name] = BookmakerOdds(
                    home=bookie_odds.get('home', 0),
                    draw=bookie_odds.get('draw', 0),
                    away=bookie_odds.get('away', 0),
                    over_25=bookie_odds.get('over_25'),
                    under_25=bookie_odds.get('under_25'),
                    btts_yes=bookie_odds.get('btts_yes'),
                    btts_no=bookie_odds.get('btts_no')
                )
            odds = Odds(bookmakers=bookmakers)
            # Analisa com OddsAnalyzer
            prediction = self.odds_analyzer.analyze_match(
                match_id=match_id,
                home_team=match_data['home_team']['name'],
                away_team=match_data['away_team']['name'],
                league=match_data['league']['name'],
                date=match_data['date'],
                odds=odds,
                strategy=strategy
            )
            predictions.append(prediction)
        logger.info(f"Análise concluída: {len(predictions)} previsões geradas")
        return predictions
