/**
 * LeagueCarousel Component
 *
 * Carrossel horizontal de ligas com:
 * - 🔴 Seção "Ao Vivo" (ligas com jogos em andamento)
 * - 🌍 Toggle: Todas / Ligas / Copas
 * - 🔍 Busca por nome/país
 * - Seleção múltipla com chips de selecionadas
 */
import React, { useRef, useState, useEffect, useCallback, useMemo } from 'react';
import type { League, Match } from '../../types';

const LIVE_STATUSES = new Set(['1H', '2H', 'HT', 'ET', 'BT', 'P', 'LIVE', 'INT', 'SUSP']);

interface LeagueCarouselProps {
  leagues: League[];
  matches: Match[];
  selectedLeagueIds: Set<string>;
  onToggleLeague: (leagueId: string) => void;
  onSelectMultiple: (leagueIds: string[]) => void;
  onClearAll: () => void;
}

export const LeagueCarousel: React.FC<LeagueCarouselProps> = ({
  leagues,
  matches,
  selectedLeagueIds,
  onToggleLeague,
  onSelectMultiple,
  onClearAll,
}) => {
  const mainScrollRef = useRef<HTMLDivElement>(null);
  const liveScrollRef = useRef<HTMLDivElement>(null);

  // Scroll state — carrossel principal
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartRef = useRef({ x: 0, scrollLeft: 0 });

  // Scroll state — carrossel ao vivo
  const [liveCanScrollLeft, setLiveCanScrollLeft] = useState(false);
  const [liveCanScrollRight, setLiveCanScrollRight] = useState(false);

  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<'all' | 'league' | 'cup'>('all');

  // ── Dados derivados ──

  // Contagem de jogos por liga
  const matchCountByLeague = useMemo(() => {
    const counts = new Map<string, number>();
    matches.forEach(m => {
      const lid = m.league.id;
      counts.set(lid, (counts.get(lid) || 0) + 1);
    });
    return counts;
  }, [matches]);

  // Top N populares (por quantidade de jogos)
  const liveLeagues = useMemo(() => {
    // Agrupa jogos ao vivo por liga
    const liveByLeague = new Map<string, number>();
    matches.forEach(m => {
      if (LIVE_STATUSES.has(m.status_short || '')) {
        const lid = m.league.id;
        liveByLeague.set(lid, (liveByLeague.get(lid) || 0) + 1);
      }
    });
    // Retorna ligas que têm jogos ao vivo, ordenadas por qtd desc
    return leagues
      .filter(l => liveByLeague.has(l.id))
      .sort((a, b) => (liveByLeague.get(b.id) || 0) - (liveByLeague.get(a.id) || 0));
  }, [leagues, matches]);

  // Contagem de jogos ao vivo por liga (para exibir no card)
  const liveMatchCountByLeague = useMemo(() => {
    const counts = new Map<string, number>();
    matches.forEach(m => {
      if (LIVE_STATUSES.has(m.status_short || '')) {
        const lid = m.league.id;
        counts.set(lid, (counts.get(lid) || 0) + 1);
      }
    });
    return counts;
  }, [matches]);

  // Ligas filtradas para o carrossel principal (tipo + busca + com jogos)
  const filteredLeagues = useMemo(() => {
    let filtered = leagues;

    // Remove ligas sem jogos
    filtered = filtered.filter(l => (matchCountByLeague.get(l.id) || 0) > 0);

    // Busca por nome ou país
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(l =>
        l.name.toLowerCase().includes(term) ||
        l.country.toLowerCase().includes(term)
      );
    }

    // Tipo
    if (typeFilter !== 'all') {
      filtered = filtered.filter(l => l.type === typeFilter);
    }

    return [...filtered].sort((a, b) => a.name.localeCompare(b.name, 'pt-BR'));
  }, [leagues, searchTerm, typeFilter, matchCountByLeague]);

  // Contagem de ligas/copas no contexto filtrado (para badges no toggle)
  const typeCounts = useMemo(() => {
    let base = leagues.filter(l => (matchCountByLeague.get(l.id) || 0) > 0);
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      base = base.filter(l => l.name.toLowerCase().includes(term) || l.country.toLowerCase().includes(term));
    }
    let leagueCount = 0, cupCount = 0;
    base.forEach(l => { if (l.type === 'cup') cupCount++; else leagueCount++; });
    return { league: leagueCount, cup: cupCount, all: leagueCount + cupCount };
  }, [leagues, searchTerm, matchCountByLeague]);

  // ── Scroll helpers — main ──

  const checkScroll = useCallback(() => {
    const el = mainScrollRef.current;
    if (!el) return;
    setCanScrollLeft(el.scrollLeft > 2);
    setCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 2);
  }, []);

  const checkLiveScroll = useCallback(() => {
    const el = liveScrollRef.current;
    if (!el) return;
    setLiveCanScrollLeft(el.scrollLeft > 2);
    setLiveCanScrollRight(el.scrollLeft + el.clientWidth < el.scrollWidth - 2);
  }, []);

  useEffect(() => {
    checkScroll();
    const el = mainScrollRef.current;
    if (el) {
      el.addEventListener('scroll', checkScroll, { passive: true });
      window.addEventListener('resize', checkScroll);
    }
    return () => {
      el?.removeEventListener('scroll', checkScroll);
      window.removeEventListener('resize', checkScroll);
    };
  }, [checkScroll, filteredLeagues]);

  useEffect(() => {
    checkLiveScroll();
    const el = liveScrollRef.current;
    if (el) {
      el.addEventListener('scroll', checkLiveScroll, { passive: true });
      window.addEventListener('resize', checkLiveScroll);
    }
    return () => {
      el?.removeEventListener('scroll', checkLiveScroll);
      window.removeEventListener('resize', checkLiveScroll);
    };
  }, [checkLiveScroll, liveLeagues]);

  const scrollEl = (ref: React.RefObject<HTMLDivElement | null>, direction: 'left' | 'right') => {
    const el = ref.current;
    if (!el) return;
    const amount = el.clientWidth * 0.7;
    el.scrollBy({ left: direction === 'left' ? -amount : amount, behavior: 'smooth' });
  };

  const scroll = (direction: 'left' | 'right') => scrollEl(mainScrollRef, direction);
  const scrollLive = (direction: 'left' | 'right') => scrollEl(liveScrollRef, direction);

  // Drag to scroll
  const handleMouseDown = (e: React.MouseEvent) => {
    const el = mainScrollRef.current;
    if (!el) return;
    setIsDragging(true);
    dragStartRef.current = { x: e.clientX, scrollLeft: el.scrollLeft };
  };
  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    const el = mainScrollRef.current;
    if (!el) return;
    e.preventDefault();
    el.scrollLeft = dragStartRef.current.scrollLeft - (e.clientX - dragStartRef.current.x);
  };
  const handleMouseUp = () => setIsDragging(false);
  const handleMouseLeave = () => setIsDragging(false);

  // Reset scroll ao mudar filtros
  useEffect(() => {
    if (mainScrollRef.current) mainScrollRef.current.scrollLeft = 0;
  }, [typeFilter, searchTerm]);

  // ── Seleção ──

  const selectedTotalMatches = useMemo(() => {
    let total = 0;
    selectedLeagueIds.forEach(id => { total += matchCountByLeague.get(id) || 0; });
    return total;
  }, [selectedLeagueIds, matchCountByLeague]);

  const selectedLeagueObjects = useMemo(() => {
    return leagues.filter(l => selectedLeagueIds.has(l.id));
  }, [leagues, selectedLeagueIds]);

  // Selecionar todas as ligas visíveis no carrossel filtrado
  const selectAllVisible = () => {
    const newIds = filteredLeagues
      .filter(l => !selectedLeagueIds.has(l.id))
      .map(l => l.id);
    if (newIds.length > 0) {
      onSelectMultiple(newIds);
    }
  };

  // ── Render helpers ──

  const renderLeagueCard = (league: League) => {
    const count = matchCountByLeague.get(league.id) || 0;
    const isSelected = selectedLeagueIds.has(league.id);
    return (
      <button
        key={league.id}
        className={`league-carousel-item ${isSelected ? 'selected' : ''}`}
        onClick={() => onToggleLeague(league.id)}
        title={`${league.name} — ${league.country} (${count} jogos)`}
      >
        {league.logo && (
          <img src={league.logo} alt="" className="league-carousel-logo"
            onError={(e) => { e.currentTarget.style.display = 'none'; }} />
        )}
        <span className="league-carousel-name">{league.name}</span>
        <span className="league-carousel-meta">
          <span className="league-carousel-country">{league.country}</span>
          <span className="league-carousel-match-count">{count} {count === 1 ? 'jogo' : 'jogos'}</span>
        </span>
      </button>
    );
  };

  const renderLiveLeagueCard = (league: League) => {
    const totalCount = matchCountByLeague.get(league.id) || 0;
    const liveCount = liveMatchCountByLeague.get(league.id) || 0;
    const isSelected = selectedLeagueIds.has(league.id);
    return (
      <button
        key={league.id}
        className={`league-carousel-item league-carousel-item-live ${isSelected ? 'selected' : ''}`}
        onClick={() => onToggleLeague(league.id)}
        title={`${league.name} — ${liveCount} ao vivo de ${totalCount} jogos`}
      >
        {league.logo && (
          <img src={league.logo} alt="" className="league-carousel-logo"
            onError={(e) => { e.currentTarget.style.display = 'none'; }} />
        )}
        <span className="league-carousel-name">{league.name}</span>
        <span className="league-carousel-meta">
          <span className="league-carousel-country">{league.country}</span>
          <span className="league-carousel-live-badge">
            <span className="league-carousel-live-dot" />
            {liveCount} ao vivo
          </span>
          <span className="league-carousel-match-count">{totalCount} {totalCount === 1 ? 'jogo' : 'jogos'} total</span>
        </span>
      </button>
    );
  };

  return (
    <div className="league-carousel">

      {/* ═══ Header: título + busca + contagem ═══ */}
      <div className="league-carousel-header">
        <h3 className="league-carousel-title">🏆 Selecione Campeonatos</h3>
        <div className="league-carousel-search">
          <input
            type="text"
            placeholder="Buscar liga ou país..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="league-carousel-search-input"
          />
          {searchTerm && (
            <button className="league-carousel-search-clear" onClick={() => setSearchTerm('')}>×</button>
          )}
        </div>
        <span className="league-carousel-count">
          {selectedLeagueIds.size > 0
            ? `${selectedLeagueIds.size} selecionada${selectedLeagueIds.size > 1 ? 's' : ''} · ${leagues.length} disponíveis`
            : `${leagues.length} ligas disponíveis`
          }
        </span>
      </div>

      {/* ═══ Seção: 🔴 Ao Vivo ═══ */}
      {!searchTerm && liveLeagues.length > 0 && (
        <div className="league-carousel-section league-carousel-section-live">
          <div className="league-carousel-section-header">
            <span className="league-carousel-section-title">
              <span className="league-carousel-live-dot" /> Ao Vivo
            </span>
            <span className="league-carousel-section-hint">
              {liveLeagues.length} {liveLeagues.length === 1 ? 'liga com jogo' : 'ligas com jogos'} em andamento
            </span>
          </div>

          <div className="league-carousel-track-wrapper">
            {liveCanScrollLeft && (
              <button className="league-carousel-arrow league-carousel-arrow-left" onClick={() => scrollLive('left')}>◀</button>
            )}
            <div ref={liveScrollRef} className="league-carousel-track">
              {liveLeagues.map(renderLiveLeagueCard)}
            </div>
            {liveCanScrollRight && (
              <button className="league-carousel-arrow league-carousel-arrow-right" onClick={() => scrollLive('right')}>▶</button>
            )}
          </div>
        </div>
      )}

      {/* ═══ Filtros: Todas / Ligas / Copas ═══ */}
      <div className="league-carousel-filters">
        <div className="league-carousel-type-toggle">
          <button
            className={`league-carousel-type-btn ${typeFilter === 'all' ? 'active' : ''}`}
            onClick={() => setTypeFilter('all')}
          >
            🌍 Todas ({typeCounts.all})
          </button>
          <button
            className={`league-carousel-type-btn ${typeFilter === 'league' ? 'active' : ''}`}
            onClick={() => setTypeFilter(typeFilter === 'league' ? 'all' : 'league')}
          >
            ⚽ Ligas ({typeCounts.league})
          </button>
          <button
            className={`league-carousel-type-btn ${typeFilter === 'cup' ? 'active' : ''}`}
            onClick={() => setTypeFilter(typeFilter === 'cup' ? 'all' : 'cup')}
          >
            🏆 Copas ({typeCounts.cup})
          </button>
        </div>
      </div>

      {/* ═══ Carrossel principal filtrado ═══ */}
      <div className="league-carousel-section">
        <div className="league-carousel-section-header">
          <span className="league-carousel-section-title">
            {searchTerm
              ? `🔍 Resultados para "${searchTerm}"`
              : '📋 Todas as ligas'
            }
          </span>
          <span className="league-carousel-section-hint">{filteredLeagues.length} ligas</span>
          {filteredLeagues.length > 0 && filteredLeagues.length <= 50 && (
            <button className="league-carousel-select-all-btn" onClick={selectAllVisible}>
              ☑️ Selecionar todas visíveis
            </button>
          )}
        </div>

        <div className="league-carousel-track-wrapper">
          {canScrollLeft && (
            <button className="league-carousel-arrow league-carousel-arrow-left" onClick={() => scroll('left')}>◀</button>
          )}

          <div
            ref={mainScrollRef}
            className={`league-carousel-track ${isDragging ? 'dragging' : ''}`}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseLeave}
          >
            {filteredLeagues.length === 0 ? (
              <div className="league-carousel-empty">
                Nenhuma liga encontrada com os filtros atuais
              </div>
            ) : (
              filteredLeagues.map(renderLeagueCard)
            )}
          </div>

          {canScrollRight && (
            <button className="league-carousel-arrow league-carousel-arrow-right" onClick={() => scroll('right')}>▶</button>
          )}
        </div>
      </div>

      {/* ═══ Barra de selecionadas ═══ */}
      {selectedLeagueIds.size > 0 && (
        <div className="league-carousel-selected-info">
          <div className="league-carousel-selected-chips">
            {selectedLeagueObjects.map(league => (
              <span key={league.id} className="league-carousel-selected-chip">
                {league.logo && <img src={league.logo} alt="" className="league-carousel-chip-logo" onError={(e) => { e.currentTarget.style.display = 'none'; }} />}
                <span>{league.name}</span>
                <button className="league-carousel-chip-remove" onClick={() => onToggleLeague(league.id)} title={`Remover ${league.name}`}>×</button>
              </span>
            ))}
          </div>
          <span className="league-carousel-selected-total">
            {selectedTotalMatches} {selectedTotalMatches === 1 ? 'jogo' : 'jogos'} no total
          </span>
          <button className="league-carousel-clear-btn" onClick={onClearAll} title="Limpar seleção">
            ✕ Limpar todas
          </button>
        </div>
      )}
    </div>
  );
};
