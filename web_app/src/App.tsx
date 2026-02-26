/**
 * App.tsx - Componente Principal (Refatorado)
 */
import React from 'react';

// Contexts
import { AppProvider, useApp } from './contexts/AppContext';
import { BookmakerProvider } from './contexts/BookmakerContext';
import { TicketProvider } from './contexts/TicketContext';
import { PredictionProvider, usePrediction } from './contexts/PredictionContext';

// Components
import { Header } from './components/common/Header';
import { Sidebar } from './components/common/Sidebar';

// Pages
import { DashboardPage, MatchesPage, PredictionsPage, TicketsPage } from './pages';

// Hooks
import { useTicket } from './contexts/TicketContext';

// Styles
import './styles/globals.css';

const AppContent: React.FC = () => {
  const { activeTab, setActiveTab } = useApp();
  const { predictions } = usePrediction();
  const { ticketBets } = useTicket();

  return (
    <div className="app">
      <Header
        matchesCount={0}
        selectedCount={0}
        ticketBetsCount={ticketBets.length}
      />

      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        predictionsCount={predictions.length}
      />

      {/* Dashboard */}
      {activeTab === 'dashboard' && <DashboardPage />}

      {/* Matches */}
      {activeTab === 'matches' && <MatchesPage />}

      {/* Predictions */}
      {activeTab === 'predictions' && <PredictionsPage />}

      {/* Tickets */}
      {activeTab === 'tickets' && <TicketsPage />}
    </div>
  );
};

function App() {
  return (
    <AppProvider>
      <BookmakerProvider>
        <PredictionProvider>
          <TicketProvider>
            <AppContent />
          </TicketProvider>
        </PredictionProvider>
      </BookmakerProvider>
    </AppProvider>
  );
}

export default App;

