"""
Betting Strategy Enum - Estratégias de análise de apostas
"""

from enum import Enum


class BettingStrategy(Enum):
    """
    Estratégias de análise de apostas.

    Define diferentes abordagens para análise de odds e recomendações.
    """

    CONSERVATIVE = "CONSERVATIVE"
    """
    Estratégia Conservadora
    - Favoritos seguros (odds 1.50-2.00)
    - Alta confiança (>70%)
    - Evita empates
    - Menor risco
    """

    BALANCED = "BALANCED"
    """
    Estratégia Balanceada
    - Mix de favoritos e azarões leves
    - Confiança média (60-75%)
    - Considera todos os mercados
    - Risco médio
    """

    VALUE_BET = "VALUE_BET"
    """
    Estratégia Value Bet
    - Busca discrepâncias entre casas (>5%)
    - Foca em Expected Value positivo
    - Identifica odds sub/supervalorizadas
    - Risco médio-alto
    """

    AGGRESSIVE = "AGGRESSIVE"
    """
    Estratégia Agressiva
    - Azarões com potencial (odds >3.00)
    - Aceita menor confiança (>50%)
    - Maior retorno potencial
    - Alto risco
    """

