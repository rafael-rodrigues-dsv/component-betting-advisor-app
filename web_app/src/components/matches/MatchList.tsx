/**
 * MatchList Component
 *
 * Fluxo: Seleciona período → Carrossel de ligas → Seleciona liga → Exibe jogos da liga
 * Padrão: nenhuma liga selecionada = nenhum jogo exibido
 */
import React, { useMemo, useState, useEffect } from 'react';
import type { Match, League, Odds } from '../../types';
import type { PeriodDays } from '../../hooks/useMatches';
import { MatchCard } from './MatchCard';
import { LeagueCarousel } from './LeagueCarousel';
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
  onLoadOddsForLeagues: (leagueIds: string[]) => Promise<void>;
  onOddsRefreshed: (matchId: string, odds: Odds, status?: string, statusShort?: string, elapsed?: number | null, goals?: { home: number | null; away: number | null }) => void;
  // Odds background loading
  loadingOdds: boolean;
  oddsProgress: { loaded: number; total: number } | null;
  livePolling: boolean;
}

// Função auxiliar para formatar data
const formatDateHeader = (dateStr: string): string => {
  const [year, month, day] = dateStr.split('-').map(Number);
  const matchDate = new Date(year, month - 1, day);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const matchDateOnly = new Date(matchDate);
  matchDateOnly.setHours(0, 0, 0, 0);

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
  selectedLeagues: _selectedLeagues,
  onLeaguesChange,
  selectedStatuses,
  onStatusesChange,
  preloading,
  selectedPeriod,
  dataLoaded,
  onFetchByPeriod,
  onLoadOddsForLeagues,
  onOddsRefreshed,
  loadingOdds,
  oddsProgress,
  livePolling,
}) => {
  // Ligas selecionadas no carrossel (multi-seleção)
  const [carouselLeagueIds, setCarouselLeagueIds] = useState<Set<string>>(new Set());

  // Estado para controlar quais datas estão expandidas
  const [expandedDates, setExpandedDates] = useState<Set<string>>(new Set());

  // ── Filtros locais ──
  const [filterOdds, setFilterOdds] = useState<'all' | 'with' | 'without'>('all');
  const [filterRound, setFilterRound] = useState<string | null>(null);
  const [filterDate, setFilterDate] = useState<string | null>(null);
  const [filterTime, setFilterTime] = useState<'all' | 'morning' | 'afternoon' | 'night'>('all');

  // Toggle de liga no carrossel
  const handleToggleLeague = (leagueId: string) => {
    const isAdding = !carouselLeagueIds.has(leagueId);

    setCarouselLeagueIds(prev => {
      const newSet = new Set(prev);
      if (newSet.has(leagueId)) {
        newSet.delete(leagueId);
      } else {
        newSet.add(leagueId);
      }
      // Sincroniza com contexto
      onLeaguesChange(newSet);
      return newSet;
    });

    // Dispara carregamento de odds FORA do setState
    if (isAdding) {
      onLoadOddsForLeagues([leagueId]);
    }

    // Reset filtros ao mudar ligas
    setFilterOdds('all');
    setFilterRound(null);
    setFilterDate(null);
    setFilterTime('all');
  };

  const handleClearCarousel = () => {
    setCarouselLeagueIds(new Set());
    onLeaguesChange(new Set());
    setFilterOdds('all');
    setFilterRound(null);
    setFilterDate(null);
    setFilterTime('all');
  };

  // Seleção em lote (usado por "Selecionar todas visíveis")
  const handleSelectMultipleLeagues = (leagueIds: string[]) => {
    setCarouselLeagueIds(prev => {
      const newSet = new Set(prev);
      leagueIds.forEach(id => newSet.add(id));
      onLeaguesChange(newSet);
      return newSet;
    });
    // Dispara carregamento de odds em batch
    onLoadOddsForLeagues(leagueIds);
    // Reset filtros
    setFilterOdds('all');
    setFilterRound(null);
    setFilterDate(null);
    setFilterTime('all');
  };

  // Reset ao trocar de período
  useEffect(() => {
    setCarouselLeagueIds(new Set());
    setFilterOdds('all');
    setFilterRound(null);
    setFilterDate(null);
    setFilterTime('all');
  }, [dataLoaded]);

  // Jogos das ligas selecionadas
  const leagueMatches = useMemo(() => {
    if (carouselLeagueIds.size === 0) return [];
    return matches.filter(m => carouselLeagueIds.has(m.league.id));
  }, [matches, carouselLeagueIds]);

  // ── Opções de filtro derivadas da liga ──
  const availableStatuses = useMemo(() => {
    const counts = new Map<string, number>();
    leagueMatches.forEach(m => {
      const s = m.status_short || 'NS';
      counts.set(s, (counts.get(s) || 0) + 1);
    });
    return counts;
  }, [leagueMatches]);

  // Rodadas disponíveis (ordenadas)
  const availableRounds = useMemo(() => {
    const roundMap = new Map<string, number>();
    leagueMatches.forEach(m => {
      const roundName = m.round?.name || 'Sem rodada';
      roundMap.set(roundName, (roundMap.get(roundName) || 0) + 1);
    });
    return Array.from(roundMap.entries())
      .sort(([a], [b]) => a.localeCompare(b, 'pt-BR', { numeric: true }));
  }, [leagueMatches]);

  // Datas disponíveis
  const availableDates = useMemo(() => {
    const dateMap = new Map<string, number>();
    leagueMatches.forEach(m => {
      const dateKey = m.date.split('T')[0];
      dateMap.set(dateKey, (dateMap.get(dateKey) || 0) + 1);
    });
    return Array.from(dateMap.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [leagueMatches]);

  // Contagem com/sem odds
  const oddsCount = useMemo(() => {
    let withOdds = 0;
    let withoutOdds = 0;
    leagueMatches.forEach(m => {
      if (m.odds && Object.keys(m.odds).length > 0) withOdds++;
      else withoutOdds++;
    });
    return { withOdds, withoutOdds };
  }, [leagueMatches]);

  // Contagem por horário
  const timeCount = useMemo(() => {
    let morning = 0, afternoon = 0, night = 0;
    leagueMatches.forEach(m => {
      const hour = new Date(m.date).getHours();
      if (hour < 12) morning++;
      else if (hour < 18) afternoon++;
      else night++;
    });
    return { morning, afternoon, night };
  }, [leagueMatches]);

  // Helper para formatar label de data curta
  const formatDateChip = (dateStr: string): string => {
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(year, month - 1, day);
    const today = new Date(); today.setHours(0,0,0,0);
    const tomorrow = new Date(today); tomorrow.setDate(tomorrow.getDate() + 1);
    const dOnly = new Date(d); dOnly.setHours(0,0,0,0);
    if (dOnly.getTime() === today.getTime()) return 'Hoje';
    if (dOnly.getTime() === tomorrow.getTime()) return 'Amanhã';
    return d.toLocaleDateString('pt-BR', { weekday: 'short', day: '2-digit', month: '2-digit' });
  };

  // ── Filtragem combinada ──
  const filteredMatches = useMemo(() => {
    let filtered = leagueMatches;

    // Status
    if (selectedStatuses.size > 0) {
      filtered = filtered.filter(m => selectedStatuses.has(m.status_short || 'NS'));
    }
    // Com/Sem Odds
    if (filterOdds === 'with') {
      filtered = filtered.filter(m => m.odds && Object.keys(m.odds).length > 0);
    } else if (filterOdds === 'without') {
      filtered = filtered.filter(m => !m.odds || Object.keys(m.odds).length === 0);
    }
    // Rodada
    if (filterRound) {
      filtered = filtered.filter(m => (m.round?.name || 'Sem rodada') === filterRound);
    }
    // Data
    if (filterDate) {
      filtered = filtered.filter(m => m.date.split('T')[0] === filterDate);
    }
    // Horário
    if (filterTime !== 'all') {
      filtered = filtered.filter(m => {
        const hour = new Date(m.date).getHours();
        if (filterTime === 'morning') return hour < 12;
        if (filterTime === 'afternoon') return hour >= 12 && hour < 18;
        return hour >= 18; // night
      });
    }

    return filtered;
  }, [leagueMatches, selectedStatuses, filterOdds, filterRound, filterDate, filterTime]);

  // Conta filtros ativos
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (selectedStatuses.size > 0) count++;
    if (filterOdds !== 'all') count++;
    if (filterRound) count++;
    if (filterDate) count++;
    if (filterTime !== 'all') count++;
    return count;
  }, [selectedStatuses, filterOdds, filterRound, filterDate, filterTime]);

  const clearAllFilters = () => {
    onStatusesChange(new Set());
    setFilterOdds('all');
    setFilterRound(null);
    setFilterDate(null);
    setFilterTime('all');
  };

  // Agrupa jogos filtrados por data
  const matchesByDate = useMemo(() => {
    const grouped: Record<string, Match[]> = {};

    filteredMatches.forEach(match => {
      const dateKey = match.date.split('T')[0];
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

    return Object.entries(grouped).sort(([dateA], [dateB]) =>
      dateA.localeCompare(dateB)
    );
  }, [filteredMatches]);

  // Inicializa todas as datas como expandidas quando ligas mudam
  useEffect(() => {
    if (matchesByDate.length > 0) {
      const allDates = new Set(matchesByDate.map(([date]) => date));
      setExpandedDates(allDates);
    }
  }, [carouselLeagueIds.size, matchesByDate.length]);

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
      setExpandedDates(new Set());
    } else {
      const allDates = new Set(matchesByDate.map(([date]) => date));
      setExpandedDates(allDates);
    }
  };

  // Toggle seleção de todos os jogos de uma data (apenas com odds)
  const toggleSelectDate = (_dateKey: string, dateMatches: Match[]) => {
    const selectableMatches = dateMatches.filter(m => m.odds && Object.keys(m.odds).length > 0);
    const selectableIds = selectableMatches.map(m => m.id);
    if (selectableIds.length === 0) return;
    const allSelected = selectableIds.every(id => selectedMatches.has(id));
    if (allSelected) {
      selectableIds.forEach(id => {
        if (selectedMatches.has(id)) onSelectMatch(id);
      });
    } else {
      const toSelect = selectableIds.filter(id => !selectedMatches.has(id));
      onSelectAll(toSelect);
    }
  };

  // Selecionar/Deselecionar todos os filtrados (apenas com odds)
  const handleSelectAll = () => {
    const selectableMatches = filteredMatches.filter(m => m.odds && Object.keys(m.odds).length > 0);
    const selectableIds = selectableMatches.map(m => m.id);
    const allSelected = selectableIds.length > 0 && selectableIds.every(id => selectedMatches.has(id));
    if (allSelected) {
      onDeselectAll();
    } else {
      onSelectAll(selectableIds);
    }
  };

  const selectableFilteredMatches = filteredMatches.filter(m => m.odds && Object.keys(m.odds).length > 0);
  const allFilteredSelected = selectableFilteredMatches.length > 0 && selectableFilteredMatches.every(m => selectedMatches.has(m.id));

  const periodOptions: { days: 1 | 3 | 7; label: string; icon: string; description: string }[] = [
    { days: 1, label: 'Hoje', icon: '⚡', description: 'Jogos de hoje' },
    { days: 3, label: '3 Dias', icon: '📅', description: 'Próximos 3 dias' },
    { days: 7, label: '7 Dias', icon: '📆', description: 'Próxima semana' },
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
            ✅ Dados carregados para <strong>{selectedPeriod === 1 ? 'Hoje' : `${selectedPeriod} dias`}</strong> — {matches.length} jogos em {leagues.length} ligas
            {livePolling && !loadingOdds && (
              <span className="live-polling-indicator">🔴 Ao vivo — atualizando a cada 5s</span>
            )}
            {loadingOdds && oddsProgress && (
              <div className="odds-loading-bar">
                <div className="odds-loading-text">
                  📊 Carregando odds: {oddsProgress.loaded}/{oddsProgress.total} liga{oddsProgress.total > 1 ? 's' : ''}
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

      {/* Carrossel de Ligas — aparece após carregar dados */}
      {dataLoaded && (
        <LeagueCarousel
          leagues={leagues}
          matches={matches}
          selectedLeagueIds={carouselLeagueIds}
          onToggleLeague={handleToggleLeague}
          onSelectMultiple={handleSelectMultipleLeagues}
          onClearAll={handleClearCarousel}
        />
      )}

      {/* Filters & Actions — só aparecem quando uma liga está selecionada */}
      {dataLoaded && carouselLeagueIds.size > 0 && (
        <>
          {/* Barra de filtros */}
          {leagueMatches.length > 0 && (
            <div className="match-filters">
              {/* Header com título e limpar */}
              <div className="match-filters-header">
                <span className="match-filters-title">🔎 Filtros</span>
                {activeFilterCount > 0 && (
                  <button className="match-filters-clear" onClick={clearAllFilters}>
                    ✕ Limpar filtros ({activeFilterCount})
                  </button>
                )}
              </div>

              {/* Filtro: Status */}
              <div className="filter-row">
                <label className="filter-row-label">📊 Status:</label>
                <StatusMultiSelect
                  selectedStatuses={selectedStatuses}
                  onChange={onStatusesChange}
                  availableStatuses={availableStatuses}
                />
              </div>

              {/* Filtro: Com/Sem Odds */}
              <div className="filter-row">
                <label className="filter-row-label">🎰 Odds:</label>
                <div className="filter-chips">
                  <button
                    className={`filter-chip ${filterOdds === 'all' ? 'active' : ''}`}
                    onClick={() => setFilterOdds('all')}
                  >
                    Todas ({leagueMatches.length})
                  </button>
                  <button
                    className={`filter-chip ${filterOdds === 'with' ? 'active' : ''}`}
                    onClick={() => setFilterOdds(filterOdds === 'with' ? 'all' : 'with')}
                  >
                    ✅ Com odds ({oddsCount.withOdds})
                  </button>
                  <button
                    className={`filter-chip ${filterOdds === 'without' ? 'active' : ''}`}
                    onClick={() => setFilterOdds(filterOdds === 'without' ? 'all' : 'without')}
                  >
                    ❌ Sem odds ({oddsCount.withoutOdds})
                  </button>
                </div>
              </div>

              {/* Filtro: Rodada */}
              {availableRounds.length > 1 && (
                <div className="filter-row">
                  <label className="filter-row-label">🏁 Rodada:</label>
                  <div className="filter-chips filter-chips-scroll">
                    <button
                      className={`filter-chip ${filterRound === null ? 'active' : ''}`}
                      onClick={() => setFilterRound(null)}
                    >
                      Todas
                    </button>
                    {availableRounds.map(([round, count]) => (
                      <button
                        key={round}
                        className={`filter-chip ${filterRound === round ? 'active' : ''}`}
                        onClick={() => setFilterRound(filterRound === round ? null : round)}
                      >
                        {round} ({count})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Filtro: Data */}
              {availableDates.length > 1 && (
                <div className="filter-row">
                  <label className="filter-row-label">📅 Data:</label>
                  <div className="filter-chips filter-chips-scroll">
                    <button
                      className={`filter-chip ${filterDate === null ? 'active' : ''}`}
                      onClick={() => setFilterDate(null)}
                    >
                      Todas
                    </button>
                    {availableDates.map(([date, count]) => (
                      <button
                        key={date}
                        className={`filter-chip ${filterDate === date ? 'active' : ''}`}
                        onClick={() => setFilterDate(filterDate === date ? null : date)}
                      >
                        {formatDateChip(date)} ({count})
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Filtro: Horário */}
              <div className="filter-row">
                <label className="filter-row-label">⏰ Horário:</label>
                <div className="filter-chips">
                  <button
                    className={`filter-chip ${filterTime === 'all' ? 'active' : ''}`}
                    onClick={() => setFilterTime('all')}
                  >
                    Todos ({leagueMatches.length})
                  </button>
                  {timeCount.morning > 0 && (
                    <button
                      className={`filter-chip ${filterTime === 'morning' ? 'active' : ''}`}
                      onClick={() => setFilterTime(filterTime === 'morning' ? 'all' : 'morning')}
                    >
                      🌅 Manhã &lt;12h ({timeCount.morning})
                    </button>
                  )}
                  {timeCount.afternoon > 0 && (
                    <button
                      className={`filter-chip ${filterTime === 'afternoon' ? 'active' : ''}`}
                      onClick={() => setFilterTime(filterTime === 'afternoon' ? 'all' : 'afternoon')}
                    >
                      ☀️ Tarde 12-18h ({timeCount.afternoon})
                    </button>
                  )}
                  {timeCount.night > 0 && (
                    <button
                      className={`filter-chip ${filterTime === 'night' ? 'active' : ''}`}
                      onClick={() => setFilterTime(filterTime === 'night' ? 'all' : 'night')}
                    >
                      🌙 Noite 18h+ ({timeCount.night})
                    </button>
                  )}
                </div>
              </div>
            </div>
          )}

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
                <span className="league-match-summary">
                  {filteredMatches.length} {filteredMatches.length === 1 ? 'jogo' : 'jogos'}
                  {activeFilterCount > 0 && ` (de ${leagueMatches.length})`}
                </span>
              )}
              {filteredMatches.length > 0 && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={handleSelectAll}
                  title={allFilteredSelected ? 'Deselecionar Todos' : 'Selecionar Todos'}
                >
                  {allFilteredSelected ? '☐ Deselecionar Todos' : '☑️ Selecionar Todos'}
                </button>
              )}
              {matchesByDate.length > 1 && (
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

      {/* Content */}
      {preloading ? (
        <Loading message="Carregando jogos do período selecionado..." />
      ) : !dataLoaded ? (
        <div className="empty-state">
          <div className="empty-state-icon">🏟️</div>
          <h3>Selecione um período acima para carregar os jogos</h3>
          <p>Escolha Hoje, 3 ou 7 dias para buscar as partidas disponíveis</p>
        </div>
      ) : carouselLeagueIds.size === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">👆</div>
          <h3>Selecione um ou mais campeonatos no carrossel acima</h3>
          <p>Escolha as ligas para visualizar os jogos disponíveis no período</p>
        </div>
      ) : filteredMatches.length === 0 ? (
        <div className="empty-state">
          <h3>Nenhum jogo encontrado com os filtros atuais</h3>
          <p>Tente limpar os filtros ou selecionar outra liga</p>
          {activeFilterCount > 0 && (
            <button className="btn btn-secondary" onClick={clearAllFilters} style={{ marginTop: '12px' }}>
              ✕ Limpar todos os filtros ({activeFilterCount})
            </button>
          )}
        </div>
      ) : (
        <div className="matches-container">
          {matchesByDate.map(([date, dateMatches]) => {
            const selectableInDate = dateMatches.filter(m => m.odds && Object.keys(m.odds).length > 0);
            const selectableIds = selectableInDate.map(m => m.id);
            const allDaySelected = selectableIds.length > 0 && selectableIds.every(id => selectedMatches.has(id));
            const someDaySelected = selectableIds.some(id => selectedMatches.has(id));

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

