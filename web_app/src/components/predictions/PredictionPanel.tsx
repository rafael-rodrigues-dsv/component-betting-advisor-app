/**
 * PredictionPanel Component
 */
import React from 'react';
import type { Prediction, MarketPrediction } from '../../types';
import { PredictionCard } from './PredictionCard';

interface PredictionPanelProps {
  predictions: Prediction[];
  onAddToTicket: (prediction: Prediction, market: MarketPrediction) => void;
  showAddButton?: boolean;
}

export const PredictionPanel: React.FC<PredictionPanelProps> = ({ predictions, onAddToTicket, showAddButton = false }) => {
  if (predictions.length === 0) {
    return null;
  }

  return (
    <div className="predictions-section">
      <h3 className="section-title">📊 Análise das Previsões</h3>
      <div className="predictions-list">
        {predictions.map((pred) => (
          <PredictionCard
            key={pred.id}
            prediction={pred}
            onAddToTicket={onAddToTicket}
            showAddButton={showAddButton}
          />
        ))}
      </div>
    </div>
  );
};
