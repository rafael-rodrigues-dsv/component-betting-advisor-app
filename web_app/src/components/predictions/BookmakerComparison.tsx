/**
 * BookmakerComparison Component
 *
 * Mostra 2 pré-bilhetes lado a lado (um por casa de apostas)
 * com recomendação de qual casa paga melhor.
 */
import React from 'react';
import type { Prediction } from '../../types';
import { formatMarket, formatOutcome } from './PredictionCard';

const BOOKMAKER_META: Record<string, { name: string; logo: string }> = {
  'bet365': { name: 'Bet365', logo: '🟢' },
  'betano': { name: 'Betano', logo: '🟡' },
};

interface PreTicketBet {
  match_id: string;
  home_team: string;
  away_team: string;
  league: string;
  market: string;
  predicted_outcome: string;
  odds: number;
  confidence: number;
}

interface BookmakerTicket {
  bookmaker_id: string;
  bets: PreTicketBet[];
  combined_odds: number;
  potential_return: number;
}

interface BookmakerComparisonProps {
  predictions: Prediction[];
  preTicketBets: PreTicketBet[];
  stake: number;
  onSelectBookmaker: (bookmakerId: string, bets: PreTicketBet[]) => void;
}

/**
 * Dado o pré-bilhete (lista de bets com mercado escolhido por jogo),
 * monta uma versão do bilhete para cada bookmaker usando as odds reais.
 */
function buildBookmakerTickets(
  predictions: Prediction[],
  preTicketBets: PreTicketBet[],
  stake: number
): BookmakerTicket[] {
  // Coleta todos os bookmakers disponíveis
  const bookmakerIds = new Set<string>();
  predictions.forEach(p => {
    if (p.odds_by_bookmaker) {
      Object.keys(p.odds_by_bookmaker).forEach(bk => bookmakerIds.add(bk));
    }
  });

  // Para cada bookmaker, monta as mesmas apostas com odds específicas
  const tickets: BookmakerTicket[] = [];

  for (const bkId of Array.from(bookmakerIds)) {
    const bets: PreTicketBet[] = [];
    let combinedOdds = 1;

    for (const bet of preTicketBets) {
      const prediction = predictions.find(p => p.match_id === bet.match_id);
      const bkOdds = prediction?.odds_by_bookmaker?.[bkId];

      // Mapeia mercado+outcome para a odd da bookmaker
      let odd = bet.odds; // fallback
      if (bkOdds) {
        if (bet.market === 'MATCH_WINNER') {
          if (bet.predicted_outcome === 'HOME') odd = bkOdds.home || bet.odds;
          else if (bet.predicted_outcome === 'DRAW') odd = bkOdds.draw || bet.odds;
          else if (bet.predicted_outcome === 'AWAY') odd = bkOdds.away || bet.odds;
        } else if (bet.market === 'OVER_UNDER') {
          if (bet.predicted_outcome.startsWith('OVER')) odd = bkOdds.over_25 || bet.odds;
          else odd = bkOdds.under_25 || bet.odds;
        } else if (bet.market === 'BTTS') {
          if (bet.predicted_outcome === 'YES') odd = bkOdds.btts_yes || bet.odds;
          else odd = bkOdds.btts_no || bet.odds;
        }
      }

      bets.push({ ...bet, odds: odd });
      combinedOdds *= odd;
    }

    tickets.push({
      bookmaker_id: bkId,
      bets,
      combined_odds: combinedOdds,
      potential_return: stake * combinedOdds,
    });
  }

  // Ordena: melhor odd combinada primeiro
  tickets.sort((a, b) => b.combined_odds - a.combined_odds);

  return tickets;
}

export const BookmakerComparison: React.FC<BookmakerComparisonProps> = ({
  predictions,
  preTicketBets,
  stake,
  onSelectBookmaker,
}) => {
  if (preTicketBets.length === 0) return null;

  const tickets = buildBookmakerTickets(predictions, preTicketBets, stake);

  if (tickets.length === 0) return null;

  const bestTicket = tickets[0];
  const worstTicket = tickets.length > 1 ? tickets[tickets.length - 1] : null;

  // Calcula diferença percentual
  let diffPercent = 0;
  let diffMoney = 0;
  if (worstTicket && bestTicket.combined_odds !== worstTicket.combined_odds) {
    diffPercent = ((bestTicket.combined_odds - worstTicket.combined_odds) / worstTicket.combined_odds) * 100;
    diffMoney = bestTicket.potential_return - worstTicket.potential_return;
  }

  return (
    <div className="bookmaker-comparison-section">
      <div className="comparison-header">
        <h3>🎫 Comparação de Bilhetes — Qual casa paga melhor?</h3>
      </div>

      <div className="comparison-grid">
        {tickets.map((ticket) => {
          const meta = BOOKMAKER_META[ticket.bookmaker_id] || { name: ticket.bookmaker_id, logo: '🎰' };
          const isBest = ticket.bookmaker_id === bestTicket.bookmaker_id && tickets.length > 1;

          return (
            <div key={ticket.bookmaker_id} className={`comparison-card ${isBest ? 'comparison-card-best' : ''}`}>
              <div className="comparison-card-header">
                <span className="comparison-bk-logo">{meta.logo}</span>
                <span className="comparison-bk-name">{meta.name}</span>
                {isBest && <span className="comparison-best-badge">⭐ Melhor</span>}
              </div>

              <div className="comparison-bets">
                {ticket.bets.map((bet, idx) => (
                  <div key={idx} className="comparison-bet-row">
                    <div className="comparison-bet-match">{bet.home_team} vs {bet.away_team}</div>
                    <div className="comparison-bet-detail">
                      <span className="comparison-bet-market">{formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)}</span>
                      <span className={`comparison-bet-odd ${isBest ? 'odd-highlight' : ''}`}>@ {bet.odds.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="comparison-summary">
                <div className="comparison-summary-row">
                  <span>Odd Combinada:</span>
                  <span className="comparison-summary-value">{ticket.combined_odds.toFixed(2)}</span>
                </div>
                <div className="comparison-summary-row">
                  <span>Retorno (R$ {stake.toFixed(0)}):</span>
                  <span className="comparison-summary-value">R$ {ticket.potential_return.toFixed(2)}</span>
                </div>
              </div>

              <button
                className="btn btn-primary comparison-select-btn"
                onClick={() => onSelectBookmaker(ticket.bookmaker_id, ticket.bets)}
              >
                ✅ Usar {meta.name}
              </button>
            </div>
          );
        })}
      </div>

      {diffPercent > 0 && worstTicket && (
        <div className="comparison-recommendation">
          💡 <strong>Recomendação:</strong>{' '}
          {BOOKMAKER_META[bestTicket.bookmaker_id]?.name || bestTicket.bookmaker_id} paga{' '}
          <strong>+{diffPercent.toFixed(1)}%</strong> melhor neste bilhete
          (R$ {diffMoney.toFixed(2)} a mais com aposta de R$ {stake.toFixed(0)})
        </div>
      )}
    </div>
  );
};

