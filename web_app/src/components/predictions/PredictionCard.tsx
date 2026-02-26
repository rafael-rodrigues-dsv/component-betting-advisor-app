/**
 * PredictionCard Component
 */
import React from 'react';
import type { Prediction, MarketPrediction } from '../../types';
import { ConfidenceMeter } from './ConfidenceMeter';

// Formatters
const formatMarket = (market: string): string => {
  const names: Record<string, string> = {
    'MATCH_WINNER': '⚽ Resultado Final',
    'OVER_UNDER': '🎯 Total de Gols',
    'BTTS': '⚡ Ambos Marcam',
  };
  return names[market] || market;
};

const formatOutcome = (market: string, outcome: string): string => {
  if (market === 'MATCH_WINNER') {
    const names: Record<string, string> = {
      HOME: '🏠 Vitória do Mandante',
      DRAW: '🤝 Empate',
      AWAY: '✈️ Vitória do Visitante'
    };
    return names[outcome] || outcome;
  }
  if (market === 'OVER_UNDER') {
    if (outcome.startsWith('OVER')) return '⬆️ Mais de 2.5 gols';
    if (outcome.startsWith('UNDER')) return '⬇️ Menos de 2.5 gols';
    return outcome;
  }
  if (market === 'BTTS') {
    return outcome === 'YES' ? '✅ Sim' : '❌ Não';
  }
  return outcome;
};

const formatRecommendation = (rec: string): string => {
  const names: Record<string, string> = {
    'STRONG_BET': '🔥 Aposta Forte',
    'RECOMMENDED': '✅ Recomendada',
    'CONSIDER': '💭 Considerar',
    'AVOID': '⛔ Evitar',
  };
  return names[rec] || rec;
};

interface PredictionCardProps {
  prediction: Prediction;
  onAddToTicket: (prediction: Prediction, market: MarketPrediction) => void;
  showAddButton?: boolean;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ prediction, onAddToTicket, showAddButton = true }) => {
  return (
    <div className="prediction-card">
      <div className="prediction-header">
        <div>
          <div className="prediction-match">{prediction.home_team} vs {prediction.away_team}</div>
          <div className="prediction-league">{prediction.league}</div>
        </div>
        {prediction.bookmaker_name && (
          <div className="bookmaker-badge-prediction">
            🎰 {prediction.bookmaker_name}
          </div>
        )}
      </div>
      <div className="prediction-markets">
        {prediction.predictions.map((market, idx) => (
          <div key={idx} className="market-item">
            <div className="market-info">
              <div className="market-name">{formatMarket(market.market)}</div>
              <div className="market-prediction">{formatOutcome(market.market, market.predicted_outcome)}</div>
            </div>
            <div className="market-stats">
              <ConfidenceMeter confidence={market.confidence} />
              <div className="market-odds-block">
                <label className="stat-label">Cotação</label>
                <div className="market-odds">{market.odds.toFixed(2)}</div>
              </div>
              <div className={`market-ev ${market.expected_value >= 0 ? 'ev-positive' : 'ev-negative'}`}>
                <label className="stat-label">Value</label>
                <span className="ev-value">{market.expected_value >= 0 ? '+' : ''}{(market.expected_value * 100).toFixed(1)}%</span>
              </div>
              <span className={`recommendation-badge recommendation-${market.recommendation}`}>
                {formatRecommendation(market.recommendation)}
              </span>
            </div>
            {showAddButton && (
              <button className="add-to-ticket-btn" onClick={() => onAddToTicket(prediction, market)}>
                ➕ Adicionar ao Bilhete
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export { formatMarket, formatOutcome, formatRecommendation };

