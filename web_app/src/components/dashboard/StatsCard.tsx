/**
 * StatsCard - Card de estatística do Dashboard
 */
import React from 'react';

interface StatsCardProps {
  icon: string;
  value: number | string;
  label: string;
  color?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({ icon, value, label, color = 'var(--accent-primary)' }) => {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value" style={{ color }}>{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
};

