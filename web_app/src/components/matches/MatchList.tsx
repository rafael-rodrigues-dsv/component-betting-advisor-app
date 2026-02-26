/**
 * MatchList Component
 */
import React, { useMemo, useState, useEffect } from 'react';
import type { Match, League, Odds } from '../../types';
import type { PeriodDays } from '../../hooks/useMatches';
import { MatchCard } from './MatchCard';
import { LeagueMultiSelect } from './LeagueMultiSelect';
import { StatusMultiSelect } from './StatusMultiSelect';
import { Loading } from '../common/Loading';

interface MatchListProps {
  matches: Match[];
  selectedMatches: Set<string>;
  onSelectMatch: (matchId: string) => void;
  onSelectAll: (matchIds: string[]) => void;
  onDeselectAll: () => void;
  analyzing: boolean;
  onAnalyze: () => void;
  // Filters
  leagues: League[];
  selectedLeagues: Set<string>;
  onLeaguesChange: (leagues: Set<string>) => void;
  selectedStatuses: Set<string>;
  onStatusesChange: (statuses: Set<string>) => void;
  // Period selector
  preloading: boolean;
  selectedPeriod: PeriodDays | null;
  dataLoaded: boolean;
  onFetchByPeriod: (days: PeriodDays) => void;
  onOddsRefreshed: (matchId: string, odds: Odds, status?: string, statusShort?: string, elapsed?: number | null, goals?: { home: number | null; away: number | null }) => void;
  // Odds background loading
  loadingOdds: boolean;
  oddsProgress: { loaded: number; total: number } | null;
  livePolling: boolean;
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
  onSelectAll,
  onDeselectAll,
  analyzing,
  onAnalyze,
  leagues,
  selectedLeagues,
  onLeaguesChange,
  selectedStatuses,
  onStatusesChange,
  preloading,
  selectedPeriod,
  dataLoaded,
  onFetchByPeriod,
  onOddsRefreshed,
  loadingOdds,
  oddsProgress,
  livePolling,
}) => {
  // Estado para controlar quais datas estão expandidas (por padrão, todas expandidas)
  const [expandedDates, setExpandedDates] = useState<Set<string>>(new Set());

  // Contagem de status disponíveis nos matches (para badges no dropdown)
  const availableStatuses = useMemo(() => {
    const counts = new Map<string, number>();
    matches.forEach(m => {
      const s = m.status_short || 'NS';
      counts.set(s, (counts.get(s) || 0) + 1);
    });
    return counts;
  }, [matches]);

  // Filtra jogos por ligas e status selecionados (client-side)
  const filteredMatches = useMemo(() => {
    let filtered = matches;
    if (selectedLeagues.size > 0) {
      filtered = filtered.filter(match => selectedLeagues.has(match.league.id));
    }
    if (selectedStatuses.size > 0) {
      filtered = filtered.filter(match => selectedStatuses.has(match.status_short || 'NS'));
    }
    return filtered;
  }, [matches, selectedLeagues, selectedStatuses]);

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

  // Toggle seleção de todos os jogos de uma data
  const toggleSelectDate = (_dateKey: string, dateMatches: Match[]) => {
    const dateMatchIds = dateMatches.map(m => m.id);
    const allSelected = dateMatchIds.every(id => selectedMatches.has(id));
    if (allSelected) {
      // Deseleciona todos do dia
      dateMatchIds.forEach(id => {
        if (selectedMatches.has(id)) onSelectMatch(id);
      });
    } else {
      // Seleciona todos do dia que ainda não estão selecionados
      const toSelect = dateMatchIds.filter(id => !selectedMatches.has(id));
      onSelectAll(toSelect);
    }
  };

  // Selecionar/Deselecionar todos os filtrados
  const handleSelectAll = () => {
    const allFilteredIds = filteredMatches.map(m => m.id);
    const allSelected = allFilteredIds.every(id => selectedMatches.has(id));
    if (allSelected) {
      onDeselectAll();
    } else {
      onSelectAll(allFilteredIds);
    }
  };

  const allFilteredSelected = filteredMatches.length > 0 && filteredMatches.every(m => selectedMatches.has(m.id));

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
            ✅ Dados carregados para <strong>{selectedPeriod} dias</strong> — {filteredMatches.length} jogos {(selectedLeagues.size > 0 || selectedStatuses.size > 0) ? `(de ${matches.length} total)` : 'encontrados'}
            {livePolling && !loadingOdds && (
              <span className="live-polling-indicator">🔴 Ao vivo — atualizando a cada 5s</span>
            )}
            {loadingOdds && oddsProgress && (
              <div className="odds-loading-bar">
                <div className="odds-loading-text">
                  📊 Carregando odds: {oddsProgress.loaded}/{oddsProgress.total} datas
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
              <label>🏆 Campeonatos:</label>
              <LeagueMultiSelect
                leagues={leagues}
                selectedLeagues={selectedLeagues}
                onChange={onLeaguesChange}
              />
            </div>
            <div className="filter-group">
              <label>📊 Status:</label>
              <StatusMultiSelect
                selectedStatuses={selectedStatuses}
                onChange={onStatusesChange}
                availableStatuses={availableStatuses}
              />
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
            <div className="actions-bar-right">
              {filteredMatches.length > 0 && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={handleSelectAll}
                  title={allFilteredSelected ? 'Deselecionar Todos' : 'Selecionar Todos'}
                >
                  {allFilteredSelected ? '☐ Deselecionar Todos' : '☑️ Selecionar Todos'}
                </button>
              )}
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
          {matchesByDate.map(([date, dateMatches]) => {
            const dateMatchIds = dateMatches.map(m => m.id);
            const allDaySelected = dateMatchIds.every(id => selectedMatches.has(id));
            const someDaySelected = dateMatchIds.some(id => selectedMatches.has(id));

            return (
              <div key={date} className="matches-date-group">
                <div className="date-header">
                  <label
                    className="date-checkbox-label"
                    onClick={(e) => { e.stopPropagation(); toggleSelectDate(date, dateMatches); }}
                  >
                    <span className={`date-checkbox ${allDaySelected ? 'checked' : someDaySelected ? 'partial' : ''}`}>
                      {allDaySelected ? '☑️' : someDaySelected ? '▪️' : '☐'}
                    </span>
                  </label>
                  <div className="date-header-content" onClick={() => toggleDateExpand(date)}>
                    <span className="date-icon">📅</span>
                    <h3 className="date-title">{formatDateHeader(date)}</h3>
                    <span className="date-count">{dateMatches.length} {dateMatches.length === 1 ? 'jogo' : 'jogos'}</span>
                    <span className="expand-toggle">
                      {expandedDates.has(date) ? '▼' : '►'}
                    </span>
                  </div>
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
          );
          })}
        </div>
      )}
    </>
  );
};

