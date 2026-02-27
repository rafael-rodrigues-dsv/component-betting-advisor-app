/**
 * Matches Page - Página de seleção de jogos
 */
import React, { useState, useEffect } from 'react';
import { MatchList } from '../components/matches/MatchList';
import { useMatchesContext } from '../contexts/MatchesContext';
import { usePrediction } from '../contexts/PredictionContext';
import { useApp } from '../contexts/AppContext';
import { showWarning } from '../services/notificationService';

export const MatchesPage: React.FC = () => {
  const [selectedMatches, setSelectedMatches] = useState<Set<string>>(new Set());

  // Contexts
  const { selectedLeagues, setSelectedLeagues, selectedStatuses, setSelectedStatuses, setActiveTab } = useApp();

  // Hooks
  const { matches, leagues, preloading, selectedPeriod, dataLoaded, fetchByPeriod, loadOddsForLeagues, updateMatchOddsAndStatus, loadingOdds, oddsProgress, livePolling, startLivePolling, stopLivePolling } = useMatchesContext();
  const { analyzing, analyze } = usePrediction();

  // Inicia polling ao entrar na aba de jogos, para ao sair
  useEffect(() => {
    if (dataLoaded && !loadingOdds) {
      startLivePolling();
    }
    return () => {
      stopLivePolling();
    };
  }, [dataLoaded, loadingOdds, startLivePolling, stopLivePolling]);

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

  const selectMultiple = (matchIds: string[]) => {
    setSelectedMatches(prev => {
      const newSet = new Set(prev);
      matchIds.forEach(id => newSet.add(id));
      return newSet;
    });
  };

  const deselectAll = () => {
    setSelectedMatches(new Set());
  };

  const handleAnalyze = async () => {
    if (selectedMatches.size === 0) {
      showWarning('⚠️ Selecione pelo menos um jogo para analisar');
      return;
    }

    // Default: CONSERVATIVE ao analisar pela primeira vez
    const success = await analyze(Array.from(selectedMatches), 'CONSERVATIVE');
    if (success) {
      setActiveTab('predictions');
    }
  };

  return (
    <MatchList
      matches={matches}
      selectedMatches={selectedMatches}
      onSelectMatch={toggleMatchSelection}
      onSelectAll={selectMultiple}
      onDeselectAll={deselectAll}
      analyzing={analyzing}
      onAnalyze={handleAnalyze}
      leagues={leagues}
      selectedLeagues={selectedLeagues}
      onLeaguesChange={setSelectedLeagues}
      selectedStatuses={selectedStatuses}
      onStatusesChange={setSelectedStatuses}
      preloading={preloading}
      selectedPeriod={selectedPeriod}
      dataLoaded={dataLoaded}
      onFetchByPeriod={fetchByPeriod}
      onLoadOddsForLeagues={loadOddsForLeagues}
      onOddsRefreshed={updateMatchOddsAndStatus}
      loadingOdds={loadingOdds}
      oddsProgress={oddsProgress}
      livePolling={livePolling}
    />
  );
};
