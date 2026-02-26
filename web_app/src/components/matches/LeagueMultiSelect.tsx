/**
 * LeagueMultiSelect - Combo multi-select com busca para ligas
 *
 * Features:
 * - Input com autocomplete para filtrar ligas
 * - Chips/tags para ligas selecionadas
 * - Dropdown com checkbox para cada liga
 * - "Todos" quando nenhuma selecionada
 * - Logo da liga (img da API) ao lado do nome
 */
import React, { useState, useRef, useEffect, useMemo } from 'react';
import type { League } from '../../types';

interface LeagueMultiSelectProps {
  leagues: League[];
  selectedLeagues: Set<string>;
  onChange: (leagues: Set<string>) => void;
}

export const LeagueMultiSelect: React.FC<LeagueMultiSelectProps> = ({
  leagues,
  selectedLeagues,
  onChange,
}) => {
  const [search, setSearch] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Fecha dropdown ao clicar fora
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

  // Filtra ligas pelo texto digitado
  const filteredLeagues = useMemo(() => {
    if (!search.trim()) return leagues;
    const term = search.toLowerCase();
    return leagues.filter(l =>
      l.name.toLowerCase().includes(term) ||
      l.country.toLowerCase().includes(term)
    );
  }, [leagues, search]);

  // Ligas selecionadas (objetos completos)
  const selectedLeagueObjects = useMemo(() => {
    return leagues.filter(l => selectedLeagues.has(l.id));
  }, [leagues, selectedLeagues]);

  const toggleLeague = (leagueId: string) => {
    const newSet = new Set(selectedLeagues);
    if (newSet.has(leagueId)) {
      newSet.delete(leagueId);
    } else {
      newSet.add(leagueId);
    }
    onChange(newSet);
  };

  const clearAll = () => {
    onChange(new Set());
    setSearch('');
  };

  const selectAll = () => {
    onChange(new Set(leagues.map(l => l.id)));
  };

  const handleInputFocus = () => {
    setIsOpen(true);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    if (!isOpen) setIsOpen(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
      setSearch('');
      inputRef.current?.blur();
    }
  };

  return (
    <div className="league-multiselect" ref={containerRef}>
      {/* Chips + Input */}
      <div
        className={`league-multiselect-input-area ${isOpen ? 'focused' : ''}`}
        onClick={() => { inputRef.current?.focus(); setIsOpen(true); }}
      >
        {selectedLeagueObjects.length > 0 ? (
          <div className="league-chips">
            {selectedLeagueObjects.map(league => (
              <span key={league.id} className="league-chip">
                {league.logo && (
                  <img
                    src={league.logo}
                    alt=""
                    className="league-chip-logo"
                    onError={(e) => { e.currentTarget.style.display = 'none'; }}
                  />
                )}
                <span className="league-chip-name">{league.name}</span>
                <button
                  className="league-chip-remove"
                  onClick={(e) => { e.stopPropagation(); toggleLeague(league.id); }}
                  title={`Remover ${league.name}`}
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
          placeholder={selectedLeagueObjects.length === 0 ? 'Todos os campeonatos — digite para filtrar...' : 'Filtrar...'}
          value={search}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onKeyDown={handleKeyDown}
        />
        <span className="league-multiselect-arrow">{isOpen ? '▲' : '▼'}</span>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="league-multiselect-dropdown">
          {/* Actions */}
          <div className="league-dropdown-actions">
            <button
              className="league-dropdown-action-btn"
              onClick={selectedLeagues.size === leagues.length ? clearAll : selectAll}
            >
              {selectedLeagues.size === leagues.length ? '☐ Limpar todos' : '☑️ Selecionar todos'}
            </button>
            {selectedLeagues.size > 0 && selectedLeagues.size < leagues.length && (
              <button className="league-dropdown-action-btn" onClick={clearAll}>
                🗑️ Limpar ({selectedLeagues.size})
              </button>
            )}
          </div>

          {/* Lista */}
          <div className="league-dropdown-list">
            {filteredLeagues.length === 0 ? (
              <div className="league-dropdown-empty">Nenhum campeonato encontrado</div>
            ) : (
              filteredLeagues.map(league => {
                const isSelected = selectedLeagues.has(league.id);
                return (
                  <div
                    key={league.id}
                    className={`league-dropdown-item ${isSelected ? 'selected' : ''}`}
                    onClick={() => toggleLeague(league.id)}
                  >
                    <span className="league-dropdown-check">
                      {isSelected ? '☑️' : '☐'}
                    </span>
                    {league.logo && (
                      <img
                        src={league.logo}
                        alt=""
                        className="league-dropdown-logo"
                        onError={(e) => { e.currentTarget.style.display = 'none'; }}
                      />
                    )}
                    <span className="league-dropdown-name">{league.name}</span>
                    <span className="league-dropdown-country">{league.country}</span>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}
    </div>
  );
};

