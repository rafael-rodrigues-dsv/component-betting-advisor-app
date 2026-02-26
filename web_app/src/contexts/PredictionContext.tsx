/**
 * PredictionContext - Gerencia análises e previsões
 */
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type { Prediction, Strategy } from '../types';
import { predictionsApi } from '../services/api';
import { showNotification, showError } from '../services/notificationService';

interface PreTicket {
  bets: any[];
  total_bets: number;
  combined_odds: number;
  message: string;
}

interface PredictionContextType {
  predictions: Prediction[];
  analyzing: boolean;
  preTicket: PreTicket | null;
  currentStrategy: Strategy;
  lastMatchIds: string[];
  analyze: (matchIds: string[], strategy: Strategy) => Promise<boolean>;
  reAnalyze: (strategy: Strategy) => Promise<boolean>;
  clearPredictions: () => void;
}

const PredictionContext = createContext<PredictionContextType | undefined>(undefined);

export const PredictionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [preTicket, setPreTicket] = useState<PreTicket | null>(null);
  const [currentStrategy, setCurrentStrategy] = useState<Strategy>('CONSERVATIVE');
  const [lastMatchIds, setLastMatchIds] = useState<string[]>([]);

  const analyze = useCallback(async (matchIds: string[], strategy: Strategy): Promise<boolean> => {
    if (matchIds.length === 0) {
      showNotification('⚠️ Selecione ao menos um jogo', 'warning');
      return false;
    }

    setAnalyzing(true);
    setCurrentStrategy(strategy);
    setLastMatchIds(matchIds);
    try {
      const data = await predictionsApi.analyze(matchIds, strategy);
      if (data.predictions && Array.isArray(data.predictions)) {
        // Filtra predictions que tenham pelo menos 1 market prediction
        const validPredictions = data.predictions.filter(
          (p: any) => p.predictions && p.predictions.length > 0
        );

        setPredictions(validPredictions);

        // Armazena pré-bilhete se veio do backend
        if (data.pre_ticket) {
          setPreTicket(data.pre_ticket);
        }

        if (validPredictions.length > 0) {
          showNotification(`✅ ${validPredictions.length} previsão(ões) gerada(s)!`, 'success');
          return true;
        }

        showError('❌ Nenhuma previsão gerada. Verifique se os jogos possuem odds carregadas.');
        return false;
      }

      showError('❌ Nenhuma previsão foi gerada');
      return false;
    } catch (error) {
      console.error('Erro ao analisar:', error);
      showError('❌ Erro ao analisar jogos');
      return false;
    } finally {
      setAnalyzing(false);
    }
  }, []);

  const reAnalyze = useCallback(async (strategy: Strategy): Promise<boolean> => {
    if (lastMatchIds.length === 0) return false;
    return analyze(lastMatchIds, strategy);
  }, [lastMatchIds, analyze]);

  const clearPredictions = useCallback(() => {
    setPredictions([]);
    setPreTicket(null);
  }, []);

  return (
    <PredictionContext.Provider
      value={{
        predictions,
        analyzing,
        preTicket,
        currentStrategy,
        lastMatchIds,
        analyze,
        reAnalyze,
        clearPredictions,
      }}
    >
      {children}
    </PredictionContext.Provider>
  );
};

export const usePrediction = (): PredictionContextType => {
  const context = useContext(PredictionContext);
  if (!context) {
    throw new Error('usePrediction must be used within PredictionProvider');
  }
  return context;
};

