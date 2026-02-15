import { useState, useEffect } from 'react';
import { matchApi, predictionApi, ticketApi, Match, Prediction, Ticket, TicketBet, MarketPrediction, League, Bookmaker } from './api';
import { getTeamLogo, getLeagueLogo, isValidLogoUrl } from './teamLogos';

type Tab = 'matches' | 'predictions' | 'tickets';
type Strategy = 'BALANCED' | 'CONSERVATIVE' | 'VALUE_BET' | 'AGGRESSIVE';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('matches');
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatches, setSelectedMatches] = useState<Set<string>>(new Set());
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [ticketBets, setTicketBets] = useState<TicketBet[]>([]);
  const [stake, setStake] = useState<number>(10);
  const [strategy, setStrategy] = useState<Strategy>('BALANCED');
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);

  // Filters
  const [leagues, setLeagues] = useState<League[]>([]);
  const [bookmakers, setBookmakers] = useState<Bookmaker[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<string>('all');
  const [selectedBookmaker, setSelectedBookmaker] = useState<string>('all');

  // Load matches on mount
  useEffect(() => {
    loadMatches();
    loadLeagues();
    loadBookmakers();
  }, []);

  // Reload matches when league filter changes
  useEffect(() => {
    loadMatches();
  }, [selectedLeague]);

  // Load tickets when tab changes
  useEffect(() => {
    if (activeTab === 'tickets') {
      loadTickets();
    }
  }, [activeTab]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const data = await matchApi.getMatches(undefined, selectedLeague !== 'all' ? selectedLeague : undefined);
      setMatches(data.matches);
    } catch (error) {
      console.error('Erro ao carregar jogos:', error);
    }
    setLoading(false);
  };

  const loadLeagues = async () => {
    try {
      const data = await matchApi.getLeagues();
      setLeagues(data.leagues);
    } catch (error) {
      console.error('Erro ao carregar ligas:', error);
    }
  };

  const loadBookmakers = async () => {
    try {
      const data = await matchApi.getBookmakers();
      setBookmakers(data.bookmakers);
    } catch (error) {
      console.error('Erro ao carregar casas de apostas:', error);
    }
  };

  const loadTickets = async () => {
    setLoading(true);
    try {
      const data = await ticketApi.getTickets();
      setTickets(data.tickets);
    } catch (error) {
      console.error('Erro ao carregar bilhetes:', error);
    }
    setLoading(false);
  };

  const toggleMatchSelection = (matchId: string) => {
    const newSelected = new Set(selectedMatches);
    if (newSelected.has(matchId)) {
      newSelected.delete(matchId);
    } else {
      newSelected.add(matchId);
    }
    setSelectedMatches(newSelected);
  };

  const analyzeMatches = async () => {
    if (selectedMatches.size === 0) return;

    setAnalyzing(true);
    try {
      const data = await predictionApi.analyze(Array.from(selectedMatches), strategy);
      setPredictions(data.predictions);
      setActiveTab('predictions');
    } catch (error) {
      console.error('Erro ao analisar:', error);
    }
    setAnalyzing(false);
  };

  const addToTicket = (prediction: Prediction, market: MarketPrediction) => {
    const bet: TicketBet = {
      match_id: prediction.match_id,
      home_team: prediction.home_team,
      away_team: prediction.away_team,
      market: market.market,
      predicted_outcome: market.predicted_outcome,
      odds: market.odds,
      confidence: market.confidence,
    };

    // Check if already added
    const exists = ticketBets.some(
      b => b.match_id === bet.match_id && b.market === bet.market
    );

    if (!exists) {
      setTicketBets([...ticketBets, bet]);
    }
  };

  const removeFromTicket = (index: number) => {
    setTicketBets(ticketBets.filter((_, i) => i !== index));
  };

  const createTicket = async () => {
    if (ticketBets.length === 0 || stake <= 0) return;

    try {
      await ticketApi.createTicket(null, stake, ticketBets);
      setTicketBets([]);
      setActiveTab('tickets');
      loadTickets();
    } catch (error) {
      console.error('Erro ao criar bilhete:', error);
    }
  };

  const simulateTicket = async (ticketId: string) => {
    try {
      await ticketApi.simulateResult(ticketId);
      loadTickets();
    } catch (error) {
      console.error('Erro ao simular:', error);
    }
  };

  const deleteTicket = async (ticketId: string) => {
    try {
      await ticketApi.deleteTicket(ticketId);
      loadTickets();
    } catch (error) {
      console.error('Erro ao deletar:', error);
    }
  };

  // Calcular odds combinadas e retorno potencial
  const combinedOdds = ticketBets.reduce((acc, bet) => acc * bet.odds, 1);
  const potentialReturn = stake * combinedOdds;

  const formatMarket = (market: string) => {
    const names: Record<string, string> = {
      '1X2': 'Resultado',
      'OVER_UNDER_25': 'Gols',
      'BTTS': 'Ambas Marcam',
    };
    return names[market] || market;
  };

  const formatOutcome = (market: string, outcome: string) => {
    if (market === '1X2') {
      const names: Record<string, string> = { HOME: 'Casa', DRAW: 'Empate', AWAY: 'Fora' };
      return names[outcome] || outcome;
    }
    if (market === 'OVER_UNDER_25') {
      return outcome === 'OVER' ? 'Mais de 2.5' : 'Menos de 2.5';
    }
    if (market === 'BTTS') {
      return outcome === 'YES' ? 'Sim' : 'Não';
    }
    return outcome;
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>⚽ Betting Advisor</h1>
        <div className="header-stats">
          <div className="stat-item">
            <div className="stat-value">{matches.length}</div>
            <div className="stat-label">Jogos Disponíveis</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{selectedMatches.size}</div>
            <div className="stat-label">Selecionados</div>
          </div>
          <div className="stat-item">
            <div className="stat-value">{ticketBets.length}</div>
            <div className="stat-label">No Bilhete</div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'matches' ? 'active' : ''}`}
          onClick={() => setActiveTab('matches')}
        >
          📅 Jogos
        </button>
        <button
          className={`tab ${activeTab === 'predictions' ? 'active' : ''}`}
          onClick={() => setActiveTab('predictions')}
        >
          🎯 Previsões {predictions.length > 0 && `(${predictions.length})`}
        </button>
        <button
          className={`tab ${activeTab === 'tickets' ? 'active' : ''}`}
          onClick={() => setActiveTab('tickets')}
        >
          🎫 Bilhetes
        </button>
      </div>

      {/* Matches Tab */}
      {activeTab === 'matches' && (
        <>
          <div className="filters-bar">
            <div className="filter-group">
              <label>🎯 Estratégia:</label>
              <select value={strategy} onChange={(e) => setStrategy(e.target.value as Strategy)}>
                <option value="BALANCED">⚖️ Balanceada</option>
                <option value="CONSERVATIVE">🛡️ Conservadora (Maior Confiança)</option>
                <option value="VALUE_BET">💰 Value Bet (Maior EV)</option>
                <option value="AGGRESSIVE">🔥 Agressiva (Odds Altas)</option>
              </select>
            </div>

            <div className="filter-group">
              <label>🏆 Campeonato:</label>
              <select value={selectedLeague} onChange={(e) => setSelectedLeague(e.target.value)}>
                <option value="all">Todos</option>
                {leagues.map(league => (
                  <option key={league.id} value={league.id}>
                    {league.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label>🎰 Casa de Apostas:</label>
              <select value={selectedBookmaker} onChange={(e) => setSelectedBookmaker(e.target.value)}>
                <option value="all">Todas</option>
                {bookmakers.map(bookmaker => (
                  <option key={bookmaker.id} value={bookmaker.id}>
                    {bookmaker.logo} {bookmaker.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="actions-bar">
            <div className="filters-info">
              {selectedLeague !== 'all' && (
                <span className="filter-badge">
                  🏆 {leagues.find(l => l.id === selectedLeague)?.name}
                </span>
              )}
              {selectedBookmaker !== 'all' && (
                <span className="filter-badge">
                  {bookmakers.find(b => b.id === selectedBookmaker)?.logo} {bookmakers.find(b => b.id === selectedBookmaker)?.name}
                </span>
              )}
              {(selectedLeague !== 'all' || selectedBookmaker !== 'all') && (
                <span className="selected-count">
                  <strong>{matches.length}</strong> jogos encontrados
                </span>
              )}
              {selectedMatches.size > 0 && (
                <span className="selected-count highlight">
                  <strong>{selectedMatches.size}</strong> selecionados
                </span>
              )}
            </div>
            <button
              className="btn btn-primary"
              disabled={selectedMatches.size === 0 || analyzing}
              onClick={analyzeMatches}
            >
              {analyzing ? '⏳ Analisando...' : '🔍 Analisar Selecionados'}
            </button>
          </div>

          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <span>Carregando jogos...</span>
            </div>
          ) : matches.length === 0 ? (
            <div className="empty-state">
              <h3>Nenhum jogo disponível</h3>
              <p>Não há jogos para esta data</p>
            </div>
          ) : (
            <div className="matches-grid">
              {matches.map((match) => (
                <div
                  key={match.id}
                  className={`match-card ${selectedMatches.has(match.id) ? 'selected' : ''}`}
                  onClick={() => toggleMatchSelection(match.id)}
                >
                  {selectedBookmaker !== 'all' && (
                    <div className="bookmaker-badge">
                      {bookmakers.find(b => b.id === selectedBookmaker)?.logo}
                      {' '}
                      {bookmakers.find(b => b.id === selectedBookmaker)?.name}
                    </div>
                  )}
                  <div className="match-league">
                    <span className="league-logo">{getLeagueLogo(match.league.name)}</span>
                    <span>{match.league.name}</span>
                    {match.round && (
                      <span className="match-round">• {match.round.name}</span>
                    )}
                  </div>
                  <div className="match-date-time">
                    <span className="match-date">
                      📅 {new Date(match.date).toLocaleDateString('pt-BR', {
                        weekday: 'short',
                        day: '2-digit',
                        month: 'short'
                      })}
                    </span>
                    <span className="match-time">
                      🕐 {new Date(match.date).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <div className="match-teams">
                    <div className="team">
                      {isValidLogoUrl(getTeamLogo(match.home_team.name)) ? (
                        <img src={getTeamLogo(match.home_team.name)} alt={match.home_team.name} className="team-logo-img" />
                      ) : (
                        <span className="team-logo">{getTeamLogo(match.home_team.name)}</span>
                      )}
                      <span className="team-name">{match.home_team.name}</span>
                    </div>
                    <span className="match-vs">vs</span>
                    <div className="team">
                      {isValidLogoUrl(getTeamLogo(match.away_team.name)) ? (
                        <img src={getTeamLogo(match.away_team.name)} alt={match.away_team.name} className="team-logo-img" />
                      ) : (
                        <span className="team-logo">{getTeamLogo(match.away_team.name)}</span>
                      )}
                      <span className="team-name">{match.away_team.name}</span>
                    </div>
                  </div>
                  {match.venue && (
                    <div className="match-venue">
                      🏟️ {match.venue.name}
                    </div>
                  )}
                  <div className="match-odds">
                    <div className="odd-item">
                      <div className="odd-label">Casa</div>
                      <div className="odd-value">{match.odds.home}</div>
                    </div>
                    <div className="odd-item">
                      <div className="odd-label">Empate</div>
                      <div className="odd-value">{match.odds.draw}</div>
                    </div>
                    <div className="odd-item">
                      <div className="odd-label">Fora</div>
                      <div className="odd-value">{match.odds.away}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Predictions Tab */}
      {activeTab === 'predictions' && (
        <>
          {predictions.length === 0 ? (
            <div className="empty-state">
              <h3>Nenhuma previsão ainda</h3>
              <p>Selecione jogos e clique em "Analisar" para ver as previsões</p>
            </div>
          ) : (
            <div className="predictions-list">
              {predictions.map((pred) => (
                <div key={pred.id} className="prediction-card">
                  <div className="prediction-header">
                    <div>
                      <div className="prediction-match">{pred.home_team} vs {pred.away_team}</div>
                      <div className="prediction-league">{pred.league}</div>
                    </div>
                  </div>
                  <div className="prediction-markets">
                    {pred.predictions.map((market, idx) => (
                      <div key={idx} className="market-item">
                        <div className="market-info">
                          <div className="market-name">{formatMarket(market.market)}</div>
                          <div className="market-prediction">{formatOutcome(market.market, market.predicted_outcome)}</div>
                        </div>
                        <div className="market-stats">
                          <div className="market-confidence">
                            <div className="confidence-bar">
                              <div
                                className="confidence-fill"
                                style={{ width: `${market.confidence * 100}%` }}
                              />
                            </div>
                            <span className="confidence-text">{(market.confidence * 100).toFixed(0)}%</span>
                          </div>
                          <div className="market-odds">{market.odds}</div>
                          <div className={`market-ev ${market.expected_value >= 0 ? 'ev-positive' : 'ev-negative'}`}>
                            {market.expected_value >= 0 ? '+' : ''}{(market.expected_value * 100).toFixed(1)}%
                          </div>
                          <span className={`recommendation-badge recommendation-${market.recommendation}`}>
                            {market.recommendation.replace('_', ' ')}
                          </span>
                        </div>
                        <button
                          className="add-to-ticket-btn"
                          onClick={() => addToTicket(pred, market)}
                        >
                          + Adicionar ao Bilhete
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Tickets Tab */}
      {activeTab === 'tickets' && (
        <>
          {/* Current Ticket Builder */}
          {ticketBets.length > 0 && (
            <div className="ticket-section">
              <div className="ticket-header">
                <span className="ticket-title">🎫 Novo Bilhete</span>
              </div>
              <div className="ticket-bets">
                {ticketBets.map((bet, idx) => (
                  <div key={idx} className="ticket-bet">
                    <div className="ticket-bet-info">
                      <div className="ticket-bet-match">{bet.home_team} vs {bet.away_team}</div>
                      <div className="ticket-bet-prediction">
                        {formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)}
                      </div>
                    </div>
                    <div className="ticket-bet-odds">{bet.odds}</div>
                    <button className="remove-bet-btn" onClick={() => removeFromTicket(idx)}>×</button>
                  </div>
                ))}
              </div>
              <div className="ticket-summary">
                <div className="summary-row">
                  <span>Apostas:</span>
                  <span>{ticketBets.length}</span>
                </div>
                <div className="summary-row">
                  <span>Odd Combinada:</span>
                  <span>{combinedOdds.toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>Retorno Potencial:</span>
                  <span>R$ {potentialReturn.toFixed(2)}</span>
                </div>
              </div>
              <div className="stake-input">
                <label>Valor (R$):</label>
                <input
                  type="number"
                  value={stake}
                  onChange={(e) => setStake(Number(e.target.value))}
                  min="1"
                />
              </div>
              <div className="ticket-actions">
                <button className="btn btn-secondary" onClick={() => setTicketBets([])}>
                  Limpar
                </button>
                <button className="btn btn-primary" onClick={createTicket}>
                  Criar Bilhete
                </button>
              </div>
            </div>
          )}

          {/* Tickets History */}
          <h3 style={{ marginBottom: 16 }}>📋 Histórico de Bilhetes</h3>
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <span>Carregando bilhetes...</span>
            </div>
          ) : tickets.length === 0 ? (
            <div className="empty-state">
              <h3>Nenhum bilhete criado</h3>
              <p>Adicione previsões ao bilhete e crie sua aposta</p>
            </div>
          ) : (
            <div className="tickets-history">
              {tickets.map((ticket) => (
                <div key={ticket.id} className="history-ticket">
                  <div className="history-header">
                    <span className="history-name">{ticket.name}</span>
                    <span className={`history-status status-${ticket.status}`}>{ticket.status}</span>
                  </div>
                  <div className="history-details">
                    <span>Stake: R$ {ticket.stake.toFixed(2)}</span>
                    <span>Odd: {ticket.combined_odds.toFixed(2)}</span>
                    <span>Retorno: R$ {ticket.potential_return.toFixed(2)}</span>
                    {ticket.profit !== undefined && (
                      <span style={{ color: ticket.profit >= 0 ? '#00ba7c' : '#f4212e' }}>
                        Lucro: R$ {ticket.profit.toFixed(2)}
                      </span>
                    )}
                  </div>
                  <div className="history-bets">
                    {ticket.bets.map((bet, idx) => (
                      <div key={idx} className="history-bet-item">
                        {bet.home_team} vs {bet.away_team} • {formatMarket(bet.market)}: {formatOutcome(bet.market, bet.predicted_outcome)} @ {bet.odds}
                      </div>
                    ))}
                  </div>
                  {ticket.status === 'PENDING' && (
                    <div className="ticket-actions" style={{ marginTop: 12 }}>
                      <button className="btn btn-secondary" onClick={() => simulateTicket(ticket.id)}>
                        🎲 Simular Resultado
                      </button>
                      <button className="btn btn-danger" onClick={() => deleteTicket(ticket.id)}>
                        🗑️ Excluir
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;

