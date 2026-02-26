/**
 * AppContext - Contexto global da aplicação
 */
import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { Tab } from '../types';

interface AppContextType {
  activeTab: Tab;
  selectedLeagues: Set<string>;
  selectedStatuses: Set<string>;
  setActiveTab: (tab: Tab) => void;
  setSelectedLeagues: (leagues: Set<string>) => void;
  setSelectedStatuses: (statuses: Set<string>) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [selectedLeagues, setSelectedLeagues] = useState<Set<string>>(new Set());
  const [selectedStatuses, setSelectedStatuses] = useState<Set<string>>(new Set());

  return (
    <AppContext.Provider
      value={{
        activeTab,
        selectedLeagues,
        selectedStatuses,
        setActiveTab,
        setSelectedLeagues,
        setSelectedStatuses,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};
