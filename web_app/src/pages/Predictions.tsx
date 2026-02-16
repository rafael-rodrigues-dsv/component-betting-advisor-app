/**
 * Predictions Page - Página de previsões
 */
import React, { useEffect } from 'react';
import type { Prediction, MarketPrediction } from '../types';
import { PredictionPanel } from '../components/predictions/PredictionPanel';
import { TicketBuilder } from '../components/tickets/TicketBuilder';
import { usePrediction } from '../contexts/PredictionContext';
import { useTicket } from '../contexts/TicketContext';
import { useBookmaker } from '../contexts/BookmakerContext';
import { useApp } from '../contexts/AppContext';
import { showSuccess } from '../services/notificationService';

export const PredictionsPage: React.FC = () => {
  const { setActiveTab } = useApp();
  const { getBookmakerName, selectedBookmaker } = useBookmaker();
  const { predictions, preTicket } = usePrediction();
  const {
    ticketBets,
    stake,
    setStake,
    addToTicket,
    removeFromTicket,
    clearTicketBets,
    createTicket,
  } = useTicket();

  // Pré-preencher bilhete quando análise retornar pré-bilhete
  useEffect(() => {
    if (preTicket && preTicket.bets.length > 0 && ticketBets.length === 0) {
      clearTicketBets();

      preTicket.bets.forEach((bet: any) => {
        const prediction = predictions.find(p => p.match_id === bet.match_id);
        if (prediction) {
          // Adiciona bookmaker_id à prediction
          prediction.bookmaker_id = selectedBookmaker;

          addToTicket(prediction, {
            market: bet.market,
            predicted_outcome: bet.predicted_outcome,
            odds: bet.odds,
            confidence: bet.confidence,
            expected_value: 0,
            recommendation: 'RECOMMENDED'
          });
        }
      });
    }
  }, [preTicket]);

  const handleAddToTicket = (prediction: Prediction, market: MarketPrediction) => {
    addToTicket(prediction, market);
  };

  const handleCreateTicket = async () => {
    const bookmaker = ticketBets[0]?.bookmaker_id || 'bet365';
    const ticket = await createTicket(stake, bookmaker);
    if (ticket) {
      showSuccess('✅ Bilhete criado! Redirecionando...');
      setTimeout(() => {
        setActiveTab('tickets');
      }, 1000);
    }
  };

  const bookmakerName = ticketBets.length > 0 && ticketBets[0].bookmaker_id
    ? getBookmakerName(ticketBets[0].bookmaker_id)
    : undefined;

  return (
    <>
      {preTicket && ticketBets.length > 0 && (
        <div className="pre-ticket-alert">
          <div className="alert-icon">✨</div>
          <div className="alert-content">
            <strong>Pré-bilhete montado!</strong>
            <p>{preTicket.message}</p>
            <p className="alert-detail">
              {preTicket.total_bets} aposta{preTicket.total_bets > 1 ? 's' : ''} •
              Odd combinada: {preTicket.combined_odds.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      <PredictionPanel
        predictions={predictions}
        onAddToTicket={handleAddToTicket}
      />

      <TicketBuilder
        ticketBets={ticketBets}
        stake={stake}
        onStakeChange={setStake}
        onRemoveBet={removeFromTicket}
        onClear={clearTicketBets}
        onCreate={handleCreateTicket}
        bookmakerName={bookmakerName}
      />
    </>
  );
};

