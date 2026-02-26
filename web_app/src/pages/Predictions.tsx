/**
 * Predictions Page - Página de previsões
 *
 * Layout:
 * 1. Seletor de estratégia (re-analisa ao trocar)
 * 2. Comparação de bilhetes entre casas de apostas (editável)
 * 3. Montagem final do bilhete (após escolher a casa)
 */
import React, { useState, useEffect } from 'react';
import type { Strategy } from '../types';
import { BookmakerComparison } from '../components/predictions/BookmakerComparison';
import { TicketBuilder } from '../components/tickets/TicketBuilder';
import { usePrediction } from '../contexts/PredictionContext';
import { useTicket } from '../contexts/TicketContext';
import { useApp } from '../contexts/AppContext';
import { showSuccess } from '../services/notificationService';
import { formatMarket, formatOutcome, formatRecommendation } from '../components/predictions/PredictionCard';

const STRATEGIES: { value: Strategy; label: string; icon: string; desc: string }[] = [
  { value: 'CONSERVATIVE', label: 'Conservadora', icon: '🛡️', desc: 'Menos risco, odds menores' },
  { value: 'BALANCED', label: 'Balanceada', icon: '⚖️', desc: 'Equilíbrio risco/retorno' },
  { value: 'VALUE_BET', label: 'Value Bet', icon: '💰', desc: 'Foco em valor esperado' },
  { value: 'AGGRESSIVE', label: 'Agressiva', icon: '🔥', desc: 'Mais risco, odds maiores' },
];

export const PredictionsPage: React.FC = () => {
  const { setActiveTab } = useApp();
  const { predictions, preTicket, analyzing, currentStrategy, reAnalyze } = usePrediction();
  const {
    ticketBets,
    stake,
    setStake,
    addToTicket,
    removeFromTicket,
    clearTicketBets,
    createTicket,
  } = useTicket();

  const [selectedBookmakerId, setSelectedBookmakerId] = useState<string | null>(null);

  // Limpa seleção de bookmaker quando novas previsões chegam
  useEffect(() => {
    setSelectedBookmakerId(null);
    clearTicketBets();
  }, [predictions]);

  const handleStrategyChange = async (strategy: Strategy) => {
    if (strategy === currentStrategy || analyzing) return;
    setSelectedBookmakerId(null);
    clearTicketBets();
    await reAnalyze(strategy);
  };

  const handleSelectBookmaker = (bookmakerId: string, bets: Array<{
    match_id: string; home_team: string; away_team: string; league: string;
    market: string; predicted_outcome: string; odds: number; confidence: number;
  }>) => {
    setSelectedBookmakerId(bookmakerId);
    clearTicketBets();

    bets.forEach((bet) => {
      const prediction = predictions.find(p => p.match_id === bet.match_id);
      if (prediction) {
        prediction.bookmaker_id = bookmakerId;
        addToTicket(prediction, {
          market: bet.market,
          predicted_outcome: bet.predicted_outcome,
          odds: bet.odds,
          confidence: bet.confidence,
          expected_value: 0,
          recommendation: 'RECOMMENDED',
        });
      }
    });
  };

  const handleCreateTicket = async () => {
    const bookmaker = selectedBookmakerId || ticketBets[0]?.bookmaker_id || 'bet365';
    const ticket = await createTicket(stake, bookmaker);
    if (ticket) {
      showSuccess('✅ Bilhete criado! Redirecionando...');
      setTimeout(() => setActiveTab('tickets'), 1000);
    }
  };

  const preTicketBets = preTicket?.bets || [];

  const BOOKMAKER_NAMES: Record<string, string> = {
    'bet365': 'Bet365',
    'betano': 'Betano',
  };

  if (predictions.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">🔍</div>
        <h3>Nenhuma previsão ainda</h3>
        <p>Selecione jogos na aba "Jogos" e clique em "Analisar Selecionados"</p>
      </div>
    );
  }

  return (
    <>
      {/* Seletor de Estratégia */}
      <div className="strategy-selector">
        <div className="strategy-header">
          <h3>🎯 Estratégia de Análise</h3>
          <span className="strategy-match-count">{predictions.length} jogo{predictions.length > 1 ? 's' : ''} analisado{predictions.length > 1 ? 's' : ''}</span>
        </div>
        <div className="strategy-options">
          {STRATEGIES.map(s => (
            <button
              key={s.value}
              className={`strategy-option ${currentStrategy === s.value ? 'active' : ''}`}
              onClick={() => handleStrategyChange(s.value)}
              disabled={analyzing}
            >
              <span className="strategy-icon">{s.icon}</span>
              <span className="strategy-label">{s.label}</span>
              <span className="strategy-desc">{s.desc}</span>
              {analyzing && currentStrategy !== s.value && <span className="strategy-loading">⏳</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Resumo das previsões (compacto) */}
      <div className="predictions-summary">
        <h3 className="section-title">📊 Resumo das Previsões</h3>
        <div className="predictions-compact-list">
          {predictions.map((pred) => (
            <div key={pred.id} className="prediction-compact-card">
              <div className="prediction-compact-header">
                <span className="prediction-compact-match">{pred.home_team} vs {pred.away_team}</span>
                <span className="prediction-compact-league">{pred.league}</span>
              </div>
              <div className="prediction-compact-markets">
                {pred.predictions.map((m, idx) => (
                  <div key={idx} className="prediction-compact-market">
                    <span className="pcm-name">{formatMarket(m.market)}</span>
                    <span className="pcm-outcome">{formatOutcome(m.market, m.predicted_outcome)}</span>
                    <span className="pcm-odds">@ {m.odds.toFixed(2)}</span>
                    <span className="pcm-confidence">{(m.confidence * 100).toFixed(0)}%</span>
                    <span className={`pcm-rec recommendation-${m.recommendation}`}>{formatRecommendation(m.recommendation)}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Valor da Aposta */}
      <div className="stake-input-section">
        <h3 className="section-title">💰 Valor da Aposta</h3>
        <div className="stake-input-row">
          <label htmlFor="stake-input">Valor (R$):</label>
          <input
            id="stake-input"
            type="number"
            className="stake-input"
            min="1"
            step="5"
            value={stake}
            onChange={(e) => setStake(Number(e.target.value))}
            placeholder="Ex: 10"
          />
          <div className="stake-presets">
            {[5, 10, 20, 50, 100].map(v => (
              <button
                key={v}
                className={`stake-preset-btn ${stake === v ? 'active' : ''}`}
                onClick={() => setStake(v)}
              >
                R${v}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Comparação entre casas de apostas */}
      {preTicketBets.length > 0 && (
        <BookmakerComparison
          predictions={predictions}
          preTicketBets={preTicketBets}
          stake={stake}
          onSelectBookmaker={handleSelectBookmaker}
        />
      )}

      {/* Bilhete montado (após escolher casa) */}
      {selectedBookmakerId && ticketBets.length > 0 && (
        <TicketBuilder
          ticketBets={ticketBets}
          stake={stake}
          onStakeChange={setStake}
          onRemoveBet={removeFromTicket}
          onClear={() => { clearTicketBets(); setSelectedBookmakerId(null); }}
          onCreate={handleCreateTicket}
          bookmakerName={BOOKMAKER_NAMES[selectedBookmakerId] || selectedBookmakerId}
        />
      )}
    </>
  );
};

