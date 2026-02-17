/**
 * Tickets Page - Página de bilhetes
 */
import React, { useEffect, useRef, useState } from 'react';
import { TicketBuilder } from '../components/tickets/TicketBuilder';
import { TicketHistory } from '../components/tickets/TicketHistory';
import { useTicket } from '../contexts/TicketContext';
import { useBookmaker } from '../contexts/BookmakerContext';
import { showSuccess } from '../services/notificationService';

const POLLING_INTERVAL = 5000; // 5 segundos

export const TicketsPage: React.FC = () => {
  const { getBookmakerName } = useBookmaker();
  const {
    tickets,
    ticketBets,
    stake,
    setStake,
    removeFromTicket,
    clearTicketBets,
    createTicket,
    refreshTickets,
    updateTicketsResults,
    deleteTicket,
  } = useTicket();

  const pollingIntervalRef = useRef<number | null>(null);
  const updateTicketsResultsRef = useRef(updateTicketsResults);
  const refreshTicketsRef = useRef(refreshTickets);
  const isPollingActiveRef = useRef(false);
  const [nextUpdate, setNextUpdate] = useState<number>(0);
  const [isPollingActive, setIsPollingActive] = useState(false);

  // Atualiza a ref sempre que a função mudar
  useEffect(() => {
    updateTicketsResultsRef.current = updateTicketsResults;
    refreshTicketsRef.current = refreshTickets;
  }, [updateTicketsResults, refreshTickets]);

  // Carrega bilhetes inicialmente
  useEffect(() => {
    console.log('🔄 Carregando bilhetes inicialmente...');
    refreshTickets().then(() => {
      // Após carregar, verifica se precisa iniciar polling
      const pending = tickets.some(t => t.status === 'PENDENTE');
      if (pending && !isPollingActiveRef.current) {
        console.log('🔄 Detectados bilhetes pendentes no carregamento inicial');
        startPolling();
      }
    });
  }, [refreshTickets]);

  // Função para iniciar o polling
  const startPolling = () => {
    if (isPollingActiveRef.current) {
      console.log('⚠️ Polling já está ativo');
      return;
    }

    console.log('🔄 Iniciando polling automático...');
    isPollingActiveRef.current = true;
    setIsPollingActive(true);
    setNextUpdate(5);

    // Primeira execução após 5 segundos
    setTimeout(async () => {
      try {
        console.log('⏰ Primeira verificação após 5s...');
        await updateTicketsResultsRef.current();

        // Verifica se ainda há pendentes
        await refreshTicketsRef.current();

        console.log('✅ Primeira verificação concluída!');
        setNextUpdate(5);

        // Configura interval para execuções subsequentes
        pollingIntervalRef.current = setInterval(async () => {
          try {
            console.log('⏰ Polling: verificando resultados...');
            await updateTicketsResultsRef.current();
            await refreshTicketsRef.current();

            console.log('✅ Polling verificação concluída!');
            setNextUpdate(5);
          } catch (error) {
            console.error('❌ Erro no interval:', error);
          }
        }, POLLING_INTERVAL) as unknown as number;

        console.log('✅ Interval configurado');
      } catch (error) {
        console.error('❌ Erro no timeout:', error);
      }
    }, POLLING_INTERVAL);

    console.log('⏱️ Timeout configurado');
  };

  // Countdown para próxima atualização (apenas quando polling ativo)
  useEffect(() => {
    if (!isPollingActive) return;

    const countdownInterval = setInterval(() => {
      setNextUpdate(prev => {
        if (prev > 0) return prev - 1;
        return 5;
      });
    }, 1000);

    return () => clearInterval(countdownInterval);
  }, [isPollingActive]);

  // Cleanup ao desmontar
  useEffect(() => {
    return () => {
      if (pollingIntervalRef.current) {
        console.log('🛑 Componente desmontado - parando polling');
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, []);

  const handleCreateTicket = async () => {
    const bookmaker = ticketBets[0]?.bookmaker_id || 'bet365';
    const ticket = await createTicket(stake, bookmaker);
    if (ticket) {
      showSuccess('✅ Bilhete criado! Verificação automática iniciará em 5 segundos.');
      // Inicia polling manualmente
      startPolling();
    }
  };

  const handleDelete = async (ticketId: string) => {
    if (window.confirm('Deseja realmente excluir este bilhete?')) {
      await deleteTicket(ticketId);
    }
  };

  const handleRefresh = () => {
    // Apenas recarrega os dados (GET)
    refreshTickets();
  };

  const bookmakerName = ticketBets.length > 0 && ticketBets[0].bookmaker_id
    ? getBookmakerName(ticketBets[0].bookmaker_id)
    : undefined;

  return (
    <div className="tickets-tab-content">
      <TicketBuilder
        ticketBets={ticketBets}
        stake={stake}
        onStakeChange={setStake}
        onRemoveBet={removeFromTicket}
        onClear={clearTicketBets}
        onCreate={handleCreateTicket}
        bookmakerName={bookmakerName}
      />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, gap: 16, flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
          <h3 style={{ color: '#fff', margin: 0 }}>📋 Histórico de Bilhetes</h3>
          {isPollingActive && (
            <span style={{
              fontSize: 11,
              color: '#10b981',
              padding: '4px 10px',
              background: 'rgba(16, 185, 129, 0.1)',
              borderRadius: 12,
              border: '1px solid rgba(16, 185, 129, 0.3)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: 6
            }}>
              <span style={{ fontSize: 8, animation: 'pulse 1.5s ease-in-out infinite' }}>⬤</span>
              Próxima verificação: {nextUpdate}s
            </span>
          )}
        </div>
        <button className="btn btn-secondary" onClick={handleRefresh}>🔄 Atualizar</button>
      </div>

      <TicketHistory
        tickets={tickets}
        onDelete={handleDelete}
      />
    </div>
  );
};

