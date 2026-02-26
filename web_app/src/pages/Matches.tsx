/**
 * Matches Page - Página de seleção de jogos
 */
import React, { useState } from 'react';
import { MatchList } from '../components/matches/MatchList';
import { useMatchesContext } from '../contexts/MatchesContext';
import { usePrediction } from '../contexts/PredictionContext';
import { useApp } from '../contexts/AppContext';
import { showWarning } from '../services/notificationService';

export const MatchesPage: React.FC = () => {
  const [selectedMatches, setSelectedMatches] = useState<Set<string>>(new Set());

  // Contexts
  const { strategy, selectedLeague, setStrategy, setSelectedLeague, setActiveTab } = useApp();

  // Hooks
  const { matches, leagues, preloading, selectedPeriod, dataLoaded, fetchByPeriod, loadingOdds, oddsProgress, updateMatchOddsAndStatus } = useMatchesContext();
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

  return (
    <MatchList
      matches={matches}
      selectedMatches={selectedMatches}
      onSelectMatch={toggleMatchSelection}
      analyzing={analyzing}
      onAnalyze={handleAnalyze}
      strategy={strategy}
      onStrategyChange={setStrategy}
      leagues={leagues}
      selectedLeague={selectedLeague}
      onLeagueChange={setSelectedLeague}
      preloading={preloading}
      selectedPeriod={selectedPeriod}
      dataLoaded={dataLoaded}
      onFetchByPeriod={fetchByPeriod}
      onOddsRefreshed={updateMatchOddsAndStatus}
      loadingOdds={loadingOdds}
      oddsProgress={oddsProgress}
    />
  );
};

