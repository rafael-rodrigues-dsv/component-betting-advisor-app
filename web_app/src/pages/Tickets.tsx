/**
 * Tickets Page - Página de bilhetes
 */
import React, { useEffect } from 'react';
import { TicketBuilder } from '../components/tickets/TicketBuilder';
import { TicketHistory } from '../components/tickets/TicketHistory';
import { useTicket } from '../contexts/TicketContext';
import { useBookmaker } from '../contexts/BookmakerContext';
import { showSuccess } from '../services/notificationService';

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
    loadTickets,
    deleteTicket,
  } = useTicket();

  // Carregar bilhetes quando a página é montada
  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const handleCreateTicket = async () => {
    const bookmaker = ticketBets[0]?.bookmaker_id || 'bet365';
    const ticket = await createTicket(stake, bookmaker);
    if (ticket) {
      showSuccess('✅ Bilhete criado com sucesso!');
    }
  };

  const handleDelete = async (ticketId: string) => {
    if (window.confirm('Deseja realmente excluir este bilhete?')) {
      await deleteTicket(ticketId);
    }
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

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h3 style={{ color: '#fff', margin: 0 }}>📋 Histórico de Bilhetes</h3>
        <button className="btn btn-secondary" onClick={loadTickets}>🔄 Atualizar</button>
      </div>

      <TicketHistory
        tickets={tickets}
        onDelete={handleDelete}
      />
    </div>
  );
};

