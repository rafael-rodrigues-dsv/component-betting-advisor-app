from domain.models.odds_model import Odds, BookmakerOdds
class OddsMapper:
    """Mapeia JSON da API para Odds (domain)"""
    @staticmethod
    def to_domain(api_json: dict) -> Odds:
        """API JSON -> Odds"""
        bookmakers = {}
        for bookmaker_data in api_json.get('bookmakers', []):
            bookmaker_name = bookmaker_data.get('name', '').lower().replace(' ', '')
            odds_values = {}
            for bet in bookmaker_data.get('bets', []):
                bet_name = bet.get('name', '')
                values = bet.get('values', [])
                if bet_name == 'Match Winner':
                    for val in values:
                        vtype = val.get('value', '').lower()
                        if vtype == 'home': odds_values['home'] = float(val.get('odd', 0))
                        elif vtype == 'draw': odds_values['draw'] = float(val.get('odd', 0))
                        elif vtype == 'away': odds_values['away'] = float(val.get('odd', 0))
            if odds_values:
                bookmakers[bookmaker_name] = BookmakerOdds(**odds_values)
        return Odds(bookmakers=bookmakers)
