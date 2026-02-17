/**
 * Dashboard Page - Página inicial com estatísticas
 */
import React, { useEffect, useState } from 'react';
import { StatsCard, QuickGuide } from '../components/dashboard';
import type { DashboardStats } from '../types';
import { useMatches } from '../hooks/useMatches';
import { usePrediction } from '../contexts/PredictionContext';
import { useTicket } from '../contexts/TicketContext';
import { ticketsApi } from '../services/api';

export const DashboardPage: React.FC = () => {
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const { matches } = useMatches('all');
  const { predictions } = usePrediction();
  const { tickets, refreshTickets } = useTicket();

  useEffect(() => {
    loadDashboardStats();
    refreshTickets();
  }, [refreshTickets]);

  const loadDashboardStats = async () => {
    try {
      const response = await ticketsApi.getDashboardStats();
      setDashboardStats(response.stats);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  return (
    <div className="dashboard-page">
      <h2 className="dashboard-title">📊 Dashboard</h2>

      {/* Seção: Visão Geral */}
      <div className="dashboard-section">
        <h3 className="section-title">📌 Visão Geral</h3>
        <div className="stats-grid stats-grid-3">
          <StatsCard
            icon="⚽"
            value={matches.length}
            label="Jogos Disponíveis"
          />

          <StatsCard
            icon="🎯"
            value={predictions.length}
            label="Previsões Geradas"
            color="var(--success)"
          />

          <StatsCard
            icon="🎫"
            value={tickets.length}
            label="Bilhetes Criados"
            color="var(--warning)"
          />
        </div>
      </div>

      {/* Seção: Estatísticas de Apostas */}
      {dashboardStats && (
        <div className="dashboard-section">
          <h3 className="section-title">📈 Estatísticas de Apostas</h3>
          <div className="stats-grid stats-grid-3">
            <StatsCard
              icon="✅"
              value={dashboardStats.won_tickets}
              label="Apostas Ganhas"
              color="var(--success)"
            />

            <StatsCard
              icon="❌"
              value={dashboardStats.lost_tickets}
              label="Apostas Perdidas"
              color="var(--danger)"
            />

            <StatsCard
              icon="⏳"
              value={dashboardStats.pending_tickets}
              label="Apostas Pendentes"
              color="var(--warning)"
            />
          </div>

          <div className="stats-grid stats-grid-3" style={{ marginTop: 16 }}>
            <StatsCard
              icon="📊"
              value={`${dashboardStats.success_rate}%`}
              label="Taxa de Sucesso"
              color={dashboardStats.success_rate >= 50 ? 'var(--success)' : 'var(--danger)'}
            />

            <StatsCard
              icon="💰"
              value={`R$ ${dashboardStats.total_staked.toFixed(2)}`}
              label="Total Apostado"
              color="var(--accent-primary)"
            />

            <StatsCard
              icon={dashboardStats.total_profit >= 0 ? "💸" : "📉"}
              value={`R$ ${dashboardStats.total_profit.toFixed(2)}`}
              label="Lucro/Prejuízo"
              color={dashboardStats.total_profit >= 0 ? 'var(--success)' : 'var(--danger)'}
            />
          </div>
        </div>
      )}

      {/* Guia Rápido */}
      <QuickGuide />
    </div>
  );
};

