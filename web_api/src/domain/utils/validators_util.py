class ValidatorsUtil:
    """Utilitários de validação de domínio"""
    @staticmethod
    def validate_odds(odds: float) -> bool:
        """Valida se odd está em range válido (1.01 - 1000)"""
        return 1.01 <= odds <= 1000.0
    @staticmethod
    def validate_stake(stake: float) -> bool:
        """Valida se stake é positivo"""
        return stake > 0
    @staticmethod
    def validate_confidence(confidence: float) -> bool:
        """Valida se confiança está entre 0 e 1"""
        return 0.0 <= confidence <= 1.0
    @staticmethod
    def validate_ticket_bets(bets: list) -> tuple:
        """Valida lista de bets de um ticket"""
        if not bets:
            return False, "Ticket deve ter pelo menos 1 aposta"
        if len(bets) > 20:
            return False, "Ticket não pode ter mais de 20 apostas"
        return True, "OK"
