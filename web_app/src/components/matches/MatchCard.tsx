/**
 * MatchCard Component
 *
 * Exibe informações de uma partida com:
 * - Badge de status (NS, Live, HT, etc.)
 * - Tabela comparativa de odds entre todas as casas de apostas
 * - Highlight verde na melhor odd de cada mercado
 * - Botão 🔄 de refresh para atualizar odds + status da API
 */
import React, { useState, useCallback } from 'react';
import { matchesApi } from '../../services/api';
import type { Match, Logo, Odds, BookmakerOdds } from '../../types';

const getLeagueLogo = (leagueName: string): string => {
  const logos: Record<string, string> = {
    'Brasileirão Série A': '🇧🇷',
    'Serie A': '🇧🇷',
    'Copa do Brasil': '🏆',
    'Copa Do Brasil': '🏆',
    'Premier League': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
    'La Liga': '🇪🇸',
    'Bundesliga': '🇩🇪',
    'Ligue 1': '🇫🇷',
  };
  return logos[leagueName] || '🏆';
};

const getTeamLogoUrl = (logo: Logo): string => {
  if (logo.type === 'EXT') return logo.url;
  if (logo.url.startsWith('http')) return logo.url;
  return `http://localhost:8000${logo.url}`;
};

const getStatusInfo = (statusShort: string): { label: string; className: string } => {
  const map: Record<string, { label: string; className: string }> = {
    'TBD': { label: 'A definir', className: 'status-tbd' },
    'NS':  { label: 'Não iniciado', className: 'status-ns' },
    '1H':  { label: '1º Tempo', className: 'status-live' },
    'HT':  { label: 'Intervalo', className: 'status-live' },
    '2H':  { label: '2º Tempo', className: 'status-live' },
    'ET':  { label: 'Prorrogação', className: 'status-live' },
    'BT':  { label: 'Intervalo Pror.', className: 'status-live' },
    'P':   { label: 'Pênaltis', className: 'status-live' },
    'SUSP':{ label: 'Suspenso', className: 'status-susp' },
    'INT': { label: 'Interrompido', className: 'status-susp' },
    'LIVE':{ label: 'Ao Vivo', className: 'status-live' },
    'FT':  { label: 'Encerrado', className: 'status-ft' },
  };
  return map[statusShort] || { label: statusShort, className: 'status-ns' };
};

/** Metadados visuais das casas de apostas */
const BOOKMAKER_META: Record<string, { name: string; logo: string }> = {
  'bet365':  { name: 'Bet365',  logo: '🟢' },
  'betano':  { name: 'Betano',  logo: '🟡' },
  'betfair':  { name: 'Betfair',  logo: '🟠' },
  '1xbet':   { name: '1xBet',   logo: '🔵' },
  'pinnacle': { name: 'Pinnacle', logo: '📊' },
};

/** Calcula a melhor odd por mercado entre todas as bookmakers */
const getBestOdds = (odds: Odds): { home: number; draw: number; away: number } => {
  const bookmakers = Object.values(odds);
  if (bookmakers.length === 0) return { home: 0, draw: 0, away: 0 };

  return {
    home: Math.max(...bookmakers.map(b => b.home || 0)),
    draw: Math.max(...bookmakers.map(b => b.draw || 0)),
    away: Math.max(...bookmakers.map(b => b.away || 0)),
  };
};

interface MatchCardProps {
  match: Match;
  isSelected: boolean;
  onSelect: (matchId: string) => void;
  onOddsRefreshed: (matchId: string, odds: Odds, status?: string, statusShort?: string) => void;
}

