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
import { TicketModal } from '../components/tickets/TicketModal';
import { usePrediction } from '../contexts/PredictionContext';
import { useTicket } from '../contexts/TicketContext';
import { useApp } from '../contexts/AppContext';
import { showSuccess } from '../services/notificationService';
import { formatMarket, formatOutcome, formatRecommendation } from '../components/predictions/PredictionCard';

const STRATEGIES: { value: Strategy; label: string; icon: string; desc: string }[] = [
  { value: 'CONSERVATIVE', label: 'Conservadora', icon: '🛡️', desc: 'Menos risco, odds menores' },
  { value: 'BALANCED', label: 'Balanceada', icon: '⚖️', desc: 'Equilíbrio risco/retorno' },
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
    replaceTicketBet,
    clearTicketBets,
    createTicket,
  } = useTicket();

  const [selectedBookmakerId, setSelectedBookmakerId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [creatingTicket, setCreatingTicket] = useState(false);

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

    // Abre o modal automaticamente
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleCreateTicket = async () => {
    setCreatingTicket(true);
    const bookmaker = selectedBookmakerId || ticketBets[0]?.bookmaker_id || 'bet365';
    const ticket = await createTicket(stake, bookmaker);
    setCreatingTicket(false);
    if (ticket) {
      setIsModalOpen(false);
      showSuccess('✅ Bilhete criado! Redirecionando...');
      setTimeout(() => setActiveTab('tickets'), 800);
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

      {/* Resumo das previsões — todas as odds de cada mercado */}
      <div className="predictions-summary">
        <h3 className="section-title">📊 Resumo das Previsões</h3>
        <div className="predictions-compact-list">
          {predictions.map((pred) => {
            // Pega odds da primeira bookmaker disponível para mostrar todas as opções
            const bkId = Object.keys(pred.odds_by_bookmaker || {})[0];
            const bkOdds = bkId ? pred.odds_by_bookmaker![bkId] : null;

            // Mapa de previsões por mercado+outcome
            const predMap = new Map(pred.predictions.map(m => [`${m.market}:${m.predicted_outcome}`, m]));

            // Monta todas as opções por mercado
            const allOptions: { market: string; outcome: string; odds: number; predicted?: { confidence: number; ev: number; recommendation: string } }[] = [];

            // MATCH_WINNER
            if (bkOdds?.home) allOptions.push({ market: 'MATCH_WINNER', outcome: 'HOME', odds: bkOdds.home, predicted: predMap.has('MATCH_WINNER:HOME') ? { confidence: predMap.get('MATCH_WINNER:HOME')!.confidence, ev: predMap.get('MATCH_WINNER:HOME')!.expected_value, recommendation: predMap.get('MATCH_WINNER:HOME')!.recommendation } : undefined });
            if (bkOdds?.draw) allOptions.push({ market: 'MATCH_WINNER', outcome: 'DRAW', odds: bkOdds.draw, predicted: predMap.has('MATCH_WINNER:DRAW') ? { confidence: predMap.get('MATCH_WINNER:DRAW')!.confidence, ev: predMap.get('MATCH_WINNER:DRAW')!.expected_value, recommendation: predMap.get('MATCH_WINNER:DRAW')!.recommendation } : undefined });
            if (bkOdds?.away) allOptions.push({ market: 'MATCH_WINNER', outcome: 'AWAY', odds: bkOdds.away, predicted: predMap.has('MATCH_WINNER:AWAY') ? { confidence: predMap.get('MATCH_WINNER:AWAY')!.confidence, ev: predMap.get('MATCH_WINNER:AWAY')!.expected_value, recommendation: predMap.get('MATCH_WINNER:AWAY')!.recommendation } : undefined });
            // OVER_UNDER
            if (bkOdds?.over_25) allOptions.push({ market: 'OVER_UNDER', outcome: 'OVER', odds: bkOdds.over_25, predicted: predMap.has('OVER_UNDER:OVER') ? { confidence: predMap.get('OVER_UNDER:OVER')!.confidence, ev: predMap.get('OVER_UNDER:OVER')!.expected_value, recommendation: predMap.get('OVER_UNDER:OVER')!.recommendation } : undefined });
            if (bkOdds?.under_25) allOptions.push({ market: 'OVER_UNDER', outcome: 'UNDER', odds: bkOdds.under_25, predicted: predMap.has('OVER_UNDER:UNDER') ? { confidence: predMap.get('OVER_UNDER:UNDER')!.confidence, ev: predMap.get('OVER_UNDER:UNDER')!.expected_value, recommendation: predMap.get('OVER_UNDER:UNDER')!.recommendation } : undefined });
            // BTTS
            if (bkOdds?.btts_yes) allOptions.push({ market: 'BTTS', outcome: 'YES', odds: bkOdds.btts_yes, predicted: predMap.has('BTTS:YES') ? { confidence: predMap.get('BTTS:YES')!.confidence, ev: predMap.get('BTTS:YES')!.expected_value, recommendation: predMap.get('BTTS:YES')!.recommendation } : undefined });
            if (bkOdds?.btts_no) allOptions.push({ market: 'BTTS', outcome: 'NO', odds: bkOdds.btts_no, predicted: predMap.has('BTTS:NO') ? { confidence: predMap.get('BTTS:NO')!.confidence, ev: predMap.get('BTTS:NO')!.expected_value, recommendation: predMap.get('BTTS:NO')!.recommendation } : undefined });

            // Se não temos odds_by_bookmaker, fallback para as previsões originais
            const hasFullOdds = allOptions.length > 0;

            return (
              <div key={pred.id} className="prediction-compact-card">
                <div className="prediction-compact-header">
                  <span className="prediction-compact-match">{pred.home_team} vs {pred.away_team}</span>
                  <span className="prediction-compact-league">{pred.league}</span>
                </div>
                <div className="prediction-compact-markets">
                  {hasFullOdds ? (
                    ['MATCH_WINNER', 'OVER_UNDER', 'BTTS'].map(marketKey => {
                      const opts = allOptions.filter(o => o.market === marketKey);
                      if (opts.length === 0) return null;
                      return (
                        <div key={marketKey} className="pcm-market-group">
                          <div className="pcm-market-group-title">{formatMarket(marketKey)}</div>
                          <div className="pcm-market-group-options">
                            {opts.map((opt, oi) => (
                              <div key={oi} className={`prediction-compact-market ${opt.predicted ? '' : 'pcm-no-prediction'}`}>
                                <span className="pcm-outcome">{formatOutcome(opt.market, opt.outcome)}</span>
                                <span className="pcm-odds">@ {opt.odds.toFixed(2)}</span>
                                {opt.predicted ? (
                                  <>
                                    <span className={`pcm-ev ${opt.predicted.ev >= 0 ? 'pcm-ev-positive' : 'pcm-ev-negative'}`}>
                                      {opt.predicted.ev >= 0 ? '+' : ''}{(opt.predicted.ev * 100).toFixed(1)}%
                                    </span>
                                    <span className="pcm-confidence">{(opt.predicted.confidence * 100).toFixed(0)}%</span>
                                    <span className={`pcm-rec recommendation-${opt.predicted.recommendation}`}>{formatRecommendation(opt.predicted.recommendation)}</span>
                                  </>
                                ) : (
                                  <span className="pcm-no-analysis">—</span>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    // Fallback: mostra só as previsões originais
                    pred.predictions.map((m, idx) => (
                      <div key={idx} className={`prediction-compact-market ${m.recommendation === 'AVOID' ? 'pcm-not-recommended' : ''}`}>
                        <span className="pcm-name">{formatMarket(m.market)}</span>
                        <span className="pcm-outcome">{formatOutcome(m.market, m.predicted_outcome)}</span>
                        <span className="pcm-odds">@ {m.odds.toFixed(2)}</span>
                        <span className={`pcm-ev ${m.expected_value >= 0 ? 'pcm-ev-positive' : 'pcm-ev-negative'}`}>
                          {m.expected_value >= 0 ? '+' : ''}{(m.expected_value * 100).toFixed(1)}%
                        </span>
                        <span className="pcm-confidence">{(m.confidence * 100).toFixed(0)}%</span>
                        <span className={`pcm-rec recommendation-${m.recommendation}`}>{formatRecommendation(m.recommendation)}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            );
          })}
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

      {/* Modal de Bilhete (abre ao clicar "Usar Bet365" / "Usar Betano") */}
      <TicketModal
        isOpen={isModalOpen}
        ticketBets={ticketBets}
        stake={stake}
        onStakeChange={setStake}
        onRemoveBet={removeFromTicket}
        onReplaceBet={replaceTicketBet}
        onClose={handleCloseModal}
        onCreate={handleCreateTicket}
        bookmakerName={selectedBookmakerId ? (BOOKMAKER_NAMES[selectedBookmakerId] || selectedBookmakerId) : undefined}
        bookmakerId={selectedBookmakerId || undefined}
        creating={creatingTicket}
        predictions={predictions}
      />
    </>
  );
};

