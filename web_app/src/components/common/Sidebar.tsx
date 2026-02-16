/**
 * Sidebar/Tabs Component
 */
import React from 'react';
import type { Tab } from '../../types';

interface SidebarProps {
  activeTab: Tab;
  onTabChange: (tab: Tab) => void;
  predictionsCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, predictionsCount }) => {
  return (
    <div className="tabs">
      <button
        className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
        onClick={() => onTabChange('dashboard')}
      >
        📊 Dashboard
      </button>
      <button
        className={`tab ${activeTab === 'matches' ? 'active' : ''}`}
        onClick={() => onTabChange('matches')}
      >
        📅 Jogos
      </button>
      <button
        className={`tab ${activeTab === 'predictions' ? 'active' : ''}`}
        onClick={() => onTabChange('predictions')}
      >
        🎯 Previsões {predictionsCount > 0 && `(${predictionsCount})`}
      </button>
      <button
        className={`tab ${activeTab === 'tickets' ? 'active' : ''}`}
        onClick={() => onTabChange('tickets')}
      >
        🎫 Bilhetes
      </button>
    </div>
  );
};

