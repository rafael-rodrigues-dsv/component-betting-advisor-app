/**
 * ConfidenceMeter Component
 */
import React from 'react';

interface ConfidenceMeterProps {
  confidence: number;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ confidence }) => {
  return (
    <div className="market-confidence">
      <label className="stat-label">Confiança</label>
      <div className="confidence-bar">
        <div className="confidence-fill" style={{ width: `${confidence * 100}%` }} />
      </div>
      <span className="confidence-text">{(confidence * 100).toFixed(0)}%</span>
    </div>
  );
};

