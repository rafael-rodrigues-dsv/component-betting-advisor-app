from domain.models.league_model import League
class LeagueMapper:
    """Mapeia JSON da API para League (domain)"""
    @staticmethod
    def to_domain(api_json: dict) -> League:
        """API JSON -> League"""
        return League(
            id=str(api_json.get('id', '')),
            name=api_json.get('name', ''),
            country=api_json.get('country', ''),
            logo=api_json.get('logo'),
            flag=api_json.get('flag'),
            season=api_json.get('season'),
            type=api_json.get('type')
        )
