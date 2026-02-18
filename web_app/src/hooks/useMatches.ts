/**
 * useMatches Hook
 */
import { useState, useEffect, useCallback } from 'react';
import { matchesApi } from '../services/api';
import type { Match, League, Bookmaker } from '../types';

export function useMatches(selectedLeague: string) {
  const [matches, setMatches] = useState<Match[]>([]);
  const [leagues, setLeagues] = useState<League[]>([]);
  const [bookmakers, setBookmakers] = useState<Bookmaker[]>([]);
  const [loading, setLoading] = useState(false);

  const loadMatches = useCallback(async () => {
    setLoading(true);
    try {
      // Backend agora retorna semana toda por padrão (hoje até domingo)
      console.log('🔄 Carregando jogos da semana...');
      const data = await matchesApi.getMatches(selectedLeague);

      console.log(`📊 Total: ${data.matches?.length || 0} jogos carregados`);
      setMatches(data.matches || []);
    } catch (error) {
      console.error('Erro ao carregar jogos:', error);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  }, [selectedLeague]);

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

  useEffect(() => {
    loadMatches();
  }, [loadMatches]);

  useEffect(() => {
    loadLeagues();
    loadBookmakers();
  }, [loadLeagues, loadBookmakers]);

  return { matches, leagues, bookmakers, loading, loadMatches };
}

