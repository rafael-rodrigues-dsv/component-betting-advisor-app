from datetime import datetime
from domain.models.match_model import Match, Venue
from domain.enums.match_status_enum import MatchStatus
from infrastructure.external.api_football.mappers.team_mapper import TeamMapper
from infrastructure.external.api_football.mappers.league_mapper import LeagueMapper
class FixtureToMatchMapper:
    """Mapeia JSON da API (fixture) para Match (domain)"""
    @staticmethod
    def to_domain(api_json: dict) -> Match:
        """API Fixture JSON -> Match"""
        fixture_data = api_json.get('fixture', {})
        teams_data = api_json.get('teams', {})
        league_data = api_json.get('league', {})
        # Mapeia times
        home_team = TeamMapper.to_domain(teams_data.get('home', {}))
        away_team = TeamMapper.to_domain(teams_data.get('away', {}))
        # Mapeia liga
        league = LeagueMapper.to_domain(league_data)
        # Mapeia status
        status_str = fixture_data.get('status', {}).get('short', 'NS')
        status_map = {'NS': MatchStatus.NOT_STARTED, 'LIVE': MatchStatus.LIVE, 'FT': MatchStatus.FINISHED}
        status = status_map.get(status_str, MatchStatus.NOT_STARTED)
        # Mapeia venue
        venue_data = fixture_data.get('venue', {})
        venue = Venue(name=venue_data.get('name', ''), city=venue_data.get('city'))
        return Match(
            id=str(fixture_data.get('id', '')),
            date=datetime.fromisoformat(fixture_data.get('date', '').replace('Z', '')),
            home_team=home_team,
            away_team=away_team,
            league=league,
            status=status,
            venue=venue,
            round=league_data.get('round'),
            timestamp=fixture_data.get('timestamp')
        )
