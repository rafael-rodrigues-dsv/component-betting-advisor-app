/**
 * MatchesContext - Compartilha state de matches entre páginas (Dashboard, Matches, etc.)
 *
 * Encapsula o useMatches hook num Context para que todas as páginas
 * leiam os mesmos dados de matches, odds, leagues e bookmakers.
 */
import React, { createContext, useContext, ReactNode } from 'react';
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
  selectedPeriod: PeriodDays | null;
  dataLoaded: boolean;
  loadMatches: (dateFrom?: string, dateTo?: string) => Promise<Match[]>;
  fetchByPeriod: (days: PeriodDays) => Promise<void>;
  updateMatchOdds: (matchId: string, odds: Odds) => void;
  updateMatchOddsAndStatus: (matchId: string, odds: Odds, status?: string, statusShort?: string) => void;
}

const MatchesContext = createContext<MatchesContextType | undefined>(undefined);

export const MatchesProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const matchesHook = useMatches();

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

