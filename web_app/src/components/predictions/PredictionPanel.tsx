/**
 * PredictionPanel Component
 */
import React from 'react';
import type { Prediction, MarketPrediction } from '../../types';
import { PredictionCard } from './PredictionCard';

interface PredictionPanelProps {
  predictions: Prediction[];
  onAddToTicket: (prediction: Prediction, market: MarketPrediction) => void;
}

export const PredictionPanel: React.FC<PredictionPanelProps> = ({ predictions, onAddToTicket }) => {
  if (predictions.length === 0) {
    return (
      <div className="empty-state">
        <h3>Nenhuma previsão ainda</h3>
        <p>Selecione jogos e clique em "Analisar"</p>
      </div>
    );
  }

  return (
    <div className="predictions-list">
      {predictions.map((pred) => (
        <PredictionCard
          key={pred.id}
          prediction={pred}
          onAddToTicket={onAddToTicket}
        />
      ))}
    </div>
  );
};