export const MatchCard: React.FC<MatchCardProps> = ({
  match, isSelected, onSelect, onOddsRefreshed
}) => {
  const [refreshingOdds, setRefreshingOdds] = useState(false);

  const homeLogoUrl = getTeamLogoUrl(match.home_team.logo);
  const awayLogoUrl = getTeamLogoUrl(match.away_team.logo);
  const statusInfo = getStatusInfo(match.status_short || 'NS');

  const hasOdds = match.odds && Object.keys(match.odds).length > 0;
  const bookmakerEntries = Object.entries(match.odds || {});
  const bestOdds = hasOdds ? getBestOdds(match.odds) : null;

  const handleRefreshOdds = useCallback(async (e: React.MouseEvent) => {
    e.stopPropagation();
    setRefreshingOdds(true);
    try {
      const response = await matchesApi.refreshMatchOdds(match.id);
      if (response.success && response.odds) {
        onOddsRefreshed(
          match.id,
          response.odds as Odds,
          response.status,
          response.status_short
        );
      }
    } catch (error) {
      console.error(`Erro ao atualizar odds para ${match.id}:`, error);
    } finally {
      setRefreshingOdds(false);
    }
  }, [match.id, onOddsRefreshed]);

  return (
    <div
      className={`match-card ${isSelected ? 'selected' : ''}`}
      onClick={() => onSelect(match.id)}
    >
      <div className="match-header">
        <div className="match-league">
          <span className="league-logo">{getLeagueLogo(match.league.name)}</span>
          <span>{match.league.name}</span>
          {match.round && <span className="match-round">• {match.round.name}</span>}
        </div>
        <span className={`match-status-badge ${statusInfo.className}`}>
          {statusInfo.label}
        </span>
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
          }} />
          <span className="team-name">{match.home_team.name}</span>
        </div>
        <span className="match-vs">vs</span>
        <div className="team">
          <img src={awayLogoUrl} alt={match.away_team.name} className="team-logo-img" onError={(e) => {
            e.currentTarget.style.display = 'none';
          }} />
          <span className="team-name">{match.away_team.name}</span>
        </div>
      </div>

      <div className="match-venue">
        🏟️ {match.venue?.name || 'Estádio não informado'}
      </div>

      {/* Tabela comparativa de odds */}
      <div className="match-odds">
        {hasOdds && bestOdds ? (
          <>
            <div className="odds-header">
              <span className="odds-compare-title">📊 Comparativo de Odds</span>
              <button
                className="odds-refresh-btn"
                onClick={handleRefreshOdds}
                disabled={refreshingOdds}
                title="Atualizar odds e status"
              >
                {refreshingOdds ? '⏳' : '🔄'}
              </button>
            </div>
            <table className="odds-compare-table">
              <thead>
                <tr>
                  <th className="odds-col-bookmaker">Casa</th>
                  <th className="odds-col-value">1</th>
                  <th className="odds-col-value">X</th>
                  <th className="odds-col-value">2</th>
                </tr>
              </thead>
              <tbody>
                {bookmakerEntries.map(([bkId, bkOdds]) => {
                  const meta = BOOKMAKER_META[bkId] || { name: bkId, logo: '🎰' };
                  return (
                    <tr key={bkId}>
                      <td className="odds-col-bookmaker">
                        <span className="bk-logo">{meta.logo}</span>
                        <span className="bk-name">{meta.name}</span>
                      </td>
                      <td className={`odds-col-value ${bkOdds.home === bestOdds.home ? 'best-odd' : ''}`}>
                        {bkOdds.home?.toFixed(2) || '-'}
                      </td>
                      <td className={`odds-col-value ${bkOdds.draw === bestOdds.draw ? 'best-odd' : ''}`}>
                        {bkOdds.draw?.toFixed(2) || '-'}
                      </td>
                      <td className={`odds-col-value ${bkOdds.away === bestOdds.away ? 'best-odd' : ''}`}>
                        {bkOdds.away?.toFixed(2) || '-'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </>
        ) : (
          <div className="odds-loading-placeholder">
            <span className="odds-loading-spinner">⏳</span>
            <span>Carregando odds...</span>
          </div>
        )}
      </div>
    </div>
  );
};

