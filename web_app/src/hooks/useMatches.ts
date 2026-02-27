/**
 * useMatches Hook
 *
 * Fluxo:
 * 1. FASE 1 (rápida): POST /preload/fetch → fixtures only → mostra jogos na tela
 * 2. FASE 2 (sob demanda): POST /preload/odds/league → odds por liga, quando selecionada no carrossel
 *    Após concluir, re-busca GET /matches para atualizar odds na UI
 *
 * Botão refresh atualiza odds + status de uma partida específica.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import { matchesApi, preloadApi } from '../services/api';
import type { Match, League, Bookmaker, Odds } from '../types';

export type PeriodDays = 1 | 3 | 7;

const LIVE_POLL_INTERVAL = 5000; // 5 segundos

export function useMatches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [bookmakers, setBookmakers] = useState<Bookmaker[]>([]);
  const [loading, setLoading] = useState(false);
  const [preloading, setPreloading] = useState(false);
  const [loadingOdds, setLoadingOdds] = useState(false);
  const [oddsProgress, setOddsProgress] = useState<{ loaded: number; total: number } | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodDays | null>(null);
  const [dataLoaded, setDataLoaded] = useState(false);

  // Controla cancelamento se o usuário trocar de período/liga durante carregamento de odds
  const oddsAbortRef = useRef(false);
  // Guarda date_from e date_to do período atual
  const currentRangeRef = useRef<{ from: string; to: string } | null>(null);
  // Guarda as datas do período atual (para usar na busca de odds por liga)
  const currentDatesRef = useRef<string[]>([]);
  // Ligas cujas odds já foram carregadas (evita re-buscar)
  const oddsLoadedLeaguesRef = useRef<Set<string>>(new Set());
  // Live polling interval
  const liveIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [livePolling, setLivePolling] = useState(false);

  const loadMatches = useCallback(async (dateFrom?: string, dateTo?: string): Promise<Match[]> => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const url = `/api/v1/matches${params.toString() ? '?' + params.toString() : ''}`;
      const res = await fetch(url);
      const response = await res.json();

      const loadedMatches: Match[] = response.matches || [];
      console.log(`📊 ${loadedMatches.length} jogos carregados`);
      setMatches(loadedMatches);
      return loadedMatches;
    } catch (error) {
      console.error('Erro ao carregar jogos:', error);
      setMatches([]);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const loadBookmakers = useCallback(async () => {
    try {
      const data = await matchesApi.getBookmakers();
      setBookmakers(data.bookmakers || []);
    } catch (error) {
      console.error('Erro ao carregar casas:', error);
    }
  }, []);

  const updateMatchOdds = useCallback((matchId: string, odds: Odds) => {
    setMatches(prev => prev.map(m =>
      m.id === matchId ? { ...m, odds } : m
    ));
  }, []);

  /**
   * Atualiza odds + status + placar de uma partida no state.
   * Chamado pelo MatchCard ao dar refresh (POST).
   */
  const updateMatchOddsAndStatus = useCallback((
    matchId: string,
    odds: Odds,
    status?: string,
    statusShort?: string,
    elapsed?: number | null,
    goals?: { home: number | null; away: number | null }
  ) => {
    setMatches(prev => prev.map(m => {
      if (m.id !== matchId) return m;
      return {
        ...m,
        odds,
        ...(status ? { status } : {}),
        ...(statusShort ? { status_short: statusShort } : {}),
        ...(elapsed !== undefined ? { elapsed } : {}),
        ...(goals ? { goals } : {}),
      };
    }));
  }, []);

  /**
   * Carrega odds de ligas específicas sob demanda.
   * Chamado quando o usuário seleciona ligas no carrossel.
   * Usa POST /preload/odds/league — busca odds só da liga+data (equilibrado).
   *
   * Apenas busca ligas que ainda não tiveram odds carregadas.
   */
  const loadOddsForLeagues = useCallback(async (leagueIds: string[]) => {
    // Filtra ligas que já foram carregadas
    const newLeagueIds = leagueIds.filter(id => !oddsLoadedLeaguesRef.current.has(id));
    if (newLeagueIds.length === 0) return;

    const range = currentRangeRef.current;
    const dates = currentDatesRef.current;
    if (!range || dates.length === 0) return;

    setLoadingOdds(true);
    setOddsProgress({ loaded: 0, total: newLeagueIds.length });
    oddsAbortRef.current = false;

    console.log(`📊 Carregando odds para ${newLeagueIds.length} liga(s) sob demanda...`);

    let loaded = 0;

    for (const leagueId of newLeagueIds) {
      if (oddsAbortRef.current) {
        console.log('⚠️ Carregamento de odds cancelado');
        break;
      }

      try {
        const result = await preloadApi.fetchOddsByLeague(leagueId, dates);
        loaded++;
        setOddsProgress({ loaded, total: newLeagueIds.length });

        if (result.success) {
          oddsLoadedLeaguesRef.current.add(leagueId);
          console.log(`  ✅ Odds liga ${leagueId}: ${result.total_odds} fixtures${result.from_cache ? ' (cache)' : ''}`);
        }

        // Re-busca matches para atualizar UI com odds
        if (!oddsAbortRef.current) {
          await loadMatches(range.from, range.to);
        }
      } catch (error) {
        console.error(`  ❌ Erro odds liga ${leagueId}:`, error);
        loaded++;
        setOddsProgress({ loaded, total: newLeagueIds.length });
      }
    }

    setLoadingOdds(false);
    setOddsProgress(null);
    console.log(`✅ Odds concluído: ${loaded}/${newLeagueIds.length} ligas`);
  }, [loadMatches]);

  /**
   * Busca updates de jogos ao vivo e atualiza o state.
   */
  const pollLiveUpdates = useCallback(async () => {
    try {
      const response = await matchesApi.getLiveUpdates();
      if (response.success && response.updates.length > 0) {
        setMatches(prev => {
          let changed = false;
          const updated = prev.map(m => {
            const update = response.updates.find(u => u.id === m.id);
            if (update) {
              changed = true;
              return {
                ...m,
                status: update.status,
                status_short: update.status_short,
                elapsed: update.elapsed,
                goals: update.goals,
              };
            }
            return m;
          });
          return changed ? updated : prev;
        });
      }
    } catch (error) {
      // Silencioso — polling não deve interromper a UX
      console.debug('Live poll error:', error);
    }
  }, []);

  /**
   * Inicia polling de jogos ao vivo a cada 5 segundos.
   */
  const startLivePolling = useCallback(() => {
    if (liveIntervalRef.current) {
      clearInterval(liveIntervalRef.current);
    }

    const hasLiveMatches = true; // Sempre inicia, o backend filtra

    if (hasLiveMatches) {
      console.log('🔴 Iniciando polling de jogos ao vivo (5s)...');
      setLivePolling(true);
      pollLiveUpdates();
      liveIntervalRef.current = setInterval(pollLiveUpdates, LIVE_POLL_INTERVAL);
    }
  }, [pollLiveUpdates]);

  /**
   * Para o polling de jogos ao vivo.
   */
  const stopLivePolling = useCallback(() => {
    if (liveIntervalRef.current) {
      clearInterval(liveIntervalRef.current);
      liveIntervalRef.current = null;
    }
    setLivePolling(false);
    console.log('⏹️ Polling de jogos ao vivo parado');
  }, []);

  // Cleanup ao desmontar o componente
  useEffect(() => {
    return () => {
      if (liveIntervalRef.current) {
        clearInterval(liveIntervalRef.current);
      }
    };
  }, []);

  /**
   * Carrega dados para um período (1, 3 ou 7 dias).
   *
   * APENAS FASE 1: POST /preload/fetch → fixtures (rápido) → mostra jogos
   * Odds são carregados sob demanda quando o usuário seleciona ligas no carrossel.
   */
  const fetchByPeriod = useCallback(async (days: PeriodDays) => {
    // Cancela odds background anterior e live polling
    oddsAbortRef.current = true;
    stopLivePolling();

    setPreloading(true);
    setSelectedPeriod(days);
    setDataLoaded(false);
    setLoadingOdds(false);
    setOddsProgress(null);
    // Reset ligas com odds carregadas
    oddsLoadedLeaguesRef.current = new Set();

    try {
      // === FASE 1: Fixtures (rápido) ===
      console.log(`📥 FASE 1 — Carregando fixtures de ${days} dias...`);
      const preloadResult = await preloadApi.fetch(days);

      if (!preloadResult.success) {
        console.error('❌ Erro no preload:', preloadResult.message);
        setPreloading(false);
        return;
      }

      const dateFrom = preloadResult.date_from!;
      const dateTo = preloadResult.date_to!;
      const dates = preloadResult.dates || [];

      console.log(`✅ Fixtures concluído: ${dateFrom} até ${dateTo} (${preloadResult.total_fixtures} fixtures)`);

      // Ligas dinâmicas
      if (preloadResult.leagues && preloadResult.leagues.length > 0) {
        setLeagues(preloadResult.leagues);
        console.log(`🏆 ${preloadResult.leagues.length} ligas dinâmicas`);
      } else {
        const leaguesData = await matchesApi.getLeagues();
        setLeagues(leaguesData.leagues || []);
      }

      // Carrega matches (sem odds — odds sob demanda)
      currentRangeRef.current = { from: dateFrom, to: dateTo };
      currentDatesRef.current = dates;
      await loadMatches(dateFrom, dateTo);
      await loadBookmakers();

      setDataLoaded(true);
      setPreloading(false);

      // NÃO carrega odds automaticamente — será sob demanda via loadOddsForLeagues

    } catch (error) {
      console.error('Erro ao carregar período:', error);
      setMatches([]);
      setPreloading(false);
    }
  }, [loadMatches, loadBookmakers, stopLivePolling]);

  return {
    matches,
    leagues,
    bookmakers,
    loading: loading || preloading,
    preloading,
    loadingOdds,
    oddsProgress,
    livePolling,
    selectedPeriod,
    dataLoaded,
    loadMatches,
    fetchByPeriod,
    loadOddsForLeagues,
    updateMatchOdds,
    updateMatchOddsAndStatus,
    startLivePolling,
    stopLivePolling,
  };
}
