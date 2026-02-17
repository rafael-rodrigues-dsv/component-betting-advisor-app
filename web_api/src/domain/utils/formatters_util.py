from datetime import datetime
class FormattersUtil:
    """Utilitários de formatação de dados"""
    @staticmethod
    def format_odds(odds: float, decimals: int = 2) -> str:
        """Formata odd para exibição"""
        return f"{odds:.{decimals}f}"
    @staticmethod
    def format_currency(value: float, currency: str = "R$") -> str:
        """Formata valor monetário"""
        return f"{currency} {value:.2f}"
    @staticmethod
    def format_percentage(value: float) -> str:
        """Formata percentual"""
        return f"{value * 100:.1f}%"
    @staticmethod
    def format_match_name(home: str, away: str) -> str:
        """Formata nome do jogo"""
        return f"{home} vs {away}"
    @staticmethod
    def format_datetime(dt: datetime, format: str = "%d/%m/%Y %H:%M") -> str:
        """Formata data/hora"""
        return dt.strftime(format)
