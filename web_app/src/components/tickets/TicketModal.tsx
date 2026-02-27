/**
 * TicketModal Component
 *
 * Modal que exibe o bilhete montado com:
 * - Lista de apostas com odds (editável — troca de mercado)
 * - Resumo (odd combinada, retorno potencial)
 * - Input de stake
 * - Botões Cancelar / Criar Bilhete
 */
import React, { useEffect, useState } from 'react';
import type { TicketBet, Prediction } from '../../types';
import { formatMarket, formatOutcome } from '../predictions/PredictionCard';

interface TicketModalProps {
  isOpen: boolean;
  ticketBets: TicketBet[];
  stake: number;
  onStakeChange: (stake: number) => void;
  onRemoveBet: (index: number) => void;
  onReplaceBet: (index: number, newBet: TicketBet) => void;
  onClose: () => void;
  onCreate: () => void;
  bookmakerName?: string;
  bookmakerId?: string;
  creating?: boolean;
  predictions?: Prediction[];
}

export const TicketModal: React.FC<TicketModalProps> = ({
  isOpen,
  ticketBets,
  stake,
  onStakeChange,
  onRemoveBet,
  onReplaceBet,
  onClose,
  onCreate,
  bookmakerName,
  bookmakerId,
  creating,
  predictions = [],
}) => {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);

  // Fecha com ESC
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (editingIndex !== null) {
          setEditingIndex(null);
        } else {
          onClose();
        }
      }
    };
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isOpen, onClose, editingIndex]);

  // Reset editing ao fechar
  useEffect(() => {
    if (!isOpen) setEditingIndex(null);
  }, [isOpen]);

  if (!isOpen || ticketBets.length === 0) return null;

  const combinedOdds = ticketBets.reduce((acc, bet) => acc * bet.odds, 1);
  const potentialReturn = stake * combinedOdds;

  // Busca TODAS as opções possíveis de cada mercado para um bet
  const getAlternatives = (bet: TicketBet): { market: string; predicted_outcome: string; odds: number; confidence: number; expected_value: number; recommendation: string }[] => {
    const pred = predictions.find(p => p.match_id === bet.match_id);
    if (!pred) return [];

    // Pega odds da bookmaker selecionada (ou da primeira disponível)
    const bkId = bookmakerId || Object.keys(pred.odds_by_bookmaker || {})[0];
    const bkOdds = bkId ? pred.odds_by_bookmaker?.[bkId] : null;

    // Mapa de previsões originais por mercado (para confiança/EV/recomendação)
    const predMap = new Map(pred.predictions.map(m => [`${m.market}:${m.predicted_outcome}`, m]));

    const alternatives: { market: string; predicted_outcome: string; odds: number; confidence: number; expected_value: number; recommendation: string }[] = [];

    // ── MATCH_WINNER: HOME, DRAW, AWAY ──
    const mwOptions: { outcome: string; oddsKey: string }[] = [
      { outcome: 'HOME', oddsKey: 'home' },
      { outcome: 'DRAW', oddsKey: 'draw' },
      { outcome: 'AWAY', oddsKey: 'away' },
    ];
    for (const opt of mwOptions) {
      const odd = bkOdds?.[opt.oddsKey as keyof typeof bkOdds] as number | undefined;
      if (!odd || odd <= 0) continue;
      const orig = predMap.get(`MATCH_WINNER:${opt.outcome}`);
      alternatives.push({
        market: 'MATCH_WINNER',
        predicted_outcome: opt.outcome,
        odds: odd,
        confidence: orig?.confidence ?? 0,
        expected_value: orig?.expected_value ?? 0,
        recommendation: orig?.recommendation ?? 'CONSIDER',
      });
    }

    // ── OVER_UNDER: OVER, UNDER ──
    const ouOptions: { outcome: string; oddsKey: string }[] = [
      { outcome: 'OVER', oddsKey: 'over_25' },
      { outcome: 'UNDER', oddsKey: 'under_25' },
    ];
    for (const opt of ouOptions) {
      const odd = bkOdds?.[opt.oddsKey as keyof typeof bkOdds] as number | undefined;
      if (!odd || odd <= 0) continue;
      const orig = predMap.get(`OVER_UNDER:${opt.outcome}`);
      alternatives.push({
        market: 'OVER_UNDER',
        predicted_outcome: opt.outcome,
        odds: odd,
        confidence: orig?.confidence ?? 0,
        expected_value: orig?.expected_value ?? 0,
        recommendation: orig?.recommendation ?? 'CONSIDER',
      });
    }

    // ── BTTS: YES, NO ──
    const bttsOptions: { outcome: string; oddsKey: string }[] = [
      { outcome: 'YES', oddsKey: 'btts_yes' },
      { outcome: 'NO', oddsKey: 'btts_no' },
    ];
    for (const opt of bttsOptions) {
      const odd = bkOdds?.[opt.oddsKey as keyof typeof bkOdds] as number | undefined;
      if (!odd || odd <= 0) continue;
      const orig = predMap.get(`BTTS:${opt.outcome}`);
      alternatives.push({
        market: 'BTTS',
        predicted_outcome: opt.outcome,
        odds: odd,
        confidence: orig?.confidence ?? 0,
        expected_value: orig?.expected_value ?? 0,
        recommendation: orig?.recommendation ?? 'CONSIDER',
      });
    }

    return alternatives;
  };

  const handleSelectAlternative = (betIndex: number, alt: { market: string; predicted_outcome: string; odds: number; confidence: number }) => {
    const currentBet = ticketBets[betIndex];
    const newBet: TicketBet = {
      ...currentBet,
      market: alt.market,
      predicted_outcome: alt.predicted_outcome,
      odds: alt.odds,
      confidence: alt.confidence,
    };
    onReplaceBet(betIndex, newBet);
    setEditingIndex(null);
  };

  return (
    <div className="ticket-modal-overlay" onClick={onClose}>
      <div className="ticket-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="ticket-modal-header">
          <div className="ticket-modal-title-row">
            <span className="ticket-modal-title">🎫 Novo Bilhete</span>
            {bookmakerName && (
              <span className="ticket-modal-bookmaker">🎰 {bookmakerName}</span>
            )}
          </div>
          <button className="ticket-modal-close" onClick={onClose} title="Fechar">×</button>
        </div>

        {/* Bets list */}
        <div className="ticket-modal-bets">
          {ticketBets.map((bet, idx) => {
            const isEditing = editingIndex === idx;
            const alternatives = isEditing ? getAlternatives(bet) : [];

            return (
              <div key={idx} className={`ticket-modal-bet ${isEditing ? 'editing' : ''}`}>
                <div className="ticket-modal-bet-main">
                  <div className="ticket-modal-bet-info">
                    <div className="ticket-modal-bet-match">{bet.home_team} vs {bet.away_team}</div>
                    <div className="ticket-modal-bet-detail">
                      {formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)}
                    </div>
                  </div>
                  <span className="ticket-modal-bet-odds">@ {bet.odds.toFixed(2)}</span>
                  {predictions.length > 0 && (
                    <button
                      className={`ticket-modal-bet-edit ${isEditing ? 'active' : ''}`}
                      onClick={() => setEditingIndex(isEditing ? null : idx)}
                      title="Trocar mercado"
                    >
                      ✏️
                    </button>
                  )}
                  <button
                    className="ticket-modal-bet-remove"
                    onClick={() => onRemoveBet(idx)}
                    title="Remover aposta"
                  >
                    ×
                  </button>
                </div>

                {/* Painel de alternativas — agrupadas por mercado */}
                {isEditing && alternatives.length > 0 && (
                  <div className="ticket-modal-alternatives">
                    <div className="ticket-modal-alt-title">Selecione o mercado e resultado:</div>
                    {['MATCH_WINNER', 'OVER_UNDER', 'BTTS'].map(marketKey => {
                      const marketAlts = alternatives.filter(a => a.market === marketKey);
                      if (marketAlts.length === 0) return null;
                      return (
                        <div key={marketKey} className="ticket-modal-alt-group">
                          <div className="ticket-modal-alt-group-title">{formatMarket(marketKey)}</div>
                          {marketAlts.map((alt, altIdx) => {
                            const isCurrent = alt.market === bet.market && alt.predicted_outcome === bet.predicted_outcome;
                            return (
                              <button
                                key={altIdx}
                                className={`ticket-modal-alt-option ${isCurrent ? 'current' : ''}`}
                                onClick={() => !isCurrent && handleSelectAlternative(idx, alt)}
                                disabled={isCurrent}
                              >
                                <span className="alt-outcome">{formatOutcome(alt.market, alt.predicted_outcome)}</span>
                                <span className="alt-odds">@ {alt.odds.toFixed(2)}</span>
                                {alt.confidence > 0 && (
                                  <span className={`alt-ev ${alt.expected_value >= 0 ? 'alt-ev-pos' : 'alt-ev-neg'}`}>
                                    EV {alt.expected_value >= 0 ? '+' : ''}{(alt.expected_value * 100).toFixed(1)}%
                                  </span>
                                )}
                                {alt.confidence > 0 && (
                                  <span className={`pcm-rec recommendation-${alt.recommendation}`}>
                                    {alt.recommendation === 'STRONG_BET' ? '🔥' : alt.recommendation === 'RECOMMENDED' ? '✅' : alt.recommendation === 'CONSIDER' ? '💭' : '⛔'}
                                  </span>
                                )}
                                {isCurrent && <span className="alt-current-badge">atual</span>}
                              </button>
                            );
                          })}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className="ticket-modal-summary">
          <div className="ticket-modal-summary-row">
            <span>Apostas:</span>
            <span>{ticketBets.length}</span>
          </div>
          <div className="ticket-modal-summary-row">
            <span>Odd Combinada:</span>
            <span className="ticket-modal-highlight">{combinedOdds.toFixed(2)}</span>
          </div>
          <div className="ticket-modal-summary-row">
            <span>Stake:</span>
            <span>R$ {stake.toFixed(2)}</span>
          </div>
          <div className="ticket-modal-summary-row ticket-modal-summary-total">
            <span>Retorno Potencial:</span>
            <span className="ticket-modal-highlight">R$ {potentialReturn.toFixed(2)}</span>
          </div>
        </div>

        {/* Stake input */}
        <div className="ticket-modal-stake">
          <label>💰 Valor da Aposta (R$):</label>
          <input
            type="number"
            value={stake}
            onChange={(e) => onStakeChange(Number(e.target.value))}
            min="1"
            step="5"
          />
          <div className="ticket-modal-stake-presets">
            {[5, 10, 20, 50, 100].map(v => (
              <button
                key={v}
                className={`stake-preset-btn ${stake === v ? 'active' : ''}`}
                onClick={() => onStakeChange(v)}
              >
                R${v}
              </button>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="ticket-modal-actions">
          <button className="btn btn-secondary" onClick={onClose}>Cancelar</button>
          <button
            className="btn btn-primary"
            onClick={onCreate}
            disabled={creating || ticketBets.length === 0}
          >
            {creating ? '⏳ Criando...' : '🎫 Criar Bilhete'}
          </button>
        </div>
      </div>
    </div>
  );
};
