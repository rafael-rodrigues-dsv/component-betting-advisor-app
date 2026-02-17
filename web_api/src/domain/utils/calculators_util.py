class CalculatorsUtil:
    """Utilitários de cálculos de apostas"""
    @staticmethod
    def calculate_implied_probability(odds: float) -> float:
        """Probabilidade implícita = 1 / odd"""
        return 1 / odds if odds > 0 else 0
    @staticmethod
    def calculate_expected_value(probability: float, odds: float) -> float:
        """EV = (prob × odd) - 1"""
        return (probability * odds) - 1
    @staticmethod
    def calculate_combined_odds(odds_list: list) -> float:
        """Odd combinada = produto de todas as odds"""
        result = 1.0
        for odd in odds_list:
            result *= odd
        return result
    @staticmethod
    def calculate_margin(odds_home: float, odds_draw: float, odds_away: float) -> float:
        """Margem da casa = soma das prob implícitas - 1"""
        total_prob = (1/odds_home + 1/odds_draw + 1/odds_away)
        return total_prob - 1
    @staticmethod
    def calculate_kelly_criterion(probability: float, odds: float) -> float:
        """Critério de Kelly para dimensionamento de aposta"""
        if odds <= 1 or probability <= 0:
            return 0
        return ((odds * probability) - 1) / (odds - 1)
