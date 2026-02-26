"""
Match Mapper - Converte dados de serviço para DTOs de response
"""
from typing import Dict, Any, List
from web.dtos.responses.match_response import (
    MatchResponse,
    TeamResponse,
    LeagueResponse,
    VenueResponse,
    RoundInfoResponse,
    OddsResponse,
    GoalsResponse
)
from web.dtos.responses.logo_dto import LogoDTO


class MatchMapper:
    """Mapper para converter dados de match do service para DTOs"""

    @staticmethod
    def to_match_response(match_data: Dict[str, Any]) -> MatchResponse:
        """
        Converte dados de match do service para MatchResponse DTO.

        Args:
            match_data: Dicionário com dados do match do service

        Returns:
            MatchResponse tipado
        """
        # Mapeia league
        league_data = match_data.get("league") or {}
        league = LeagueResponse(
            id=str(league_data.get("id") or ""),
            name=league_data.get("name") or "",
            country=league_data.get("country") or "",
            logo=league_data.get("logo") or "",
            type=league_data.get("type") or "league"
        )

        # Mapeia home_team
        home_team_data = match_data.get("home_team") or {}
        home_team_logo_data = home_team_data.get("logo") or {}
        home_team = TeamResponse(
            id=str(home_team_data.get("id") or ""),
            name=home_team_data.get("name") or "",
            logo=LogoDTO(
                url=home_team_logo_data.get("url") or "",
                type=home_team_logo_data.get("type") or "LOCAL"
            ),
            country=home_team_data.get("country") or "Brazil"
        )

        # Mapeia away_team
        away_team_data = match_data.get("away_team") or {}
        away_team_logo_data = away_team_data.get("logo") or {}
        away_team = TeamResponse(
            id=str(away_team_data.get("id") or ""),
            name=away_team_data.get("name") or "",
            logo=LogoDTO(
                url=away_team_logo_data.get("url") or "",
                type=away_team_logo_data.get("type") or "LOCAL"
            ),
            country=away_team_data.get("country") or "Brazil"
        )

        # Mapeia round
        round_data = match_data.get("round") or {}
        round_info = RoundInfoResponse(
            type=round_data.get("type") or "round",
            number=round_data.get("number"),
            name=round_data.get("name") or ""
        )

        # Mapeia venue
        venue_data = match_data.get("venue") or {}
        venue = VenueResponse(
            name=venue_data.get("name") or "",
            city=venue_data.get("city") or ""
        )

        # Mapeia odds (dicionário de bookmakers)
        odds_data = match_data.get("odds", {})
        odds_mapped: Dict[str, OddsResponse] = {}

        for bookmaker, bookmaker_odds in odds_data.items():
            if isinstance(bookmaker_odds, dict):
                odds_mapped[bookmaker] = OddsResponse(
                    home=bookmaker_odds.get("home", 0.0),
                    draw=bookmaker_odds.get("draw", 0.0),
                    away=bookmaker_odds.get("away", 0.0),
                    over_25=bookmaker_odds.get("over_25", 0.0),
                    under_25=bookmaker_odds.get("under_25", 0.0),
                    btts_yes=bookmaker_odds.get("btts_yes", 0.0),
                    btts_no=bookmaker_odds.get("btts_no", 0.0)
                )

        # Mapeia goals (placar)
        goals_data = match_data.get("goals") or {}
        goals = GoalsResponse(
            home=goals_data.get("home"),
            away=goals_data.get("away"),
        )

        return MatchResponse(
            id=str(match_data.get("id") or ""),
            league=league,
            home_team=home_team,
            away_team=away_team,
            date=match_data.get("date") or "",
            timestamp=match_data.get("timestamp") or "",
            status=match_data.get("status") or "Not Started",
            status_short=match_data.get("status_short") or "NS",
            elapsed=match_data.get("elapsed"),
            goals=goals,
            round=round_info,
            venue=venue,
            odds=odds_mapped
        )

    @staticmethod
    def to_matches_list(matches_data: List[Dict[str, Any]]) -> List[MatchResponse]:
        """
        Converte lista de matches do service para lista de MatchResponse DTOs.

        Args:
            matches_data: Lista de dicionários com dados de matches

        Returns:
            Lista de MatchResponse tipados
        """
        return [MatchMapper.to_match_response(match) for match in matches_data]

