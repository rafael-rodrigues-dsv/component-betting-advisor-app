/**
 * Header Component
 */
import React from 'react';

interface HeaderProps {
  matchesCount: number;
  selectedCount: number;
  ticketBetsCount: number;
}

export const Header: React.FC<HeaderProps> = ({ matchesCount, selectedCount, ticketBetsCount }) => {
  return (
    <header className="header">
      <h1>⚽ Betting Advisor</h1>
      <div className="header-stats">
        <div className="stat-item">
          <span className="stat-value">{matchesCount}</span>
          <span className="stat-label">Jogos</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{selectedCount}</span>
          <span className="stat-label">Selecionados</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{ticketBetsCount}</span>
          <span className="stat-label">No Bilhete</span>
        </div>
      </div>
    </header>
  );
};

