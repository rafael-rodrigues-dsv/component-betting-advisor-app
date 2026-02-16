/**
 * MatchList Component
 */
import React, { useMemo, useState, useEffect } from 'react';
import type { Match, League, Bookmaker, Strategy } from '../../types';
import { MatchCard } from './MatchCard';
import { Loading } from '../common/Loading';

interface MatchListProps {
  matches: Match[];
  selectedMatches: Set<string>;
  onSelectMatch: (matchId: string) => void;
  loading: boolean;
  analyzing: boolean;
  onAnalyze: () => void;
  // Filters
  strategy: Strategy;
  onStrategyChange: (strategy: Strategy) => void;
  leagues: League[];
  selectedLeague: string;
  onLeagueChange: (leagueId: string) => void;
  bookmakers: Bookmaker[];
  selectedBookmaker: string;
  onBookmakerChange: (bookmakerId: string) => void;
}

// Função auxiliar para formatar data
const formatDateHeader = (dateStr: string): string => {
  const matchDate = new Date(dateStr);
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const matchDateOnly = new Date(matchDate);
  matchDateOnly.setHours(0, 0, 0, 0);

  // Compara datas
  if (matchDateOnly.getTime() === today.getTime()) {
    return `Hoje - ${matchDate.toLocaleDateString('pt-BR', { 
      weekday: 'long', 
      day: '2-digit', 
      month: 'long' 
    })}`;
  } else if (matchDateOnly.getTime() === tomorrow.getTime()) {
    return `Amanhã - ${matchDate.toLocaleDateString('pt-BR', { 
      weekday: 'long', 
      day: '2-digit', 
      month: 'long' 
    })}`;
  }

  return matchDate.toLocaleDateString('pt-BR', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });
};

export const MatchList: React.FC<MatchListProps> = ({
  matches,
  selectedMatches,
  onSelectMatch,
  loading,
  analyzing,
  onAnalyze,
  strategy,
  onStrategyChange,
  leagues,
  selectedLeague,
  onLeagueChange,
  bookmakers,
  selectedBookmaker,
  onBookmakerChange,
}) => {
  // Estado para controlar quais datas estão expandidas (por padrão, todas expandidas)
  const [expandedDates, setExpandedDates] = useState<Set<string>>(new Set());
  const [hasInitialized, setHasInitialized] = useState(false);

  // Agrupa jogos por data
  const matchesByDate = useMemo(() => {
    const grouped: Record<string, Match[]> = {};

    matches.forEach(match => {
      // Extrai apenas a data (YYYY-MM-DD) do timestamp ISO
      const matchDate = new Date(match.date);
      const dateKey = matchDate.toISOString().split('T')[0]; // YYYY-MM-DD

      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(match);
    });

    // Ordena os jogos dentro de cada data por horário
    Object.keys(grouped).forEach(dateKey => {
      grouped[dateKey].sort((a, b) => {
        const timeA = new Date(a.date).getTime();
        const timeB = new Date(b.date).getTime();
        return timeA - timeB;
      });
    });

    // Retorna array ordenado por data
    return Object.entries(grouped).sort(([dateA], [dateB]) =>
      dateA.localeCompare(dateB)
    );
  }, [matches]);

  // Inicializa todas as datas como expandidas APENAS na primeira renderização
  useEffect(() => {
    if (matchesByDate.length > 0 && !hasInitialized) {
      const allDates = new Set(matchesByDate.map(([date]) => date));
      setExpandedDates(allDates);
      setHasInitialized(true);
    }
  }, [matchesByDate, hasInitialized]);

  // Toggle expand/collapse de uma data
  const toggleDateExpand = (dateKey: string) => {
    setExpandedDates(prev => {
      const newSet = new Set(prev);
      if (newSet.has(dateKey)) {
        newSet.delete(dateKey);
      } else {
        newSet.add(dateKey);
      }
      return newSet;
    });
  };

  // Expandir/Colapsar todas
  const toggleAll = () => {
    if (expandedDates.size === matchesByDate.length) {
      // Todas expandidas, minimizar todas
      setExpandedDates(new Set());
    } else {
      // Expandir todas
      const allDates = new Set(matchesByDate.map(([date]) => date));
      setExpandedDates(allDates);
    }
  };

  return (
    <>
      <div className="filters-bar">
        {/* ...existing filters code... */}
        <div className="filter-group">
          <label>🎯 Estratégia:</label>
          <select value={strategy} onChange={(e) => onStrategyChange(e.target.value as Strategy)}>
            <option value="BALANCED">⚖️ Balanceada</option>
            <option value="CONSERVATIVE">🛡️ Conservadora</option>
            <option value="VALUE_BET">💰 Value Bet</option>
            <option value="AGGRESSIVE">🔥 Agressiva</option>
          </select>
        </div>
        <div className="filter-group">
          <label>🏆 Campeonato:</label>
          <select value={selectedLeague} onChange={(e) => onLeagueChange(e.target.value)}>
            <option value="all">Todos</option>
            {leagues.map(l => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label>🎰 Casa:</label>
          <select value={selectedBookmaker} onChange={(e) => onBookmakerChange(e.target.value)}>
            {bookmakers.map(b => <option key={b.id} value={b.id}>{b.logo} {b.name}</option>)}
          </select>
        </div>
      </div>

      <div className="actions-bar">
        <button
          className="btn btn-primary"
          disabled={selectedMatches.size === 0 || analyzing}
          onClick={onAnalyze}
        >
          {analyzing ? '⏳ Analisando...' : '🔍 Analisar Selecionados'}
        </button>
        {matches.length > 0 && matchesByDate.length > 1 && (
          <button
            className="btn btn-secondary btn-sm"
            onClick={toggleAll}
            title={expandedDates.size === matchesByDate.length ? 'Minimizar Todas' : 'Expandir Todas'}
          >
            {expandedDates.size === matchesByDate.length ? '📁 Minimizar Todas' : '📂 Expandir Todas'}
          </button>
        )}
        {selectedMatches.size > 0 && (
          <span className="selected-count">
            <strong>{selectedMatches.size} selecionado{selectedMatches.size > 1 ? 's' : ''}</strong>
          </span>
        )}
      </div>

      {loading ? (
        <Loading message="Carregando jogos..." />
      ) : matches.length === 0 ? (
        <div className="empty-state"><h3>Nenhum jogo disponível</h3></div>
      ) : (
        <div className="matches-container">
          {matchesByDate.map(([date, dateMatches]) => (
            <div key={date} className="matches-date-group">
              <div className="date-header" onClick={() => toggleDateExpand(date)}>
                <span className="date-icon">📅</span>
                <h3 className="date-title">{formatDateHeader(dateMatches[0].date)}</h3>
                <span className="date-count">{dateMatches.length} {dateMatches.length === 1 ? 'jogo' : 'jogos'}</span>
                <span className="expand-toggle">
                  {expandedDates.has(date) ? '▼' : '►'}
                </span>
              </div>
              {expandedDates.has(date) && (
                <div className="matches-grid">
                  {dateMatches.map((match) => (
                    <MatchCard
                      key={match.id}
                      match={match}
                      isSelected={selectedMatches.has(match.id)}
                      onSelect={onSelectMatch}
                      selectedBookmaker={selectedBookmaker}
                    />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </>
  );
};

