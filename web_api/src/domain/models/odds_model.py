"""
Odds Model - Representa odds de uma partida
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class BookmakerOdds:
    """
    Odds de uma casa de apostas para um jogo.

    Representa as odds oferecidas por uma bookmaker específica.
    """
    home: float
    """Odd para vitória do time da casa"""

    draw: float
    """Odd para empate"""

    away: float
    """Odd para vitória do time visitante"""

    over_25: Optional[float] = None
    """Odd para Over 2.5 gols"""

    under_25: Optional[float] = None
    """Odd para Under 2.5 gols"""

    btts_yes: Optional[float] = None
    """Odd para ambos marcam (BTTS Yes)"""

    btts_no: Optional[float] = None
    """Odd para ambos não marcam (BTTS No)"""

    def implied_probability_home(self) -> float:
        """Calcula probabilidade implícita de vitória da casa"""
        return 1 / self.home if self.home > 0 else 0

    def implied_probability_draw(self) -> float:
        """Calcula probabilidade implícita de empate"""
        return 1 / self.draw if self.draw > 0 else 0

    def implied_probability_away(self) -> float:
        """Calcula probabilidade implícita de vitória fora"""
        return 1 / self.away if self.away > 0 else 0

    def margin(self) -> float:
        """
        Calcula a margem da casa de apostas.

        Margem = soma das probabilidades implícitas - 1
        Exemplo: 0.05 = 5% de margem
        """
        total_prob = (
            self.implied_probability_home() +
            self.implied_probability_draw() +
            self.implied_probability_away()
        )
        return total_prob - 1


@dataclass
class Odds:
    """
    Odds completas de um jogo (todas as casas).

    Agrupa as odds de múltiplas bookmakers para comparação.
    """
    bookmakers: Dict[str, BookmakerOdds]
    """
    Dicionário de odds por bookmaker.
    
    Exemplo:
    {
        "bet365": BookmakerOdds(...),
        "betano": BookmakerOdds(...)
    }
    """

    def get_best_odd_home(self) -> tuple[str, float]:
        """Retorna (bookmaker, odd) com melhor odd para casa"""
        best_bookmaker = None
        best_odd = 0.0

        for bookmaker, odds in self.bookmakers.items():
            if odds.home > best_odd:
                best_odd = odds.home
                best_bookmaker = bookmaker

        return best_bookmaker, best_odd

    def get_best_odd_draw(self) -> tuple[str, float]:
        """Retorna (bookmaker, odd) com melhor odd para empate"""
        best_bookmaker = None
        best_odd = 0.0

        for bookmaker, odds in self.bookmakers.items():
            if odds.draw > best_odd:
                best_odd = odds.draw
                best_bookmaker = bookmaker

        return best_bookmaker, best_odd

    def get_best_odd_away(self) -> tuple[str, float]:
        """Retorna (bookmaker, odd) com melhor odd para fora"""
        best_bookmaker = None
        best_odd = 0.0

        for bookmaker, odds in self.bookmakers.items():
            if odds.away > best_odd:
                best_odd = odds.away
                best_bookmaker = bookmaker

        return best_bookmaker, best_odd

    def has_discrepancy(self, threshold: float = 0.05) -> bool:
        """
        Verifica se há discrepância significativa entre casas.

        Args:
            threshold: Diferença percentual mínima (padrão: 5%)

        Returns:
            True se houver discrepância acima do threshold
        """
        if len(self.bookmakers) < 2:
            return False

        # Verifica home
        odds_home = [odds.home for odds in self.bookmakers.values()]
        max_home = max(odds_home)
        min_home = min(odds_home)
        if (max_home - min_home) / min_home > threshold:
            return True

        # Verifica draw
        odds_draw = [odds.draw for odds in self.bookmakers.values()]
        max_draw = max(odds_draw)
        min_draw = min(odds_draw)
        if (max_draw - min_draw) / min_draw > threshold:
            return True

        # Verifica away
        odds_away = [odds.away for odds in self.bookmakers.values()]
        max_away = max(odds_away)
        min_away = min(odds_away)
        if (max_away - min_away) / min_away > threshold:
            return True

        return False

