/**
 * TicketContext - Gerencia bilhetes e apostas
 */
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import type { Ticket, TicketBet, Prediction, MarketPrediction } from '../types';
import { ticketsApi } from '../services/api';
import { showNotification } from '../services/notificationService';

interface TicketContextType {
  tickets: Ticket[];
  ticketBets: TicketBet[];
  stake: number;
  loading: boolean;
  setStake: (stake: number) => void;
  addToTicket: (prediction: Prediction, market: MarketPrediction) => void;
  removeFromTicket: (indexOrMatchId: number | string) => void;
  clearTicketBets: () => void;
  createTicket: (stake: number, bookmakerId: string) => Promise<Ticket | null>;
  loadTickets: () => Promise<void>;
  deleteTicket: (ticketId: string) => Promise<void>;
}

const TicketContext = createContext<TicketContextType | undefined>(undefined);

export const TicketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [ticketBets, setTicketBets] = useState<TicketBet[]>([]);
  const [stake, setStake] = useState<number>(10);
  const [loading, setLoading] = useState(false);

  const addToTicket = useCallback((prediction: Prediction, market: MarketPrediction) => {
    setTicketBets(prev => {
      // Remove aposta anterior do mesmo jogo (se existir)
      const filtered = prev.filter(bet => bet.match_id !== prediction.match_id);

      // Adiciona nova aposta
      return [...filtered, {
        match_id: prediction.match_id,
        home_team: prediction.home_team,
        away_team: prediction.away_team,
        league: prediction.league,
        date: prediction.date,
        market: market.market,
        predicted_outcome: market.predicted_outcome,
        odds: market.odds,
        confidence: market.confidence,
        bookmaker_id: prediction.bookmaker_id,
      }];
    });

    showNotification('✅ Aposta adicionada ao bilhete!', 'success');
  }, []);

  const removeFromTicket = useCallback((indexOrMatchId: number | string) => {
    setTicketBets(prev => {
      if (typeof indexOrMatchId === 'number') {
        // Remove por índice
        return prev.filter((_, i) => i !== indexOrMatchId);
      } else {
        // Remove por match_id
        return prev.filter(bet => bet.match_id !== indexOrMatchId);
      }
    });
    showNotification('🗑️ Aposta removida', 'info');
  }, []);

  const clearTicketBets = useCallback(() => {
    setTicketBets([]);
  }, []);

  const createTicket = useCallback(async (stakeAmount: number, bookmakerId: string): Promise<Ticket | null> => {
    if (ticketBets.length === 0) {
      showNotification('⚠️ Adicione apostas ao bilhete primeiro', 'warning');
      return null;
    }

    setLoading(true);
    try {
      const response = await ticketsApi.createTicket({
        name: `Bilhete ${new Date().toLocaleString('pt-BR')}`,
        bets: ticketBets,
        stake: stakeAmount,
        bookmaker_id: bookmakerId,
      });

      if (response.success && response.ticket) {
        setTickets(prev => [response.ticket!, ...prev]);
        clearTicketBets();
        showNotification('🎉 Bilhete criado com sucesso!', 'success');

        // Simula webhook de resultado após 5s
        setTimeout(async () => {
          await ticketsApi.simulateResult(response.ticket!.id);
          await loadTickets(); // Recarrega para pegar resultado
        }, 5000);

        return response.ticket!;
      }
      return null;
    } catch (error) {
      console.error('Erro ao criar bilhete:', error);
      showNotification('❌ Erro ao criar bilhete', 'error');
      return null;
    } finally {
      setLoading(false);
    }
  }, [ticketBets]);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    try {
      const response = await ticketsApi.getTickets();
      setTickets(response.tickets || []);
    } catch (error) {
      console.error('Erro ao carregar bilhetes:', error);
      showNotification('❌ Erro ao carregar bilhetes', 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteTicket = useCallback(async (ticketId: string) => {
    setLoading(true);
    try {
      await ticketsApi.deleteTicket(ticketId);
      setTickets(prev => prev.filter(t => t.id !== ticketId));
      showNotification('🗑️ Bilhete excluído', 'success');
    } catch (error) {
      console.error('Erro ao deletar bilhete:', error);
      showNotification('❌ Erro ao excluir bilhete', 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <TicketContext.Provider
      value={{
        tickets,
        ticketBets,
        stake,
        loading,
        setStake,
        addToTicket,
        removeFromTicket,
        clearTicketBets,
        createTicket,
        loadTickets,
        deleteTicket,
      }}
    >
      {children}
    </TicketContext.Provider>
  );
};

export const useTicket = (): TicketContextType => {
  const context = useContext(TicketContext);
  if (!context) {
    throw new Error('useTicket must be used within TicketProvider');
  }
  return context;
};

