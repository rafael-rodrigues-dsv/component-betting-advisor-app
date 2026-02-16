/**
 * API Endpoints
 */
import { apiGet, apiPost, apiDelete } from './apiClient';
import type { Match, League, Bookmaker, Prediction, Ticket, TicketBet, Strategy } from '../types';

// ============================================
// MATCHES
// ============================================
interface MatchesResponse {
  success: boolean;
  matches: Match[];
}

interface LeaguesResponse {
  success: boolean;
  leagues: League[];
}

interface BookmakersResponse {
  success: boolean;
  bookmakers: Bookmaker[];
}

export const matchesApi = {
  getMatches: (leagueId?: string) =>
    apiGet<MatchesResponse>('/matches', leagueId && leagueId !== 'all' ? { league_id: leagueId } : undefined),

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
  predictions: Prediction[];
  pre_ticket?: PreTicket;
}

export const predictionsApi = {
  analyze: (matchIds: string[], strategy: Strategy) =>
    apiPost<AnalyzeResponse>('/analyze', { match_ids: matchIds, strategy }),
};

// ============================================
// TICKETS
// ============================================
interface TicketsResponse {
  success: boolean;
  tickets: Ticket[];
}

interface CreateTicketResponse {
  success: boolean;
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
};


