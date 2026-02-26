/**
 * MatchList Component
 */
import React, { useMemo, useState, useEffect } from 'react';
import type { Match, League, Strategy, Odds } from '../../types';
import type { PeriodDays } from '../../hooks/useMatches';
import { MatchCard } from './MatchCard';
import { Loading } from '../common/Loading';

interface MatchListProps {
  matches: Match[];
  selectedMatches: Set<string>;
  onSelectMatch: (matchId: string) => void;
  analyzing: boolean;
  onAnalyze: () => void;
  // Filters
  strategy: Strategy;
  onStrategyChange: (strategy: Strategy) => void;
  leagues: League[];
  selectedLeague: string;
  onLeagueChange: (leagueId: string) => void;
  // Period selector
  preloading: boolean;
  selectedPeriod: PeriodDays | null;
  dataLoaded: boolean;
  onFetchByPeriod: (days: PeriodDays) => void;
  onOddsRefreshed: (matchId: string, odds: Odds, status?: string, statusShort?: string) => void;
  // Odds batch loading
  loadingOdds: boolean;
  oddsProgress: { loaded: number; total: number } | null;
}

// Função auxiliar para formatar data
const formatDateHeader = (dateStr: string): string => {
  // dateStr vem no formato YYYY-MM-DD (já extraído no agrupamento)
  const [year, month, day] = dateStr.split('-').map(Number);

  // Cria data local (sem timezone issues)
  const matchDate = new Date(year, month - 1, day);

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
  analyzing,
  onAnalyze,
  strategy,
  onStrategyChange,
  leagues,
  selectedLeague,
  onLeagueChange,
  preloading,
  selectedPeriod,
  dataLoaded,
  onFetchByPeriod,
  onOddsRefreshed,
  loadingOdds,
  oddsProgress,
}) => {
  // Estado para controlar quais datas estão expandidas (por padrão, todas expandidas)
  const [expandedDates, setExpandedDates] = useState<Set<string>>(new Set());

  // Filtra jogos por liga selecionada (client-side)
  const filteredMatches = useMemo(() => {
    if (!selectedLeague || selectedLeague === 'all') {
      return matches;
    }
    return matches.filter(match => match.league.id === selectedLeague);
  }, [matches, selectedLeague]);

  // Agrupa jogos filtrados por data
  const matchesByDate = useMemo(() => {
    const grouped: Record<string, Match[]> = {};

    filteredMatches.forEach(match => {
      // Extrai apenas a data (YYYY-MM-DD) diretamente da string, sem conversão de Date
      // Isso evita problemas com timezone
      const dateKey = match.date.split('T')[0]; // YYYY-MM-DD

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
  }, [filteredMatches]);

  // Inicializa todas as datas como expandidas quando novos dados carregam
  useEffect(() => {
    if (matchesByDate.length > 0) {
      const allDates = new Set(matchesByDate.map(([date]) => date));
      setExpandedDates(allDates);
    }
  }, [dataLoaded, matchesByDate.length]);

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

  const periodOptions: { days: 3 | 7 | 14; label: string; icon: string; description: string }[] = [
    { days: 3, label: '3 Dias', icon: '⚡', description: 'Jogos próximos' },
    { days: 7, label: '7 Dias', icon: '📅', description: 'Próxima semana' },
    { days: 14, label: '14 Dias', icon: '📆', description: 'Duas semanas' },
  ];

  return (
    <>
      {/* Period Selector - Sempre visível */}
      <div className="period-selector">
        <div className="period-selector-header">
          <h3>📥 Carregar Jogos</h3>
          <p>Selecione o período para buscar os jogos disponíveis</p>
        </div>
        <div className="period-buttons">
          {periodOptions.map(({ days, label, icon, description }) => (
            <button
              key={days}
              className={`period-btn ${selectedPeriod === days ? 'active' : ''}`}
              onClick={() => onFetchByPeriod(days)}
              disabled={preloading}
            >
              <span className="period-btn-icon">{icon}</span>
              <span className="period-btn-label">{label}</span>
              <span className="period-btn-desc">{description}</span>
              {preloading && selectedPeriod === days && (
                <span className="period-btn-loading">⏳</span>
              )}
            </button>
          ))}
        </div>
        {selectedPeriod && dataLoaded && (
          <div className="period-info">
            ✅ Dados carregados para <strong>{selectedPeriod} dias</strong> — {filteredMatches.length} jogos {selectedLeague !== 'all' ? `(de ${matches.length} total)` : 'encontrados'}
            {loadingOdds && oddsProgress && (
              <div className="odds-loading-bar">
                <div className="odds-loading-text">
                  📊 Carregando odds: {oddsProgress.loaded}/{oddsProgress.total}
                </div>
                <div className="odds-progress-track">
                  <div
                    className="odds-progress-fill"
                    style={{ width: `${(oddsProgress.loaded / oddsProgress.total) * 100}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Filters & Content - Só aparecem depois de carregar dados */}
      {dataLoaded && (
        <>
          <div className="filters-bar">
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
          </div>

          <div className="actions-bar">
            <div className="actions-bar-left">
              <button
                className="btn btn-primary"
                disabled={selectedMatches.size === 0 || analyzing}
                onClick={onAnalyze}
              >
                {analyzing ? '⏳ Analisando...' : '🔍 Analisar Selecionados'}
              </button>
              {selectedMatches.size > 0 && (
                <span className="selected-count">
                  <strong>{selectedMatches.size} selecionado{selectedMatches.size > 1 ? 's' : ''}</strong>
                </span>
              )}
            </div>
            {matches.length > 0 && matchesByDate.length > 1 && (
              <button
                className="btn btn-secondary btn-sm"
                onClick={toggleAll}
                title={expandedDates.size === matchesByDate.length ? 'Minimizar Todas' : 'Expandir Todas'}
              >
                {expandedDates.size === matchesByDate.length ? '📁 Minimizar Todas' : '📂 Expandir Todas'}
              </button>
            )}
          </div>
        </>
      )}

      {preloading ? (
        <Loading message="Carregando jogos do período selecionado..." />
      ) : !dataLoaded ? (
        <div className="empty-state">
          <div className="empty-state-icon">🏟️</div>
          <h3>Selecione um período acima para carregar os jogos</h3>
          <p>Escolha entre 3, 7 ou 14 dias para buscar as partidas disponíveis</p>
        </div>
      ) : filteredMatches.length === 0 ? (
        <div className="empty-state">
          <h3>Nenhum jogo disponível para o período selecionado</h3>
          <p>Tente selecionar um período maior ou outro campeonato</p>
        </div>
      ) : (
        <div className="matches-container">
          {matchesByDate.map(([date, dateMatches]) => (
            <div key={date} className="matches-date-group">
              <div className="date-header" onClick={() => toggleDateExpand(date)}>
                <span className="date-icon">📅</span>
                <h3 className="date-title">{formatDateHeader(date)}</h3>
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
                      onOddsRefreshed={onOddsRefreshed}
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

