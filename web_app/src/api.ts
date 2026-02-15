import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
});

// Types
export interface Team {
  id: string;
  name: string;
  logo: string;
}

export interface League {
  id: string;
  name: string;
  country: string;
  logo: string;
  type: 'league' | 'cup';
}

export interface RoundInfo {
  type: 'round' | 'phase';
  number?: number;
  name: string;
}

export interface Venue {
  name: string;
  city: string;
}

export interface Bookmaker {
  id: string;
  name: string;
  logo: string;
}

export interface Odds {
  home: number;
  draw: number;
  away: number;
  over_25?: number;
  under_25?: number;
  btts_yes?: number;
  btts_no?: number;
}

export interface Match {
  id: string;
  league: League;
  home_team: Team;
  away_team: Team;
  date: string;
  status: string;
  round: RoundInfo;
  venue: Venue;
  odds: Odds;
}

export interface MarketPrediction {
  market: string;
  predicted_outcome: string;
  confidence: number;
  odds: number;
  expected_value: number;
  recommendation: string;
}

export interface Prediction {
  id: string;
  match_id: string;
  home_team: string;
  away_team: string;
  league: string;
  match_date: string;
  predictions: MarketPrediction[];
  best_bet: MarketPrediction | null;
  created_at: string;
}

export interface TicketBet {
  match_id: string;
  home_team: string;
  away_team: string;
  market: string;
  predicted_outcome: string;
  odds: number;
  confidence: number;
}

export interface Ticket {
  id: string;
  name: string;
  stake: number;
  combined_odds: number;
  potential_return: number;
  status: string;
  result: string | null;
  profit?: number;
  bets: TicketBet[];
  created_at: string;
}

// API Calls
export const matchApi = {
  getMatches: async (date?: string, leagueId?: string) => {
    const params: Record<string, string> = {};
    if (date) params.date = date;
    if (leagueId && leagueId !== 'all') params.league_id = leagueId;
    const response = await api.get('/matches', { params });
    return response.data;
  },

  getMatch: async (id: string) => {
    const response = await api.get(`/matches/${id}`);
    return response.data;
  },

  getLeagues: async () => {
    const response = await api.get('/leagues');
    return response.data;
  },

  getBookmakers: async () => {
    const response = await api.get('/bookmakers');
    return response.data;
  },
};

export const predictionApi = {
  analyze: async (matchIds: string[], strategy: string = 'BALANCED') => {
    const response = await api.post('/analyze', { match_ids: matchIds, strategy });
    return response.data;
  },

  getPredictions: async (limit: number = 10) => {
    const response = await api.get('/predictions', { params: { limit } });
    return response.data;
  },

  getPrediction: async (id: string) => {
    const response = await api.get(`/predictions/${id}`);
    return response.data;
  },
};

export const ticketApi = {
  createTicket: async (name: string | null, stake: number, bets: TicketBet[]) => {
    const response = await api.post('/tickets', { name, stake, bets });
    return response.data;
  },

  getTickets: async (status?: string, limit: number = 20) => {
    const params: Record<string, unknown> = { limit };
    if (status) params.status = status;
    const response = await api.get('/tickets', { params });
    return response.data;
  },

  getTicket: async (id: string) => {
    const response = await api.get(`/tickets/${id}`);
    return response.data;
  },

  updateTicket: async (id: string, data: { name?: string; stake?: number }) => {
    const response = await api.put(`/tickets/${id}`, data);
    return response.data;
  },

  deleteTicket: async (id: string) => {
    const response = await api.delete(`/tickets/${id}`);
    return response.data;
  },

  simulateResult: async (id: string) => {
    const response = await api.post(`/tickets/${id}/simulate`);
    return response.data;
  },
};

export default api;

