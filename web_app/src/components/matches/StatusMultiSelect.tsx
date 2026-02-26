/**
 * StatusMultiSelect - Combo multi-select para status de partidas
 *
 * Mesma dinâmica do LeagueMultiSelect:
 * - Input com busca
 * - Chips para status selecionados
 * - Dropdown com checkbox
 * - Nenhum selecionado = mostra todos
 */
import React, { useState, useRef, useEffect, useMemo } from 'react';

interface StatusOption {
  code: string;
  label: string;
  icon: string;
  group: string;
}

const STATUS_OPTIONS: StatusOption[] = [
  // Não começou
  { code: 'TBD', label: 'A definir', icon: '❓', group: 'Agendado' },
  { code: 'NS',  label: 'Não iniciado', icon: '⏰', group: 'Agendado' },
  // Em andamento
  { code: '1H',  label: '1º Tempo', icon: '⚽', group: 'Em andamento' },
  { code: 'HT',  label: 'Intervalo', icon: '⏸️', group: 'Em andamento' },
  { code: '2H',  label: '2º Tempo', icon: '⚽', group: 'Em andamento' },
  { code: 'ET',  label: 'Prorrogação', icon: '⏱️', group: 'Em andamento' },
  { code: 'P',   label: 'Pênaltis', icon: '🥅', group: 'Em andamento' },
  { code: 'LIVE', label: 'Ao vivo', icon: '🔴', group: 'Em andamento' },
  { code: 'BT',  label: 'Intervalo Prorr.', icon: '⏸️', group: 'Em andamento' },
  // Interrompido
  { code: 'SUSP', label: 'Suspenso', icon: '🚫', group: 'Interrompido' },
  { code: 'INT',  label: 'Interrompido', icon: '⛔', group: 'Interrompido' },
];

interface StatusMultiSelectProps {
  selectedStatuses: Set<string>;
  onChange: (statuses: Set<string>) => void;
  /** Status disponíveis nos matches carregados (para mostrar contadores) */
  availableStatuses?: Map<string, number>;
}

export const StatusMultiSelect: React.FC<StatusMultiSelectProps> = ({
  selectedStatuses,
  onChange,
  availableStatuses,
}) => {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
        setSearch('');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filtra apenas status que existem nos matches carregados
  const relevantOptions = useMemo(() => {
    if (!availableStatuses || availableStatuses.size === 0) return STATUS_OPTIONS;
    return STATUS_OPTIONS.filter(s => availableStatuses.has(s.code));
  }, [availableStatuses]);

  const filteredOptions = useMemo(() => {
    if (!search.trim()) return relevantOptions;
    const term = search.toLowerCase();
    return relevantOptions.filter(s =>
      s.label.toLowerCase().includes(term) ||
      s.code.toLowerCase().includes(term) ||
      s.group.toLowerCase().includes(term)
    );
  }, [relevantOptions, search]);

  const selectedObjects = useMemo(() => {
    return STATUS_OPTIONS.filter(s => selectedStatuses.has(s.code));
  }, [selectedStatuses]);

  const toggleStatus = (code: string) => {
    const newSet = new Set(selectedStatuses);
    if (newSet.has(code)) {
      newSet.delete(code);
    } else {
      newSet.add(code);
    }
    onChange(newSet);
  };

  const clearAll = () => {
    onChange(new Set());
    setSearch('');
  };

  const selectAll = () => {
    onChange(new Set(relevantOptions.map(s => s.code)));
  };

  // Atalhos rápidos
  const selectGroup = (group: string) => {
    const groupCodes = relevantOptions.filter(s => s.group === group).map(s => s.code);
    const newSet = new Set(selectedStatuses);
    groupCodes.forEach(c => newSet.add(c));
    onChange(newSet);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      setSearch('');
      inputRef.current?.blur();
    }
  };

  // Agrupa por grupo para exibir no dropdown
  const groupedOptions = useMemo(() => {
    const groups: Record<string, StatusOption[]> = {};
    filteredOptions.forEach(opt => {
      if (!groups[opt.group]) groups[opt.group] = [];
      groups[opt.group].push(opt);
    });
    return Object.entries(groups);
  }, [filteredOptions]);

  return (
    <div className="status-multiselect" ref={containerRef}>
      <div
        className={`league-multiselect-input-area ${isOpen ? 'focused' : ''}`}
        onClick={() => { inputRef.current?.focus(); setIsOpen(true); }}
      >
        {selectedObjects.length > 0 ? (
          <div className="league-chips">
            {selectedObjects.map(status => (
              <span key={status.code} className="league-chip">
                <span>{status.icon}</span>
                <span className="league-chip-name">{status.label}</span>
                <button
                  className="league-chip-remove"
                  onClick={(e) => { e.stopPropagation(); toggleStatus(status.code); }}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        ) : null}
        <input
          ref={inputRef}
          type="text"
          className="league-multiselect-input"
          placeholder={selectedObjects.length === 0 ? 'Todos os status — digite para filtrar...' : 'Filtrar...'}
          value={search}
          onChange={(e) => { setSearch(e.target.value); if (!isOpen) setIsOpen(true); }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
        />
        <span className="league-multiselect-arrow">{isOpen ? '▲' : '▼'}</span>
      </div>

      {isOpen && (
        <div className="league-multiselect-dropdown">
          <div className="league-dropdown-actions">
            <button
              className="league-dropdown-action-btn"
              onClick={selectedStatuses.size === relevantOptions.length ? clearAll : selectAll}
            >
              {selectedStatuses.size === relevantOptions.length ? '☐ Limpar todos' : '☑️ Selecionar todos'}
            </button>
            {selectedStatuses.size > 0 && selectedStatuses.size < relevantOptions.length && (
              <button className="league-dropdown-action-btn" onClick={clearAll}>
                🗑️ Limpar ({selectedStatuses.size})
              </button>
            )}
            {/* Atalhos por grupo */}
            {relevantOptions.some(s => s.group === 'Agendado') && (
              <button className="league-dropdown-action-btn" onClick={() => selectGroup('Agendado')}>
                ⏰ Agendados
              </button>
            )}
            {relevantOptions.some(s => s.group === 'Em andamento') && (
              <button className="league-dropdown-action-btn" onClick={() => selectGroup('Em andamento')}>
                ⚽ Ao vivo
              </button>
            )}
          </div>

          <div className="league-dropdown-list">
            {groupedOptions.length === 0 ? (
              <div className="league-dropdown-empty">Nenhum status encontrado</div>
            ) : (
              groupedOptions.map(([group, options]) => (
                <div key={group}>
                  <div className="status-group-header">{group}</div>
                  {options.map(status => {
                    const isSelected = selectedStatuses.has(status.code);
                    const count = availableStatuses?.get(status.code) || 0;
                    return (
                      <div
                        key={status.code}
                        className={`league-dropdown-item ${isSelected ? 'selected' : ''}`}
                        onClick={() => toggleStatus(status.code)}
                      >
                        <span className="league-dropdown-check">
                          {isSelected ? '☑️' : '☐'}
                        </span>
                        <span>{status.icon}</span>
                        <span className="league-dropdown-name">{status.label}</span>
                        <span className="league-dropdown-country">{status.code}</span>
                        {count > 0 && (
                          <span className="status-count-badge">{count}</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

