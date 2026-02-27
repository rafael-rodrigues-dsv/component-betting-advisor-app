/**
 * API Endpoints
 */
import { apiGet, apiPost, apiDelete } from './apiClient';
import type { Match, League, Bookmaker, Prediction, Ticket, TicketBet, Strategy } from '../../types';

// ============================================
// MATCHES
// ============================================
interface MatchesResponse {
  success: boolean;
  date: string;  // Data no formato YYYY-MM-DD
  count: number;
  matches: Match[];
}

interface LeaguesResponse {
  success: boolean;
  count: number;
  leagues: League[];
}

interface BookmakersResponse {
  success: boolean;
  count: number;
  bookmakers: Bookmaker[];
}

interface OddsResponse {
  success: boolean;
  fixture_id: string;
  odds: Record<string, any>;
  status?: string;
  status_short?: string;
  elapsed?: number | null;
  goals?: { home: number | null; away: number | null };
  message?: string;
  error?: string;
}

interface LiveMatchUpdate {
  id: string;
  status: string;
  status_short: string;
  elapsed: number | null;
  goals: {
    home: number | null;
    away: number | null;
  };
}

interface LiveUpdatesResponse {
  success: boolean;
  count: number;
  updates: LiveMatchUpdate[];
  error?: string;
}

export const matchesApi = {
  getMatches: (leagueId?: string, date?: string) => {
    const params: any = {};
    if (leagueId && leagueId !== 'all') {
      params.league_id = leagueId;
    }
    if (date) {
      params.date = date;
    }
    return apiGet<MatchesResponse>('/matches', Object.keys(params).length > 0 ? params : undefined);
  },

  getLeagues: () => apiGet<LeaguesResponse>('/leagues'),

  getBookmakers: () => apiGet<BookmakersResponse>('/bookmakers'),

  /** Busca odds de uma partida (cache ou API) */
  getMatchOdds: (fixtureId: string) =>
    apiGet<OddsResponse>(`/matches/${fixtureId}/odds`),

  /** Força refresh das odds de uma partida */
  refreshMatchOdds: (fixtureId: string) =>
    apiPost<OddsResponse>(`/matches/${fixtureId}/odds/refresh`, {}),

  /** Busca updates de jogos ao vivo (placar, status, minuto) */
  getLiveUpdates: () =>
    apiGet<LiveUpdatesResponse>('/matches/live'),
};

// ============================================
// PREDICTIONS
// ============================================
interface PreTicket {
  bets: any[];
  total_bets: number;
  combined_odds: number;
  message: string;
}

interface AnalyzeResponse {
  success: boolean;
  count: number;
  strategy: string;
  predictions: Prediction[];
  pre_ticket?: PreTicket;
}

export const predictionsApi = {
  analyze: (matchIds: string[], strategy: Strategy) =>
    apiPost<AnalyzeResponse>('/analyze', { match_ids: matchIds, strategy }),
};

// ============================================
// PRELOAD
// ============================================
interface PreloadFetchResponse {
  success: boolean;
  message: string;
  days?: number;
  date_from?: string;
  date_to?: string;
  total_fixtures?: number;
  leagues?: League[];
  dates?: string[];       // Lista de datas YYYY-MM-DD (para chamar /preload/odds)
  from_cache?: boolean;
}

interface PreloadOddsResponse {
  success: boolean;
  date: string;
  total_odds: number;
  from_cache?: boolean;
  error?: string;
}

interface PreloadLeagueOddsResponse {
  success: boolean;
  league_id: string;
  total_odds: number;
  dates_loaded: { date: string; count: number; from_cache: boolean }[];
  from_cache?: boolean;
  error?: string;
}

interface PreloadStatusResponse {
  hasCache: boolean;
  leagues: string[];
  timestamp: string;
  cacheValid: boolean;
}

export const preloadApi = {
  /** FASE 1: Carrega fixtures (rápido) */
  fetch: (days: number) =>
    apiPost<PreloadFetchResponse>(`/preload/fetch?days=${days}`, {}),

  /** FASE 2 (LEGACY): Carrega odds de UMA data (lento, paginado) */
  fetchOdds: (date: string) =>
    apiPost<PreloadOddsResponse>(`/preload/odds?date=${date}`, {}),

  /** FASE 2b: Carrega odds de uma LIGA para múltiplas datas (sob demanda, equilibrado) */
  fetchOddsByLeague: (leagueId: string, dates: string[]) =>
    apiPost<PreloadLeagueOddsResponse>('/preload/odds/league', { league_id: leagueId, dates }),

  getStatus: () =>
    apiGet<PreloadStatusResponse>('/preload/status'),
};

// ============================================
// TICKETS
// ============================================
interface TicketsResponse {
  success: boolean;
  count: number;
  tickets: Ticket[];
}

interface CreateTicketResponse {
  success: boolean;
  message: string;
  ticket: Ticket;
}

interface CreateTicketPayload {
  name: string;
  stake: number;
  bets: TicketBet[];
  bookmaker_id: string;
}

interface DashboardStatsResponse {
  success: boolean;
  stats: {
    total_tickets: number;
    won_tickets: number;
    lost_tickets: number;
    pending_tickets: number;
    success_rate: number;
    total_staked: number;
    total_profit: number;
  };
}

interface UpdateResultsResponse {
  success: boolean;
  message: string;
  stats: {
    total_pending: number;
    updated: number;
    won: number;
    lost: number;
  };
}

export const ticketsApi = {
  getTickets: () => apiGet<TicketsResponse>('/tickets'),

  getDashboardStats: () => apiGet<DashboardStatsResponse>('/tickets/stats/dashboard'),

  createTicket: (payload: CreateTicketPayload) =>
    apiPost<CreateTicketResponse>('/tickets', payload),

  simulateTicket: (ticketId: string) =>
    apiPost<{ success: boolean }>(`/tickets/${ticketId}/simulate`, {}),

  // Alias para compatibilidade
  simulateResult: (ticketId: string) =>
    apiPost<{ success: boolean }>(`/tickets/${ticketId}/simulate`, {}),

  deleteTicket: (ticketId: string) =>
    apiDelete<{ success: boolean }>(`/tickets/${ticketId}`),

  // Atualiza resultados de todos os bilhetes pendentes
  updateResults: () =>
    apiPost<UpdateResultsResponse>('/tickets/update-results', {}),
};


