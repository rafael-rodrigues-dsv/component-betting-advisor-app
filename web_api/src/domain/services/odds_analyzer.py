"""
Odds Analyzer - Serviço de análise de odds e estratégias de apostas.

Este é o CORAÇÃO do sistema. Implementa as 4 estratégias de análise:
- CONSERVATIVE: Favoritos seguros, alta confiança
- BALANCED: Mix equilibrado de risco/retorno
- VALUE_BET: Busca discrepâncias entre casas
- AGGRESSIVE: Azarões com alto potencial

Calcula Expected Value (EV), identifica value bets e gera recomendações.
"""

from typing import List, Dict, Any
import logging

from domain.models.odds_model import Odds, BookmakerOdds
from domain.models.prediction_model import Prediction, MarketPrediction
from domain.enums.betting_strategy_enum import BettingStrategy
from domain.enums.market_type_enum import MarketType

logger = logging.getLogger(__name__)


class OddsAnalyzer:
    """
    Analisador de odds com múltiplas estratégias.

    Responsável por:
    - Analisar odds de um jogo
    - Aplicar estratégias de betting
    - Calcular Expected Value (EV)
    - Gerar recomendações (STRONG_BUY, BUY, HOLD, AVOID)
    - Identificar value bets
    """

    def analyze_match(
        self,
        match_id: str,
        home_team: str,
        away_team: str,
        league: str,
        date: str,
        odds: Odds,
        strategy: BettingStrategy
    ) -> Prediction:
        """
        Analisa um jogo e gera previsões baseado na estratégia.

        Args:
            match_id: ID do jogo
            home_team: Nome do time da casa
            away_team: Nome do time visitante
            league: Nome da liga
            date: Data do jogo
            odds: Odds completas do jogo
            strategy: Estratégia de análise a aplicar

        Returns:
            Prediction com análises de todos os mercados
        """
        logger.info(f"🔍 Analisando {home_team} vs {away_team} - Estratégia: {strategy.value}")

        # Aplica estratégia específica
        if strategy == BettingStrategy.CONSERVATIVE:
            predictions = self._conservative_strategy(odds)
        elif strategy == BettingStrategy.BALANCED:
            predictions = self._balanced_strategy(odds)
        elif strategy == BettingStrategy.VALUE_BET:
            predictions = self._value_bet_strategy(odds)
        elif strategy == BettingStrategy.AGGRESSIVE:
            predictions = self._aggressive_strategy(odds)
        else:
            predictions = []

        logger.info(f"✅ {len(predictions)} previsões geradas")

        return Prediction(
            match_id=match_id,
            home_team=home_team,
            away_team=away_team,
            league=league,
            date=date,
            strategy=strategy,
            predictions=predictions
        )

    def _conservative_strategy(self, odds: Odds) -> List[MarketPrediction]:
        """
        Estratégia Conservadora.

        Regras:
        - Favoritos com odds entre 1.50 e 2.00
        - Confiança mínima de 70%
        - Evita empates
        - Foca em probabilidades altas
        """
        predictions = []

        # Analisa cada bookmaker
        for bookmaker_name, bookmaker_odds in odds.bookmakers.items():

            # Verifica vitória da casa
            if 1.50 <= bookmaker_odds.home <= 2.00:
                confidence = self._calculate_confidence(bookmaker_odds.home)
                if confidence >= 0.70:
                    ev = self._calculate_ev(confidence, bookmaker_odds.home)

                    predictions.append(MarketPrediction(
                        market=MarketType.MATCH_WINNER,
                        predicted_outcome="HOME",
                        confidence=confidence,
                        odds=bookmaker_odds.home,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="STRONG_BUY" if confidence >= 0.75 else "BUY",
                        reason=f"Favorito seguro com {confidence*100:.1f}% de confiança"
                    ))

            # Verifica vitória visitante
            if 1.50 <= bookmaker_odds.away <= 2.00:
                confidence = self._calculate_confidence(bookmaker_odds.away)
                if confidence >= 0.70:
                    ev = self._calculate_ev(confidence, bookmaker_odds.away)

                    predictions.append(MarketPrediction(
                        market=MarketType.MATCH_WINNER,
                        predicted_outcome="AWAY",
                        confidence=confidence,
                        odds=bookmaker_odds.away,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="STRONG_BUY" if confidence >= 0.75 else "BUY",
                        reason=f"Favorito visitante seguro com {confidence*100:.1f}% de confiança"
                    ))

        # Remove duplicatas, mantém melhor EV
        return self._deduplicate_predictions(predictions)

    def _balanced_strategy(self, odds: Odds) -> List[MarketPrediction]:
        """
        Estratégia Balanceada.

        Regras:
        - Odds entre 1.70 e 3.50
        - Confiança mínima de 60%
        - Considera todos os mercados (1X2, Over/Under, BTTS)
        - Balanceia risco e retorno
        """
        predictions = []

        for bookmaker_name, bookmaker_odds in odds.bookmakers.items():

            # 1X2
            for outcome, odd in [("HOME", bookmaker_odds.home), ("DRAW", bookmaker_odds.draw), ("AWAY", bookmaker_odds.away)]:
                if 1.70 <= odd <= 3.50:
                    confidence = self._calculate_confidence(odd)
                    if confidence >= 0.60:
                        ev = self._calculate_ev(confidence, odd)

                        if ev > 0.02:  # Mínimo 2% EV
                            predictions.append(MarketPrediction(
                                market=MarketType.MATCH_WINNER,
                                predicted_outcome=outcome,
                                confidence=confidence,
                                odds=odd,
                                expected_value=ev,
                                bookmaker=bookmaker_name,
                                recommendation="BUY" if ev > 0.05 else "HOLD",
                                reason=f"Balanceado com EV de {ev*100:.1f}%"
                            ))

            # Over/Under 2.5
            if bookmaker_odds.over_25 and 1.70 <= bookmaker_odds.over_25 <= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.over_25)
                if confidence >= 0.60:
                    ev = self._calculate_ev(confidence, bookmaker_odds.over_25)

                    if ev > 0.02:
                        predictions.append(MarketPrediction(
                            market=MarketType.OVER_UNDER,
                            predicted_outcome="OVER_2.5",
                            confidence=confidence,
                            odds=bookmaker_odds.over_25,
                            expected_value=ev,
                            bookmaker=bookmaker_name,
                            recommendation="BUY" if ev > 0.05 else "HOLD",
                            reason=f"Over 2.5 balanceado (EV: {ev*100:.1f}%)"
                        ))

            # BTTS
            if bookmaker_odds.btts_yes and 1.70 <= bookmaker_odds.btts_yes <= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.btts_yes)
                if confidence >= 0.60:
                    ev = self._calculate_ev(confidence, bookmaker_odds.btts_yes)

                    if ev > 0.02:
                        predictions.append(MarketPrediction(
                            market=MarketType.BOTH_TEAMS_SCORE,
                            predicted_outcome="YES",
                            confidence=confidence,
                            odds=bookmaker_odds.btts_yes,
                            expected_value=ev,
                            bookmaker=bookmaker_name,
                            recommendation="BUY" if ev > 0.05 else "HOLD",
                            reason=f"BTTS com bom valor (EV: {ev*100:.1f}%)"
                        ))

        return self._deduplicate_predictions(predictions)

    def _value_bet_strategy(self, odds: Odds) -> List[MarketPrediction]:
        """
        Estratégia Value Bet.

        Regras:
        - Compara odds entre bookmakers
        - Identifica discrepâncias > 5%
        - Busca Expected Value positivo (EV > 5%)
        - Foca em oportunidades de arbitragem
        """
        predictions = []

        # Verifica se há múltiplas casas
        if len(odds.bookmakers) < 2:
            logger.warning("Value Bet precisa de múltiplas bookmakers")
            return predictions

        # Encontra discrepâncias
        discrepancies = self._find_discrepancies(odds)

        for disc in discrepancies:
            if disc['diff_percentage'] >= 5.0:  # Mínimo 5% de diferença
                confidence = disc['implied_prob']
                ev = self._calculate_ev(confidence, disc['best_odd'])

                if ev > 0.05:  # Mínimo 5% EV
                    predictions.append(MarketPrediction(
                        market=MarketType.MATCH_WINNER,
                        predicted_outcome=disc['outcome'],
                        confidence=confidence,
                        odds=disc['best_odd'],
                        expected_value=ev,
                        bookmaker=disc['best_bookmaker'],
                        recommendation="STRONG_BUY" if ev > 0.10 else "BUY",
                        reason=f"Value Bet! Discrepância de {disc['diff_percentage']:.1f}% entre casas (EV: {ev*100:.1f}%)"
                    ))

        return predictions

    def _aggressive_strategy(self, odds: Odds) -> List[MarketPrediction]:
        """
        Estratégia Agressiva.

        Regras:
        - Azarões com odds > 3.00
        - Confiança mínima de apenas 50%
        - Alto potencial de retorno
        - Aceita mais risco
        """
        predictions = []

        for bookmaker_name, bookmaker_odds in odds.bookmakers.items():

            # Busca azarões
            for outcome, odd in [("HOME", bookmaker_odds.home), ("DRAW", bookmaker_odds.draw), ("AWAY", bookmaker_odds.away)]:
                if odd >= 3.00:
                    confidence = self._calculate_confidence(odd)
                    if confidence >= 0.25:  # Mínimo 25% (1 em 4)
                        ev = self._calculate_ev(confidence, odd)

                        if ev > -0.05:  # Aceita até -5% EV para azarões
                            predictions.append(MarketPrediction(
                                market=MarketType.MATCH_WINNER,
                                predicted_outcome=outcome,
                                confidence=confidence,
                                odds=odd,
                                expected_value=ev,
                                bookmaker=bookmaker_name,
                                recommendation="BUY" if ev > 0 else "HOLD",
                                reason=f"Azarão com alto potencial (odd {odd:.2f}, EV: {ev*100:.1f}%)"
                            ))

            # Over altos
            if bookmaker_odds.over_25 and bookmaker_odds.over_25 >= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.over_25)
                if confidence >= 0.30:
                    ev = self._calculate_ev(confidence, bookmaker_odds.over_25)

                    if ev > -0.05:
                        predictions.append(MarketPrediction(
                            market=MarketType.OVER_UNDER,
                            predicted_outcome="OVER_2.5",
                            confidence=confidence,
                            odds=bookmaker_odds.over_25,
                            expected_value=ev,
                            bookmaker=bookmaker_name,
                            recommendation="BUY" if ev > 0 else "HOLD",
                            reason=f"Over agressivo (odd {bookmaker_odds.over_25:.2f})"
                        ))

        return self._deduplicate_predictions(predictions)

    def _calculate_confidence(self, odd: float) -> float:
        """
        Calcula confiança baseada na odd.

        Confiança = Probabilidade Implícita = 1 / odd

        Exemplos:
        - Odd 2.00 = 50% de confiança
        - Odd 1.50 = 66.7% de confiança
        - Odd 3.00 = 33.3% de confiança
        """
        return 1 / odd if odd > 0 else 0

    def _calculate_ev(self, probability: float, odd: float) -> float:
        """
        Calcula Expected Value (Valor Esperado).

        EV = (Probabilidade × Odd) - 1

        Interpretação:
        - EV > 0: Aposta vantajosa (value bet)
        - EV = 0: Aposta justa
        - EV < 0: Aposta desvantajosa

        Exemplos:
        - Prob 55%, Odd 2.00 → EV = 10% (ótima!)
        - Prob 50%, Odd 2.00 → EV = 0% (justa)
        - Prob 45%, Odd 2.00 → EV = -10% (ruim)
        """
        return (probability * odd) - 1

    def _find_discrepancies(self, odds: Odds) -> List[Dict[str, Any]]:
        """
        Encontra discrepâncias entre bookmakers.

        Compara as odds de todas as casas para cada mercado
        e identifica diferenças significativas (>3%).
        """
        discrepancies = []

        # Para cada mercado (home, draw, away)
        for outcome in ['home', 'draw', 'away']:
            odds_by_bookmaker = []

            for bookmaker_name, bookmaker_odds in odds.bookmakers.items():
                odd_value = getattr(bookmaker_odds, outcome)
                if odd_value and odd_value > 0:
                    odds_by_bookmaker.append({
                        'bookmaker': bookmaker_name,
                        'odd': odd_value
                    })

            if len(odds_by_bookmaker) >= 2:
                # Encontra melhor e pior odd
                best = max(odds_by_bookmaker, key=lambda x: x['odd'])
                worst = min(odds_by_bookmaker, key=lambda x: x['odd'])

                diff = best['odd'] - worst['odd']
                diff_percentage = (diff / worst['odd']) * 100

                if diff_percentage >= 3.0:  # Mínimo 3%
                    discrepancies.append({
                        'outcome': outcome.upper(),
                        'best_odd': best['odd'],
                        'best_bookmaker': best['bookmaker'],
                        'worst_odd': worst['odd'],
                        'worst_bookmaker': worst['bookmaker'],
                        'diff': diff,
                        'diff_percentage': diff_percentage,
                        'implied_prob': 1 / best['odd']
                    })

        return discrepancies

    def _deduplicate_predictions(self, predictions: List[MarketPrediction]) -> List[MarketPrediction]:
        """
        Remove previsões duplicadas, mantendo a de melhor EV.

        Agrupa por (market, outcome) e mantém apenas a melhor.
        """
        best_predictions = {}

        for pred in predictions:
            key = (pred.market, pred.predicted_outcome)

            if key not in best_predictions:
                best_predictions[key] = pred
            else:
                # Mantém a de maior EV
                if pred.expected_value > best_predictions[key].expected_value:
                    best_predictions[key] = pred

        # Ordena por EV (maior primeiro)
        result = list(best_predictions.values())
        result.sort(key=lambda x: x.expected_value, reverse=True)

        return result

