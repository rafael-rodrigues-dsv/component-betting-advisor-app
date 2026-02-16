/**
 * TicketBuilder Component
 */
import React from 'react';
import type { TicketBet } from '../../types';
import { formatMarket, formatOutcome } from '../predictions/PredictionCard';

interface TicketBuilderProps {
  ticketBets: TicketBet[];
  stake: number;
  onStakeChange: (stake: number) => void;
  onRemoveBet: (index: number) => void;
  onClear: () => void;
  onCreate: () => void;
  bookmakerName?: string;
}

export const TicketBuilder: React.FC<TicketBuilderProps> = ({
  ticketBets,
  stake,
  onStakeChange,
  onRemoveBet,
  onClear,
  onCreate,
  bookmakerName,
}) => {
  if (ticketBets.length === 0) return null;

  const combinedOdds = ticketBets.reduce((acc, bet) => acc * bet.odds, 1);
  const potentialReturn = stake * combinedOdds;

  return (
    <div className="ticket-section">
      <div className="ticket-header">
        <span className="ticket-title">🎫 Novo Bilhete</span>
        {bookmakerName && (
          <div className="bookmaker-badge-ticket">
            🎰 {bookmakerName}
          </div>
        )}
      </div>
      <div className="ticket-bets">
        {ticketBets.map((bet, idx) => (
          <div key={idx} className="ticket-bet">
            <div className="ticket-bet-info">
              <div className="ticket-bet-match">{bet.home_team} vs {bet.away_team}</div>
              <div className="ticket-bet-prediction">{formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)}</div>
            </div>
            <div className="ticket-bet-odds">{bet.odds.toFixed(2)}</div>
            <button className="remove-bet-btn" onClick={() => onRemoveBet(idx)}>×</button>
          </div>
        ))}
      </div>
      <div className="ticket-summary">
        <div className="summary-row"><span>Apostas:</span><span>{ticketBets.length}</span></div>
        <div className="summary-row"><span>Odd Combinada:</span><span>{combinedOdds.toFixed(2)}</span></div>
        <div className="summary-row"><span>Retorno Potencial:</span><span>R$ {potentialReturn.toFixed(2)}</span></div>
      </div>
      <div className="stake-input">
        <label>Valor (R$):</label>
        <input type="number" value={stake} onChange={(e) => onStakeChange(Number(e.target.value))} min="1" />
      </div>
      <div className="ticket-actions">
        <button className="btn btn-secondary" onClick={onClear}>Limpar</button>
        <button className="btn btn-primary" onClick={onCreate}>Criar Bilhete</button>
      </div>
    </div>
  );
};

