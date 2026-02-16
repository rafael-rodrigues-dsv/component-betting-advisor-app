/**
 * Matches Page - Página de seleção de jogos
 */
import React, { useState } from 'react';
import { MatchList } from '../components/matches/MatchList';
import { useMatches } from '../hooks/useMatches';
import { usePrediction } from '../contexts/PredictionContext';
import { useApp } from '../contexts/AppContext';
import { useBookmaker } from '../contexts/BookmakerContext';
import { useTicket } from '../contexts/TicketContext';
import { showWarning } from '../services/notificationService';

export const MatchesPage: React.FC = () => {
  const [selectedMatches, setSelectedMatches] = useState<Set<string>>(new Set());

  // Contexts
  const { strategy, selectedLeague, setStrategy, setSelectedLeague, setActiveTab } = useApp();
  const { bookmakers, selectedBookmaker, setSelectedBookmaker } = useBookmaker();
  const { ticketBets, clearTicketBets } = useTicket();

  // Hooks
  const { matches, leagues, loading } = useMatches(selectedLeague);
  const { analyzing, analyze } = usePrediction();

  // Handlers
  const toggleMatchSelection = (matchId: string) => {
    const newSelected = new Set(selectedMatches);
    if (newSelected.has(matchId)) {
      newSelected.delete(matchId);
    } else {
      newSelected.add(matchId);
    }
    setSelectedMatches(newSelected);
  };

  const handleAnalyze = async () => {
    if (selectedMatches.size === 0) {
      showWarning('⚠️ Selecione pelo menos um jogo para analisar');
      return;
    }

    const success = await analyze(Array.from(selectedMatches), strategy);
    if (success) {

      setActiveTab('predictions');
    }
  };

  const handleBookmakerChange = (bookmakerId: string) => {
    // Ao trocar de casa de apostas, limpa o bilhete se tiver apostas
    if (ticketBets.length > 0) {
      if (window.confirm('Trocar de casa de apostas irá limpar seu bilhete atual. Deseja continuar?')) {
        clearTicketBets();
        setSelectedBookmaker(bookmakerId);
      }
    } else {
      setSelectedBookmaker(bookmakerId);
    }
  };

  return (
    <MatchList
      matches={matches}
      selectedMatches={selectedMatches}
      onSelectMatch={toggleMatchSelection}
      loading={loading}
      analyzing={analyzing}
      onAnalyze={handleAnalyze}
      strategy={strategy}
      onStrategyChange={setStrategy}
      leagues={leagues}
      selectedLeague={selectedLeague}
      onLeagueChange={setSelectedLeague}
      bookmakers={bookmakers}
      selectedBookmaker={selectedBookmaker}
      onBookmakerChange={handleBookmakerChange}
    />
  );
};

