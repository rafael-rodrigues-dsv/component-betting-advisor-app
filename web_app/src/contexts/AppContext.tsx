/**
 * AppContext - Contexto global da aplicação
 */
import React, { createContext, useContext, useState, ReactNode } from 'react';
import type { Tab } from '../types';

interface AppContextType {
  activeTab: Tab;
  selectedLeague: string;
  setActiveTab: (tab: Tab) => void;
  setSelectedLeague: (leagueId: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [selectedLeague, setSelectedLeague] = useState<string>('all');

  return (
    <AppContext.Provider
      value={{
        activeTab,
        selectedLeague,
        setActiveTab,
        setSelectedLeague,
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
