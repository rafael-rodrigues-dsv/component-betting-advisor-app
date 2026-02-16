/**
 * MatchCard Component
 */
import React from 'react';
import type { Match, Logo } from '../../types';

const getLeagueLogo = (leagueName: string): string => {
  const logos: Record<string, string> = {
    'Brasileirão Série A': '🇧🇷',
    'Copa do Brasil': '🏆',
    'Premier League': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  };
  return logos[leagueName] || '🏆';
};

const getTeamLogoUrl = (logo: Logo): string => {
  // Se é externo, retorna direto
  if (logo.type === 'EXT') {
    return logo.url;
  }

  // Se é local, monta URL com backend
  if (logo.url.startsWith('http')) {
    return logo.url;
  }

  return `http://localhost:8000${logo.url}`;
};

interface MatchCardProps {
  match: Match;
  isSelected: boolean;
  onSelect: (matchId: string) => void;
  selectedBookmaker: string;
}

export const MatchCard: React.FC<MatchCardProps> = ({ match, isSelected, onSelect, selectedBookmaker }) => {
  const homeLogoUrl = getTeamLogoUrl(match.home_team.logo);
  const awayLogoUrl = getTeamLogoUrl(match.away_team.logo);

  // Pega as odds da casa de apostas selecionada (fallback para bet365)
  const bookmakerOdds = match.odds[selectedBookmaker] || match.odds['bet365'] || {
    home: 0,
    draw: 0,
    away: 0
  };

  return (
    <div
      className={`match-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(match.id)}
    >
      <div className="match-league">
        <span className="league-logo">{getLeagueLogo(match.league.name)}</span>
        <span>{match.league.name}</span>
        {match.round && <span className="match-round">• {match.round.name}</span>}
      </div>
      <div className="match-date-time">
        <span className="match-date">
          📅 {new Date(match.date).toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: 'short' })}
        </span>
        <span className="match-time">
          🕐 {new Date(match.date).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
      <div className="match-teams">
        <div className="team">
          <img src={homeLogoUrl} alt={match.home_team.name} className="team-logo-img" onError={(e) => {
            e.currentTarget.style.display = 'none';
            e.currentTarget.nextElementSibling && (e.currentTarget.nextElementSibling.textContent = '⚽');
          }} />
          <span className="team-logo" style={{ display: 'none' }}>⚽</span>
          <span className="team-name">{match.home_team.name}</span>
        </div>
        <span className="match-vs">vs</span>
        <div className="team">
          <img src={awayLogoUrl} alt={match.away_team.name} className="team-logo-img" onError={(e) => {
            e.currentTarget.style.display = 'none';
            e.currentTarget.nextElementSibling && (e.currentTarget.nextElementSibling.textContent = '⚽');
          }} />
          <span className="team-logo" style={{ display: 'none' }}>⚽</span>
          <span className="team-name">{match.away_team.name}</span>
        </div>
      </div>
      {match.venue && <div className="match-venue">🏟️ {match.venue.name}</div>}
      <div className="match-odds">
        <div className="odd-item"><div className="odd-label">Casa</div><div className="odd-value">{bookmakerOdds.home}</div></div>
        <div className="odd-item"><div className="odd-label">Empate</div><div className="odd-value">{bookmakerOdds.draw}</div></div>
        <div className="odd-item"><div className="odd-label">Fora</div><div className="odd-value">{bookmakerOdds.away}</div></div>
      </div>
    </div>
  );
};

