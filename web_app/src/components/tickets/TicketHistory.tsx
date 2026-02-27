/**
 * TicketHistory Component
 *
 * Layout rico para acompanhamento:
 * - Placar ao vivo com minuto do jogo
 * - Barra de progresso do jogo (0-90min)
 * - Indicador visual se a aposta está ganhando/perdendo
 * - Status detalhado por partida
 */
import React from 'react';
import type { Ticket, TicketBet } from '../../types';
import { formatMarket, formatOutcome } from '../predictions/PredictionCard';

const LIVE_STATUSES = ['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE'];
const FINISHED_STATUSES = ['FT', 'AET', 'PEN'];

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
    'AET': { label: 'Enc. (Pror.)', className: 'match-status-ft' },
    'PEN': { label: 'Enc. (Pên.)', className: 'match-status-ft' },
  };
  return map[statusShort] || { label: statusShort, className: 'match-status-ns' };
};

/** Verifica se a aposta está ganhando no momento com base no placar parcial */
const isBetCurrentlyWinning = (bet: TicketBet): boolean | null => {
  const gh = bet.goals_home;
  const ga = bet.goals_away;
  if (gh == null || ga == null) return null;

  const { market, predicted_outcome } = bet;

  if (market === 'MATCH_WINNER') {
    if (predicted_outcome === 'HOME') return gh > ga;
    if (predicted_outcome === 'DRAW') return gh === ga;
    if (predicted_outcome === 'AWAY') return ga > gh;
  }
  if (market === 'OVER_UNDER' || market === 'BTTS' || market === 'BOTH_TEAMS_SCORE') {
    const total = gh + ga;
    if (predicted_outcome === 'OVER') return total > 2;
    if (predicted_outcome === 'UNDER') return total < 2;
    if (predicted_outcome === 'YES') return gh > 0 && ga > 0;
    if (predicted_outcome === 'NO') return gh === 0 || ga === 0;
  }
  return null;
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
        const hasLive = bets.some(b => LIVE_STATUSES.includes(b.status_short || ''));

        return (
          <div key={ticket.id} className={`history-ticket ${hasLive ? 'history-ticket-live' : ''}`}>
            {/* Header */}
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

            {/* Details */}
            <div className="history-details">
              <span>💰 Stake: R$ {stake.toFixed(2)}</span>
              <span>📊 Odd: {combinedOdds.toFixed(2)}</span>
              <span>🎯 Retorno: R$ {potentialReturn.toFixed(2)}</span>
              {ticket.profit !== undefined && ticket.profit !== null && (
                <span style={{ color: ticket.profit >= 0 ? '#00ba7c' : '#f4212e', fontWeight: 700 }}>
                  {ticket.profit >= 0 ? '✅' : '❌'} Lucro: R$ {ticket.profit.toFixed(2)}
                </span>
              )}
            </div>

            {/* Bets */}
            <div className="history-bets">
              {bets.map((bet, idx) => {
                const isWon = bet.result === 'WON' || bet.result === 'GANHOU';
                const isLost = bet.result === 'LOST' || bet.result === 'PERDEU';
                const isLive = LIVE_STATUSES.includes(bet.status_short || '');
                const isFinished = FINISHED_STATUSES.includes(bet.status_short || '');
                const matchStatus = getMatchStatusInfo(bet.status_short);
                const winning = isLive ? isBetCurrentlyWinning(bet) : null;
                const hasScore = bet.goals_home != null && bet.goals_away != null;

                // Classe do card
                let betClass = 'bet-pending';
                if (isWon) betClass = 'bet-won';
                else if (isLost) betClass = 'bet-lost';
                else if (isLive && winning === true) betClass = 'bet-winning';
                else if (isLive && winning === false) betClass = 'bet-losing';

                // Ícone
                let icon = '⏳';
                if (isWon) icon = '✅';
                else if (isLost) icon = '❌';
                else if (isLive && winning === true) icon = '🟢';
                else if (isLive && winning === false) icon = '🔴';
                else if (isLive) icon = '⚽';

                // Progresso do jogo (0-90min, ~120 com prorrogação)
                const elapsed = bet.elapsed || 0;
                const maxMin = (bet.status_short === 'ET' || bet.status_short === 'BT') ? 120 : 90;
                const progressPct = isLive ? Math.min((elapsed / maxMin) * 100, 100) : (isFinished ? 100 : 0);

                return (
                  <div key={idx} className={`history-bet-item ${betClass}`}>
                    {/* Coluna esquerda: ícone */}
                    <span className="bet-result-icon">{icon}</span>

                    {/* Coluna central: info do jogo */}
                    <div className="hbi-content">
                      {/* Linha 1: Times + Placar ao vivo */}
                      <div className="hbi-row-main">
                        <span className="hbi-teams">{bet.home_team} vs {bet.away_team}</span>
                        <div className="hbi-right">
                          {/* Placar */}
                          {hasScore && (
                            <span className={`hbi-score ${isLive ? 'hbi-score-live' : ''}`}>
                              {bet.goals_home} × {bet.goals_away}
                            </span>
                          )}
                          {/* Minuto ao vivo */}
                          {isLive && elapsed > 0 && (
                            <span className="hbi-elapsed">{elapsed}&apos;</span>
                          )}
                          {/* Status badge */}
                          {matchStatus.label && (
                            <span className={`ticket-match-status-badge ${matchStatus.className}`}>
                              {matchStatus.label}
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Barra de progresso (apenas ao vivo) */}
                      {(isLive || isFinished) && (
                        <div className="hbi-progress-track">
                          <div
                            className={`hbi-progress-fill ${isLive ? 'hbi-progress-live' : 'hbi-progress-done'}`}
                            style={{ width: `${progressPct}%` }}
                          />
                        </div>
                      )}

                      {/* Linha 2: Liga + Mercado + Odd */}
                      <div className="hbi-row-detail">
                        <span className="hbi-league">{bet.league}</span>
                        <span className="hbi-market">
                          {formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)}
                        </span>
                        <span className="hbi-odds">@ {(bet.odds ?? 0).toFixed(2)}</span>
                      </div>

                      {/* Indicador de winning/losing ao vivo */}
                      {isLive && winning !== null && (
                        <div className={`hbi-live-indicator ${winning ? 'hbi-winning' : 'hbi-losing'}`}>
                          {winning ? '✓ Ganhando' : '✗ Perdendo'}
                        </div>
                      )}

                      {/* Placar final (jogos encerrados sem resultado processado ainda) */}
                      {bet.final_score && isFinished && !isLive && (
                        <span className="bet-final-score">
                          Placar Final: <strong>{bet.final_score}</strong>
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Actions */}
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
