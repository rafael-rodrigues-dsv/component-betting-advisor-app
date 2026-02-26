/**
 * useMatches Hook
 *
 * Não carrega automaticamente. O usuário deve selecionar um período (3, 7 ou 14 dias)
 * para disparar o preload e depois buscar os matches.
 *
 * Sempre busca TODOS os matches (sem filtro de liga).
 * A filtragem por liga/campeonato é feita client-side no MatchList.
 */
import { useState, useCallback } from 'react';
import { matchesApi, preloadApi } from '../services/api';
import type { Match, League, Bookmaker } from '../types';

export type PeriodDays = 3 | 7 | 14;

export function useMatches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [bookmakers, setBookmakers] = useState<Bookmaker[]>([]);
  const [loading, setLoading] = useState(false);
  const [preloading, setPreloading] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<PeriodDays | null>(null);
  const [dataLoaded, setDataLoaded] = useState(false);
  const [dateRange, setDateRange] = useState<{ from: string; to: string } | null>(null);

  const loadMatches = useCallback(async (dateFrom?: string, dateTo?: string) => {
    setLoading(true);
    try {
      console.log('🔄 Carregando jogos...', { dateFrom, dateTo });

      const params = new URLSearchParams();
      if (dateFrom) params.append('date_from', dateFrom);
      if (dateTo) params.append('date_to', dateTo);

      const url = `/api/v1/matches${params.toString() ? '?' + params.toString() : ''}`;
      const res = await fetch(url);
      const response = await res.json();

      console.log(`📊 Total: ${response.matches?.length || 0} jogos carregados`);
      setMatches(response.matches || []);
    } catch (error) {
      console.error('Erro ao carregar jogos:', error);
      setMatches([]);
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
   * Carrega dados para um período específico (3, 7 ou 14 dias).
   * 1. Chama POST /preload/fetch?days=N para popular o cache do backend
   * 2. Depois busca GET /matches?date_from=X&date_to=Y
   */
  const fetchByPeriod = useCallback(async (days: PeriodDays) => {
    setPreloading(true);
    setSelectedPeriod(days);
    setDataLoaded(false);

    try {
      console.log(`📥 Solicitando preload de ${days} dias...`);
      const preloadResult = await preloadApi.fetch(days);

      if (!preloadResult.success) {
        console.error('❌ Erro no preload:', preloadResult.message);
        return;
      }

      console.log(`✅ Preload concluído: ${preloadResult.date_from} até ${preloadResult.date_to}`);

      // Guarda range de datas para re-fetch
      setDateRange({ from: preloadResult.date_from!, to: preloadResult.date_to! });

      // Agora carrega os matches do período (sem filtro de liga - traz tudo)
      await loadMatches(preloadResult.date_from, preloadResult.date_to);

      // Carrega ligas e bookmakers (metadados)
      await loadLeagues();
      await loadBookmakers();

      setDataLoaded(true);
    } catch (error) {
      console.error('Erro ao carregar período:', error);
      setMatches([]);
    } finally {
      setPreloading(false);
    }
  }, [loadMatches, loadLeagues, loadBookmakers]);

  return {
    matches,
    leagues,
    bookmakers,
    loading: loading || preloading,
    preloading,
    selectedPeriod,
    dataLoaded,
    loadMatches,
    fetchByPeriod,
  };
}

