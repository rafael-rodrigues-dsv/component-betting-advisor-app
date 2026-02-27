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
  replaceTicketBet: (index: number, newBet: TicketBet) => void;
  clearTicketBets: () => void;
  createTicket: (stake: number, bookmakerId: string) => Promise<Ticket | null>;
  loadTickets: () => Promise<void>;
  refreshTickets: () => Promise<void>;
  updateTicketsResults: () => Promise<void>;
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

  const replaceTicketBet = useCallback((index: number, newBet: TicketBet) => {
    setTicketBets(prev => prev.map((bet, i) => i === index ? newBet : bet));
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
        showNotification('🎉 Bilhete criado com sucesso! Clique em "Atualizar" para verificar resultados.', 'success');

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

  const refreshTickets = useCallback(async () => {
    setLoading(true);
    try {
      // Apenas busca a lista de tickets (GET)
      console.log('🔄 Buscando bilhetes...');
      const response = await ticketsApi.getTickets();
      const tickets = response.tickets || [];
      const pendingCount = tickets.filter(t => t.status === 'PENDENTE').length;

      console.log(`✅ Bilhetes carregados: ${tickets.length} total, ${pendingCount} pendentes`);

      setTickets(tickets);
    } catch (error) {
      console.error('Erro ao carregar bilhetes:', error);
      showNotification('❌ Erro ao carregar bilhetes', 'error');
    } finally {
      setLoading(false);
    }
  }, []);

  const updateTicketsResults = useCallback(async () => {
    try {
      // Atualiza resultados dos bilhetes pendentes (backend processa)
      console.log('⚙️ Processando resultados dos bilhetes pendentes...');
      console.log('📡 Chamando: POST /api/v1/tickets/update-results');

      const updateResponse = await ticketsApi.updateResults();

      console.log('📥 Resposta recebida:', updateResponse);

      if (updateResponse.success) {
        if (updateResponse.stats.updated > 0) {
          console.log(`✅ ${updateResponse.stats.updated} bilhetes atualizados!`);
          showNotification(
            `✅ ${updateResponse.stats.updated} bilhetes atualizados (${updateResponse.stats.won} ganhos, ${updateResponse.stats.lost} perdidos)`,
            'success'
          );
        } else {
          console.log('ℹ️ Nenhum bilhete atualizado (ainda pendentes)');
        }

        // Sempre busca a lista atualizada
        await refreshTickets();
      }
    } catch (error) {
      console.error('Erro ao atualizar resultados:', error);
      // Não mostra notificação de erro para não poluir (polling automático)
    }
  }, [refreshTickets]);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    try {
      // Mantido para compatibilidade inicial - atualiza E busca
      console.log('🔄 Atualizando resultados dos bilhetes pendentes...');
      try {
        const updateResponse = await ticketsApi.updateResults();
        if (updateResponse.success && updateResponse.stats.updated > 0) {
          showNotification(
            `✅ ${updateResponse.stats.updated} bilhetes atualizados (${updateResponse.stats.won} ganhos, ${updateResponse.stats.lost} perdidos)`,
            'success'
          );
        }
      } catch (error) {
        console.warn('⚠️ Erro ao atualizar resultados, continuando...', error);
      }

      // 2. Busca lista atualizada de tickets
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
        replaceTicketBet,
        clearTicketBets,
        createTicket,
        loadTickets,
        refreshTickets,
        updateTicketsResults,
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

