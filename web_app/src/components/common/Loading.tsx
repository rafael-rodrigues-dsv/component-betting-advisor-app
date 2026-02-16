/**
 * Loading Component
 */
import React from 'react';

interface LoadingProps {
  message?: string;
}

export const Loading: React.FC<LoadingProps> = ({ message = 'Carregando...' }) => {
  return (
    <div className="loading">
      <div className="spinner"></div>
      <span>{message}</span>
    </div>
  );
};

