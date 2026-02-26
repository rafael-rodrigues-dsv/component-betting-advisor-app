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

export const matchesApi = {
  getMatches: (leagueId?: string, date?: string) => {
    const params: any = {};
    if (leagueId && leagueId !== 'all') {
      params.league_id = leagueId;
    }
    if (date) {
      params.date = date;
    }
    // Se não passar date, backend retorna semana toda automaticamente
    return apiGet<MatchesResponse>('/matches', Object.keys(params).length > 0 ? params : undefined);
  },

  getLeagues: () => apiGet<LeaguesResponse>('/leagues'),

  getBookmakers: () => apiGet<BookmakersResponse>('/bookmakers'),
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
}

interface PreloadStatusResponse {
  hasCache: boolean;
  leagues: string[];
  timestamp: string;
  cacheValid: boolean;
}

export const preloadApi = {
  fetch: (days: number) =>
    apiPost<PreloadFetchResponse>(`/preload/fetch?days=${days}`, {}),

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


