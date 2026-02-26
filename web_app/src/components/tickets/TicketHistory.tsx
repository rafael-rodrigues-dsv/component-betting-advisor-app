/**
 * TicketHistory Component
 */
import React from 'react';
import type { Ticket } from '../../types';
import { formatMarket, formatOutcome } from '../predictions/PredictionCard';

const getMatchStatusInfo = (statusShort?: string | null): { label: string; className: string } => {
  if (!statusShort) return { label: '', className: '' };
  const map: Record<string, { label: string; className: string }> = {
    'TBD': { label: 'A definir', className: 'match-status-tbd' },
    'NS':  { label: 'Não iniciado', className: 'match-status-ns' },
    '1H':  { label: '1º Tempo', className: 'match-status-live' },
    'HT':  { label: 'Intervalo', className: 'match-status-live' },
    '2H':  { label: '2º Tempo', className: 'match-status-live' },
    'ET':  { label: 'Prorrogação', className: 'match-status-live' },
    'BT':  { label: 'Intervalo Pror.', className: 'match-status-live' },
    'P':   { label: 'Pênaltis', className: 'match-status-live' },
    'SUSP':{ label: 'Suspenso', className: 'match-status-susp' },
    'INT': { label: 'Interrompido', className: 'match-status-susp' },
    'LIVE':{ label: 'Ao Vivo', className: 'match-status-live' },
    'FT':  { label: 'Encerrado', className: 'match-status-ft' },
    'AET': { label: 'Encerrado (Pror.)', className: 'match-status-ft' },
    'PEN': { label: 'Encerrado (Pên.)', className: 'match-status-ft' },
  };
  return map[statusShort] || { label: statusShort, className: 'match-status-ns' };
};

interface TicketHistoryProps {
  tickets: Ticket[];
  onDelete: (ticketId: string) => void;
}

export const TicketHistory: React.FC<TicketHistoryProps> = ({ tickets, onDelete }) => {
  if (!tickets || tickets.length === 0) {
    return (
      <div className="empty-state">
        <h3>Nenhum bilhete criado</h3>
        <p>Adicione previsões ao bilhete</p>
      </div>
    );
  }

  return (
    <div className="tickets-history">
      {tickets.map((ticket) => {
        if (!ticket) return null;

        const stake = ticket.stake ?? 0;
        const combinedOdds = ticket.combined_odds ?? 0;
        const potentialReturn = ticket.potential_return ?? 0;
        const bets = ticket.bets ?? [];

        return (
          <div key={ticket.id} className="history-ticket">
            <div className="history-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className="history-name">{ticket.name || 'Bilhete'}</span>
                {ticket.bookmaker_id && (
                  <span className="bookmaker-badge-history">
                    🎰 {ticket.bookmaker_id === 'bet365' ? 'Bet365' : ticket.bookmaker_id === 'betano' ? 'Betano' : ticket.bookmaker_id}
                  </span>
                )}
              </div>
              <span className={`history-status status-${ticket.status}`}>{ticket.status}</span>
            </div>
            <div className="history-details">
              <span>Stake: R$ {stake.toFixed(2)}</span>
              <span>Odd: {combinedOdds.toFixed(2)}</span>
              <span>Retorno: R$ {potentialReturn.toFixed(2)}</span>
              {ticket.profit !== undefined && ticket.profit !== null && (
                <span style={{ color: ticket.profit >= 0 ? '#00ba7c' : '#f4212e' }}>
                  Lucro: R$ {ticket.profit.toFixed(2)}
                </span>
              )}
            </div>
            <div className="history-bets">
              {bets.map((bet, idx) => {
                const isWon = bet.result === 'WON' || bet.result === 'GANHOU';
                const isLost = bet.result === 'LOST' || bet.result === 'PERDEU';
                const resultIcon = isWon ? '✅' : isLost ? '❌' : '⏳';
                const resultClass = isWon ? 'bet-won' : isLost ? 'bet-lost' : 'bet-pending';
                const resultText = isWon ? 'GANHOU' : isLost ? 'PERDEU' : 'PENDENTE';

                const matchStatus = getMatchStatusInfo(bet.status_short);

                return (
                  <div key={idx} className={`history-bet-item ${resultClass}`}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                      <span className="bet-result-icon" style={{ fontSize: 20 }}>{resultIcon}</span>
                      <div className="bet-info-container" style={{ flex: 1 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                          <span className="bet-info">
                            {bet.home_team} vs {bet.away_team}
                          </span>
                          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                            {matchStatus.label && (
                              <span className={`ticket-match-status-badge ${matchStatus.className}`}>
                                {matchStatus.label}
                              </span>
                            )}
                            <span style={{
                              fontSize: 11,
                              fontWeight: 700,
                              padding: '2px 8px',
                              borderRadius: 6,
                              backgroundColor: isWon ? 'rgba(16, 185, 129, 0.2)' : isLost ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                              color: isWon ? '#10b981' : isLost ? '#ef4444' : '#f59e0b',
                              border: `1px solid ${isWon ? '#10b981' : isLost ? '#ef4444' : '#f59e0b'}`
                            }}>
                              {resultText}
                            </span>
                          </div>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span className="bet-market-info" style={{ fontSize: 12, color: '#9ca3af' }}>
                            {formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)} @ {(bet.odds ?? 0).toFixed(2)}
                          </span>
                          {bet.final_score && (
                            <span className="bet-final-score">
                              Placar: <strong>{bet.final_score}</strong>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            {ticket.status === 'PENDENTE' && (
              <div className="ticket-actions" style={{ marginTop: 12 }}>
                <span className="processing-label">⏳ Aguardando resultados...</span>
                <button className="btn btn-danger" onClick={() => onDelete(ticket.id)}>🗑️ Excluir</button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};
