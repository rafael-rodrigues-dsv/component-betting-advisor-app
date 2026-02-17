"""
Prediction Model - Representa uma previsão de análise
"""

from dataclasses import dataclass
from typing import List
from domain.enums.market_type_enum import MarketType
from domain.enums.betting_strategy_enum import BettingStrategy


@dataclass
class MarketPrediction:
    """
    Previsão para um mercado específico.

    Representa a análise de um mercado (1X2, Over/Under, etc) com
    recomendação, confiança e Expected Value.
    """
    market: MarketType
    """Tipo do mercado analisado"""

    predicted_outcome: str
    """Resultado previsto (ex: "HOME", "OVER_2.5", "YES")"""

    confidence: float
    """Confiança na previsão (0.0 a 1.0)"""

    odds: float
    """Odd recomendada"""

    expected_value: float
    """Expected Value (EV) - Valor esperado da aposta"""

    bookmaker: str
    """Casa de apostas recomendada"""

    recommendation: str
    """Recomendação: STRONG_BUY, BUY, HOLD, AVOID"""

    reason: str = ""
    """Razão da recomendação"""

    def is_positive_ev(self) -> bool:
        """Verifica se tem EV positivo"""
        return self.expected_value > 0

    def is_recommended(self) -> bool:
        """Verifica se é recomendada (BUY ou STRONG_BUY)"""
        return self.recommendation in ["BUY", "STRONG_BUY"]


@dataclass
class Prediction:
    """
    Previsão completa de um jogo.

    Contém todas as análises de mercados para um jogo específico,
    baseado em uma estratégia de betting.
    """
    match_id: str
    """ID da partida analisada"""

    home_team: str
    """Nome do time da casa"""

    away_team: str
    """Nome do time visitante"""

    league: str
    """Nome da liga"""

    date: str
    """Data do jogo"""

    strategy: BettingStrategy
    """Estratégia usada na análise"""

    predictions: List[MarketPrediction]
    """Lista de previsões por mercado"""

    def get_best_predictions(self, min_confidence: float = 0.6) -> List[MarketPrediction]:
        """
        Retorna as melhores previsões.

        Args:
            min_confidence: Confiança mínima (padrão: 60%)

        Returns:
            Lista de previsões filtradas e ordenadas por EV
        """
        filtered = [
            p for p in self.predictions
            if p.confidence >= min_confidence and p.is_recommended()
        ]

        # Ordena por Expected Value (maior primeiro)
        return sorted(filtered, key=lambda x: x.expected_value, reverse=True)

    def has_recommendations(self) -> bool:
        """Verifica se há pelo menos uma recomendação"""
        return any(p.is_recommended() for p in self.predictions)

    def total_expected_value(self) -> float:
        """Soma o EV de todas as previsões recomendadas"""
        return sum(
            p.expected_value
            for p in self.predictions
            if p.is_recommended()
        )

