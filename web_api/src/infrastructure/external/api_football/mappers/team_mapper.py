from domain.models.team_model import Team
from domain.models.logo_model import Logo
from pathlib import Path
class TeamMapper:
    """Mapeia JSON da API para Team (domain)"""
    ESCUDOS_PATH = Path(__file__).parent.parent.parent.parent.parent / "static" / "escudos"
    TEAM_LOGO_MAP = {
        "Flamengo": "flamengo.png", "Palmeiras": "palmeiras.png",
        "São Paulo": "sao-paulo.png", "Corinthians": "corinthians.png",
        "Atlético-MG": "atletico-mineiro.png", "Fluminense": "fluminense.png",
        "Internacional": "internacional.png", "Grêmio": "gremio.png",
        "Botafogo": "botafogo.png", "Santos": "santos.png",
        "Manchester City": "manchester-city.png", "Arsenal": "arsenal.png",
        "Liverpool": "liverpool.png", "Chelsea": "chelsea.png"
    }
    @classmethod
    def to_domain(cls, api_json: dict) -> Team:
        """API JSON -> Team"""
        team_id = str(api_json.get('id', ''))
        team_name = api_json.get('name', '')
        api_logo_url = api_json.get('logo', '')
        local_logo_file = cls.TEAM_LOGO_MAP.get(team_name)
        if local_logo_file and (cls.ESCUDOS_PATH / local_logo_file).exists():
            logo = Logo.local(local_logo_file)
        else:
            logo = Logo.external(api_logo_url)
        return Team(
            id=team_id,
            name=team_name,
            logo=logo,
            country=api_json.get('country')
        )
