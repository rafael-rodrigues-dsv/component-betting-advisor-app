/**
 * Types - Definições de tipos TypeScript
 */

// ============================================
// LOGO
// ============================================
export type LogoType = 'LOCAL' | 'EXT';

export interface Logo {
  url: string;
  type: LogoType;
}

// ============================================
// TEAM & LEAGUE
// ============================================
export interface Team {
  id: string;
  name: string;
  logo: Logo;
  country?: string;
}

export interface League {
  id: string;
  name: string;
  country: string;
  logo: string;
  type: 'league' | 'cup';
}

export interface Bookmaker {
  id: string;
  name: string;
  logo: string;
  is_default?: boolean;
}

// ============================================
// MATCH
// ============================================
export interface RoundInfo {
  type: 'round' | 'phase';
  number?: number;
  name: string;
}

export interface Venue {
  name: string;
  city: string;
}

export interface BookmakerOdds {
  home: number;
  draw: number;
  away: number;
  over_25?: number;
  under_25?: number;
  btts_yes?: number;
  btts_no?: number;
}

export interface Odds {
  [bookmaker: string]: BookmakerOdds;
}

export interface Match {
  id: string;
  league: League;
  home_team: Team;
  away_team: Team;
  date: string;
  timestamp: string;  // Data no formato YYYY-MM-DD
  status: string;
  status_short: string;  // "NS", "1H", "2H", "HT", "FT", etc.
  round: RoundInfo;
  venue: Venue;
  odds: Odds;  // Pode estar vazio {} — odds são carregadas sob demanda
}

// ============================================
// PREDICTION
// ============================================
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
  date: string;
  predictions: MarketPrediction[];
  strategy_used: string;
  bookmaker_id?: string;
  bookmaker_name?: string;
  odds_by_bookmaker?: Record<string, Record<string, number>>;
}

// ============================================
// TICKET
// ============================================
export interface TicketBet {
  match_id: string;
  home_team: string;
  away_team: string;
  league: string;
  date?: string;
  market: string;
  predicted_outcome: string;
  odds: number;
  confidence: number;
  bookmaker_id?: string;
  result?: string | null;
  final_score?: string | null;
  status?: string | null;
  status_short?: string | null;
}

export interface Ticket {
  id: string;
  name: string;
  stake: number;
  combined_odds: number;
  potential_return: number;
  bookmaker_id: string;
  status: string;
  profit?: number;
  bets: TicketBet[];
  created_at: string;
}

export interface DashboardStats {
  total_tickets: number;
  won_tickets: number;
  lost_tickets: number;
  pending_tickets: number;
  success_rate: number;
  total_staked: number;
  total_profit: number;
}

// ============================================
// APP STATE
// ============================================
export type Tab = 'dashboard' | 'matches' | 'predictions' | 'tickets';
export type Strategy = 'BALANCED' | 'CONSERVATIVE' | 'VALUE_BET' | 'AGGRESSIVE';

