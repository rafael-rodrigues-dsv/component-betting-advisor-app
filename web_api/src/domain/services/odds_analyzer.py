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
        - Favoritos com odds entre 1.20 e 1.80
        - Confiança mínima de 55% (ajustada por margem)
        - Foca em probabilidades altas e EV positivo
        """
        predictions = []

        for bookmaker_name, bookmaker_odds in odds.bookmakers.items():

            # Verifica vitória da casa (favoritos fortes)
            if 1.20 <= bookmaker_odds.home <= 1.80:
                confidence = self._calculate_confidence(bookmaker_odds.home)
                ev = self._calculate_ev(confidence, bookmaker_odds.home)
                if ev > 0.01:
                    predictions.append(MarketPrediction(
                        market=MarketType.MATCH_WINNER,
                        predicted_outcome="HOME",
                        confidence=confidence,
                        odds=bookmaker_odds.home,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="STRONG_BUY" if ev > 0.05 else "BUY",
                        reason=f"Favorito seguro com {confidence*100:.1f}% de confianca"
                    ))

            # Verifica vitória visitante (favoritos fortes)
            if 1.20 <= bookmaker_odds.away <= 1.80:
                confidence = self._calculate_confidence(bookmaker_odds.away)
                ev = self._calculate_ev(confidence, bookmaker_odds.away)
                if ev > 0.01:
                    predictions.append(MarketPrediction(
                        market=MarketType.MATCH_WINNER,
                        predicted_outcome="AWAY",
                        confidence=confidence,
                        odds=bookmaker_odds.away,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="STRONG_BUY" if ev > 0.05 else "BUY",
                        reason=f"Favorito visitante seguro com {confidence*100:.1f}% de confianca"
                    ))

            # Under 2.5 é um mercado conservador
            if bookmaker_odds.under_25 and 1.20 <= bookmaker_odds.under_25 <= 1.80:
                confidence = self._calculate_confidence(bookmaker_odds.under_25)
                ev = self._calculate_ev(confidence, bookmaker_odds.under_25)
                if ev > 0.01:
                    predictions.append(MarketPrediction(
                        market=MarketType.OVER_UNDER,
                        predicted_outcome="UNDER_2.5",
                        confidence=confidence,
                        odds=bookmaker_odds.under_25,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="STRONG_BUY" if ev > 0.05 else "BUY",
                        reason=f"Under 2.5 conservador ({confidence*100:.1f}% de confianca)"
                    ))

            # BTTS Nao tambem e conservador
            if bookmaker_odds.btts_no and 1.20 <= bookmaker_odds.btts_no <= 1.80:
                confidence = self._calculate_confidence(bookmaker_odds.btts_no)
                ev = self._calculate_ev(confidence, bookmaker_odds.btts_no)
                if ev > 0.01:
                    predictions.append(MarketPrediction(
                        market=MarketType.BOTH_TEAMS_SCORE,
                        predicted_outcome="NO",
                        confidence=confidence,
                        odds=bookmaker_odds.btts_no,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="STRONG_BUY" if ev > 0.05 else "BUY",
                        reason=f"BTTS Nao conservador ({confidence*100:.1f}% de confianca)"
                    ))

        # Remove duplicatas, mantém melhor EV
        return self._deduplicate_predictions(predictions)

    def _balanced_strategy(self, odds: Odds) -> List[MarketPrediction]:
        """
        Estratégia Balanceada.

        Regras:
        - Odds entre 1.50 e 3.50
        - Confiança mínima de 30%
        - EV mínimo de 2%
        - Considera todos os mercados (1X2, Over/Under, BTTS)
        - Balanceia risco e retorno
        """
        predictions = []

        for bookmaker_name, bookmaker_odds in odds.bookmakers.items():

            # 1X2
            for outcome, odd in [("HOME", bookmaker_odds.home), ("DRAW", bookmaker_odds.draw), ("AWAY", bookmaker_odds.away)]:
                if 1.50 <= odd <= 3.50:
                    confidence = self._calculate_confidence(odd)
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
            if bookmaker_odds.over_25 and 1.50 <= bookmaker_odds.over_25 <= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.over_25)
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

            if bookmaker_odds.under_25 and 1.50 <= bookmaker_odds.under_25 <= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.under_25)
                ev = self._calculate_ev(confidence, bookmaker_odds.under_25)

                if ev > 0.02:
                    predictions.append(MarketPrediction(
                        market=MarketType.OVER_UNDER,
                        predicted_outcome="UNDER_2.5",
                        confidence=confidence,
                        odds=bookmaker_odds.under_25,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="BUY" if ev > 0.05 else "HOLD",
                        reason=f"Under 2.5 balanceado (EV: {ev*100:.1f}%)"
                    ))

            # BTTS
            if bookmaker_odds.btts_yes and 1.50 <= bookmaker_odds.btts_yes <= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.btts_yes)
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
                        reason=f"BTTS Sim com bom valor (EV: {ev*100:.1f}%)"
                    ))

            if bookmaker_odds.btts_no and 1.50 <= bookmaker_odds.btts_no <= 2.50:
                confidence = self._calculate_confidence(bookmaker_odds.btts_no)
                ev = self._calculate_ev(confidence, bookmaker_odds.btts_no)

                if ev > 0.02:
                    predictions.append(MarketPrediction(
                        market=MarketType.BOTH_TEAMS_SCORE,
                        predicted_outcome="NO",
                        confidence=confidence,
                        odds=bookmaker_odds.btts_no,
                        expected_value=ev,
                        bookmaker=bookmaker_name,
                        recommendation="BUY" if ev > 0.05 else "HOLD",
                        reason=f"BTTS Nao com bom valor (EV: {ev*100:.1f}%)"
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
                        market=disc.get('market_type', MarketType.MATCH_WINNER),
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

            # BTTS Sim agressivo
            if bookmaker_odds.btts_yes and bookmaker_odds.btts_yes >= 2.00:
                confidence = self._calculate_confidence(bookmaker_odds.btts_yes)
                if confidence >= 0.30:
                    ev = self._calculate_ev(confidence, bookmaker_odds.btts_yes)

                    if ev > -0.05:
                        predictions.append(MarketPrediction(
                            market=MarketType.BOTH_TEAMS_SCORE,
                            predicted_outcome="YES",
                            confidence=confidence,
                            odds=bookmaker_odds.btts_yes,
                            expected_value=ev,
                            bookmaker=bookmaker_name,
                            recommendation="BUY" if ev > 0 else "HOLD",
                            reason=f"BTTS agressivo (odd {bookmaker_odds.btts_yes:.2f})"
                        ))

        return self._deduplicate_predictions(predictions)

    def _calculate_confidence(self, odd: float) -> float:
        """
        Calcula confiança (probabilidade estimada) baseada na odd.

        Aplica correção de margem da casa de apostas (~5-8% de overround).
        A probabilidade implícita pura (1/odd) inclui a margem da casa,
        então a probabilidade real é ligeiramente maior para favoritos
        e menor para azarões.

        Fórmula: prob_estimada = (1/odd) + ajuste_margem

        O ajuste é proporcional: favoritos ganham mais confiança,
        azarões ganham menos.
        """
        if odd <= 0:
            return 0

        implied_prob = 1 / odd

        # Ajuste de margem: assume ~6% de overround total
        # Favoritos (odds baixas) têm probabilidade subestimada pela odd
        # Azarões (odds altas) têm probabilidade superestimada
        margin_adjustment = 0.03  # ~3% de ajuste por lado

        if odd <= 2.00:
            # Favoritos: a probabilidade real é um pouco MAIOR que a implícita
            adjusted = implied_prob + margin_adjustment
        elif odd <= 3.50:
            # Odds médias: ajuste moderado
            adjusted = implied_prob + (margin_adjustment * 0.5)
        else:
            # Azarões: sem ajuste (a odd já reflete bem o risco)
            adjusted = implied_prob

        return min(adjusted, 0.95)  # Cap em 95%

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

        # Mercados a comparar: (atributo, outcome_label, market_type)
        markets_to_check = [
            ('home', 'HOME', MarketType.MATCH_WINNER),
            ('draw', 'DRAW', MarketType.MATCH_WINNER),
            ('away', 'AWAY', MarketType.MATCH_WINNER),
            ('over_25', 'OVER_2.5', MarketType.OVER_UNDER),
            ('under_25', 'UNDER_2.5', MarketType.OVER_UNDER),
            ('btts_yes', 'YES', MarketType.BOTH_TEAMS_SCORE),
            ('btts_no', 'NO', MarketType.BOTH_TEAMS_SCORE),
        ]

        for attr, outcome_label, market_type in markets_to_check:
            odds_by_bookmaker = []

            for bookmaker_name, bookmaker_odds in odds.bookmakers.items():
                odd_value = getattr(bookmaker_odds, attr, None)
                if odd_value and odd_value > 0:
                    odds_by_bookmaker.append({
                        'bookmaker': bookmaker_name,
                        'odd': odd_value
                    })

            if len(odds_by_bookmaker) >= 2:
                best = max(odds_by_bookmaker, key=lambda x: x['odd'])
                worst = min(odds_by_bookmaker, key=lambda x: x['odd'])

                diff = best['odd'] - worst['odd']
                diff_percentage = (diff / worst['odd']) * 100

                if diff_percentage >= 3.0:
                    discrepancies.append({
                        'outcome': outcome_label,
                        'market_type': market_type,
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

