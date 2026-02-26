/**
 * useMatches Hook
 *
 * Não carrega automaticamente. O usuário deve selecionar um período (3, 7 ou 14 dias)
 * para disparar o preload e depois buscar os matches.
 *
 * Fluxo:
 * 1. Preload fixtures (sem odds)
 * 2. Carrega matches do backend
 * 3. Dispara batch de odds para TODOS os matches carregados
 * 4. Odds ficam no cache do backend — próximas vezes vêm do cache
 * 5. Botão refresh atualiza odds + status de uma partida específica
 */
import { useState, useCallback, useRef } from 'react';
import { matchesApi, preloadApi } from '../services/api';
import type { Match, League, Bookmaker, Odds } from '../types';

export type PeriodDays = 3 | 7 | 14;

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

  // Ref para controlar cancelamento se o usuário trocar de período
  const batchAbortRef = useRef(false);

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
      console.log(`📊 ${loadedMatches.length} jogos carregados (sem odds)`);
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

  const loadLeagues = useCallback(async () => {
    try {
      const data = await matchesApi.getLeagues();
      setLeagues(data.leagues || []);
    } catch (error) {
      console.error('Erro ao carregar ligas:', error);
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

  /**
   * Carrega odds em lote para todos os matches.
   * Faz em chunks para não sobrecarregar a API.
   */
  const loadAllOdds = useCallback(async (matchList: Match[]) => {
    if (matchList.length === 0) return;

    const fixtureIds = matchList.map(m => m.id);
    const CHUNK_SIZE = 10;
    const chunks: string[][] = [];

    for (let i = 0; i < fixtureIds.length; i += CHUNK_SIZE) {
      chunks.push(fixtureIds.slice(i, i + CHUNK_SIZE));
    }

    setLoadingOdds(true);
    setOddsProgress({ loaded: 0, total: fixtureIds.length });
    batchAbortRef.current = false;

    console.log(`📊 Carregando odds para ${fixtureIds.length} partidas em ${chunks.length} lotes...`);

    let totalLoaded = 0;

    for (const chunk of chunks) {
      if (batchAbortRef.current) {
        console.log('⚠️ Carregamento de odds cancelado');
        break;
      }

      try {
        const response = await matchesApi.batchOdds(chunk);

        if (response.success && response.odds) {
          // Atualiza matches com as odds recebidas
          setMatches(prev => prev.map(m => {
            const matchOdds = response.odds[m.id];
            if (matchOdds && Object.keys(matchOdds).length > 0) {
              return { ...m, odds: matchOdds as Odds };
            }
            return m;
          }));

          totalLoaded += chunk.length;
          setOddsProgress({ loaded: totalLoaded, total: fixtureIds.length });
        }
      } catch (error) {
        console.error('Erro ao carregar chunk de odds:', error);
        totalLoaded += chunk.length;
        setOddsProgress({ loaded: totalLoaded, total: fixtureIds.length });
      }
    }

    setLoadingOdds(false);
    setOddsProgress(null);
    console.log(`✅ Odds carregadas para ${totalLoaded} partidas`);
  }, []);

  /**
   * Atualiza as odds de uma partida específica no state.
   * Chamado pelo MatchCard ao carregar odds individual (GET).
   */
  const updateMatchOdds = useCallback((matchId: string, odds: Odds) => {
    setMatches(prev => prev.map(m =>
      m.id === matchId ? { ...m, odds } : m
    ));
  }, []);

  /**
   * Atualiza odds + status de uma partida no state.
   * Chamado pelo MatchCard ao dar refresh (POST).
   */
  const updateMatchOddsAndStatus = useCallback((
    matchId: string,
    odds: Odds,
    status?: string,
    statusShort?: string
  ) => {
    setMatches(prev => prev.map(m => {
      if (m.id !== matchId) return m;
      return {
        ...m,
        odds,
        ...(status ? { status } : {}),
        ...(statusShort ? { status_short: statusShort } : {}),
      };
    }));
  }, []);

  /**
   * Carrega dados para um período específico (3, 7 ou 14 dias).
   * 1. Preload fixtures no backend (cache incremental)
   * 2. Carrega matches (sem odds)
   * 3. Dispara batch de odds para todos os matches
   */
  const fetchByPeriod = useCallback(async (days: PeriodDays) => {
    // Cancela batch de odds anterior se existir
    batchAbortRef.current = true;

    setPreloading(true);
    setSelectedPeriod(days);
    setDataLoaded(false);
    setLoadingOdds(false);
    setOddsProgress(null);

    try {
      console.log(`📥 Solicitando preload de ${days} dias...`);
      const preloadResult = await preloadApi.fetch(days);

      if (!preloadResult.success) {
        console.error('❌ Erro no preload:', preloadResult.message);
        return;
      }

      console.log(`✅ Preload concluído: ${preloadResult.date_from} até ${preloadResult.date_to}`);

      // Carrega matches (sem odds)
      const loadedMatches = await loadMatches(preloadResult.date_from, preloadResult.date_to);

      // Carrega metadados
      await loadLeagues();
      await loadBookmakers();

      setDataLoaded(true);
      setPreloading(false);

      // Dispara carregamento de odds em lote (não bloqueia o preloading)
      loadAllOdds(loadedMatches);
    } catch (error) {
      console.error('Erro ao carregar período:', error);
      setMatches([]);
      setPreloading(false);
    }
  }, [loadMatches, loadLeagues, loadBookmakers, loadAllOdds]);

  return {
    matches,
    leagues,
    bookmakers,
    loading: loading || preloading,
    preloading,
    loadingOdds,
    oddsProgress,
    selectedPeriod,
    dataLoaded,
    loadMatches,
    fetchByPeriod,
    updateMatchOdds,
    updateMatchOddsAndStatus,
  };
}

