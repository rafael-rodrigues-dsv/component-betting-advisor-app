/**
 * MatchesContext - Compartilha state de matches entre páginas (Dashboard, Matches, etc.)
 *
 * Encapsula o useMatches hook num Context para que todas as páginas
 * leiam os mesmos dados de matches, odds, leagues e bookmakers.
 *
 * Ao montar, carrega automaticamente os jogos de Hoje (1 dia)
 * para que o Dashboard já exiba dados sem interação do usuário.
 */
import React, { createContext, useContext, useEffect, useRef, ReactNode } from 'react';
import { useMatches, type PeriodDays } from '../hooks/useMatches';
import type { Match, League, Bookmaker, Odds } from '../types';

interface MatchesContextType {
  matches: Match[];
  leagues: League[];
  bookmakers: Bookmaker[];
  loading: boolean;
  preloading: boolean;
  loadingOdds: boolean;
  oddsProgress: { loaded: number; total: number } | null;
  livePolling: boolean;
  selectedPeriod: PeriodDays | null;
  dataLoaded: boolean;
  loadMatches: (dateFrom?: string, dateTo?: string) => Promise<Match[]>;
  fetchByPeriod: (days: PeriodDays) => Promise<void>;
  loadOddsForLeagues: (leagueIds: string[]) => Promise<void>;
  updateMatchOdds: (matchId: string, odds: Odds) => void;
  updateMatchOddsAndStatus: (matchId: string, odds: Odds, status?: string, statusShort?: string, elapsed?: number | null, goals?: { home: number | null; away: number | null }) => void;
  startLivePolling: () => void;
  stopLivePolling: () => void;
}

const MatchesContext = createContext<MatchesContextType | undefined>(undefined);

export const MatchesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const matchesHook = useMatches();
  const didAutoLoad = useRef(false);

  // Auto-carrega jogos de Hoje ao iniciar o app
  useEffect(() => {
    if (!didAutoLoad.current) {
      didAutoLoad.current = true;
      matchesHook.fetchByPeriod(1);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <MatchesContext.Provider value={matchesHook}>
      {children}
    </MatchesContext.Provider>
  );
};

export const useMatchesContext = (): MatchesContextType => {
  const context = useContext(MatchesContext);
  if (!context) {
    throw new Error('useMatchesContext must be used within MatchesProvider');
  }
  return context;
};
