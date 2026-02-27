/**
 * TicketModal Component — Lista Flat Limpa
 *
 * Modal com:
 * - Header: título + bookmaker + botão fechar
 * - Lista flat de apostas (sem accordion)
 * - Cada card: times + liga + data + mercado selecionado + odds
 * - Dropdown inline para trocar mercado
 * - Footer compacto: resumo inline + stake + criar bilhete
 */
import React, { useEffect, useState, useRef, useCallback } from 'react';
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

type Alternative = {
  market: string;
  predicted_outcome: string;
  odds: number;
  confidence: number;
  expected_value: number;
  recommendation: string;
};

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
  const bodyRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  // Keyboard / body lock
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

  useEffect(() => {
    if (!isOpen) setEditingIndex(null);
  }, [isOpen]);

  // Auto-scroll ao abrir dropdown
  useEffect(() => {
    if (editingIndex !== null) {
      setTimeout(() => {
        const el = cardRefs.current.get(editingIndex);
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }, 50);
    }
  }, [editingIndex]);

  const setCardRef = useCallback((idx: number, el: HTMLDivElement | null) => {
    if (el) cardRefs.current.set(idx, el);
    else cardRefs.current.delete(idx);
  }, []);

  if (!isOpen || ticketBets.length === 0) return null;

  const combinedOdds = ticketBets.reduce((acc, bet) => acc * bet.odds, 1);
  const potentialReturn = stake * combinedOdds;

  // Alternativas de aposta
  const getAlternatives = (bet: TicketBet): Alternative[] => {
    const pred = predictions.find(p => p.match_id === bet.match_id);
    if (!pred) return [];

    const bkId = bookmakerId || Object.keys(pred.odds_by_bookmaker || {})[0];
    const bkOdds = bkId ? pred.odds_by_bookmaker?.[bkId] : null;
    const predMap = new Map(pred.predictions.map(m => [`${m.market}:${m.predicted_outcome}`, m]));
    const alts: Alternative[] = [];

    const options = [
      { market: 'MATCH_WINNER', outcome: 'HOME', key: 'home' },
      { market: 'MATCH_WINNER', outcome: 'DRAW', key: 'draw' },
      { market: 'MATCH_WINNER', outcome: 'AWAY', key: 'away' },
      { market: 'OVER_UNDER', outcome: 'OVER', key: 'over_25' },
      { market: 'OVER_UNDER', outcome: 'UNDER', key: 'under_25' },
      { market: 'BTTS', outcome: 'YES', key: 'btts_yes' },
      { market: 'BTTS', outcome: 'NO', key: 'btts_no' },
    ];

    for (const { market, outcome, key } of options) {
      const odd = bkOdds?.[key as keyof typeof bkOdds] as number | undefined;
      if (!odd || odd <= 0) continue;
      const orig = predMap.get(`${market}:${outcome}`);
      alts.push({
        market, predicted_outcome: outcome, odds: odd,
        confidence: orig?.confidence ?? 0,
        expected_value: orig?.expected_value ?? 0,
        recommendation: orig?.recommendation ?? 'CONSIDER',
      });
    }
    return alts;
  };

  const handleSelect = (idx: number, alt: Alternative) => {
    onReplaceBet(idx, {
      ...ticketBets[idx],
      market: alt.market,
      predicted_outcome: alt.predicted_outcome,
      odds: alt.odds,
      confidence: alt.confidence,
    });
    setEditingIndex(null);
  };

  const recIcon = (r: string) =>
    r === 'STRONG_BET' ? '🔥' : r === 'RECOMMENDED' ? '✅' : r === 'CONSIDER' ? '💭' : '⛔';

  return (
    <div className="tm-overlay" onClick={onClose}>
      <div className="tm-modal" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="tm-header">
          <div className="tm-header-left">
            <span className="tm-title">🎫 Novo Bilhete</span>
            {bookmakerName && <span className="tm-bookmaker-badge">🎰 {bookmakerName}</span>}
            <span className="tm-bet-count">{ticketBets.length} {ticketBets.length === 1 ? 'aposta' : 'apostas'}</span>
          </div>
          <button className="tm-close" onClick={onClose} title="Fechar (ESC)">×</button>
        </div>

        {/* Lista flat de apostas */}
        <div className="tm-body" ref={bodyRef}>
          {ticketBets.map((bet, idx) => {
            const isEditing = editingIndex === idx;
            const alternatives = isEditing ? getAlternatives(bet) : [];

            return (
              <div
                key={idx}
                className={`tm-card ${isEditing ? 'tm-card-editing' : ''}`}
                ref={el => setCardRef(idx, el)}
              >
                {/* Linha 1: Times + Odds + Ações */}
                <div className="tm-card-row1">
                  <div className="tm-card-info">
                    <span className="tm-card-teams">{bet.home_team} vs {bet.away_team}</span>
                    <span className="tm-card-meta">
                      🏆 {bet.league}
                      {bet.date && <> · {new Date(bet.date).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })}</>}
                    </span>
                  </div>
                  <span className="tm-card-odds">@ {bet.odds.toFixed(2)}</span>
                  <button className="tm-card-remove" onClick={() => onRemoveBet(idx)} title="Remover">✕</button>
                </div>

                {/* Linha 2: Mercado selecionado + Trocar */}
                <div className="tm-card-row2">
                  <span className="tm-card-selection">
                    {formatMarket(bet.market)}: <strong>{formatOutcome(bet.market, bet.predicted_outcome)}</strong>
                  </span>
                  {predictions.length > 0 && (
                    <button
                      className={`tm-card-change ${isEditing ? 'active' : ''}`}
                      onClick={() => setEditingIndex(isEditing ? null : idx)}
                    >
                      {isEditing ? 'Fechar ▲' : 'Trocar ▼'}
                    </button>
                  )}
                </div>

                {/* Dropdown de alternativas */}
                {isEditing && alternatives.length > 0 && (
                  <div className="tm-dropdown">
                    {alternatives.map((alt, ai) => {
                      const isCurrent = alt.market === bet.market && alt.predicted_outcome === bet.predicted_outcome;
                      return (
                        <button
                          key={ai}
                          className={`tm-dropdown-item ${isCurrent ? 'tm-dropdown-current' : ''}`}
                          onClick={() => !isCurrent && handleSelect(idx, alt)}
                          disabled={isCurrent}
                        >
                          <span className="tm-dropdown-label">
                            {formatOutcome(alt.market, alt.predicted_outcome)}
                            <span className="tm-dropdown-market-hint">{formatMarket(alt.market)}</span>
                          </span>
                          <span className="tm-dropdown-odds">@ {alt.odds.toFixed(2)}</span>
                          {alt.confidence > 0 && (
                            <span className={`tm-dropdown-ev ${alt.expected_value >= 0 ? 'ev-pos' : 'ev-neg'}`}>
                              EV {alt.expected_value >= 0 ? '+' : ''}{(alt.expected_value * 100).toFixed(1)}%
                            </span>
                          )}
                          <span className="tm-dropdown-rec">{recIcon(alt.recommendation)}</span>
                          {isCurrent && <span className="tm-dropdown-tag">atual</span>}
                        </button>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Footer compacto */}
        <div className="tm-footer">
          <div className="tm-footer-row">
            <span className="tm-footer-info">
              {ticketBets.length} apostas · Odd <strong>{combinedOdds.toFixed(2)}</strong> · Retorno <strong>R$ {potentialReturn.toFixed(2)}</strong>
            </span>
          </div>
          <div className="tm-footer-row">
            <div className="tm-stake-row">
              <label className="tm-stake-label">💰</label>
              <input
                type="number"
                value={stake}
                onChange={e => onStakeChange(Number(e.target.value))}
                min="1"
                step="5"
                className="tm-stake-input"
              />
              <div className="tm-stake-presets">
                {[5, 10, 25, 50, 100].map(v => (
                  <button
                    key={v}
                    className={`tm-stake-btn ${stake === v ? 'active' : ''}`}
                    onClick={() => onStakeChange(v)}
                  >
                    {v}
                  </button>
                ))}
              </div>
            </div>
            <div className="tm-footer-actions">
              <button className="btn btn-secondary tm-cancel-btn" onClick={onClose}>Cancelar</button>
              <button
                className="btn btn-primary tm-create-btn"
                onClick={onCreate}
                disabled={creating || ticketBets.length === 0}
              >
                {creating ? '⏳ Criando...' : '🎫 Criar Bilhete'}
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
