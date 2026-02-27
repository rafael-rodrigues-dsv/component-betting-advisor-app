# 🎰 Betting Advisor - Arquitetura do Sistema

> Sistema de sugestão de bilhetes de apostas esportivas — API-Football integrada

**Data:** 2026-02-27  
**Versão:** 5.0.0  
**Status:** ✅ Produção (API-Football Real, sem mocks)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológica](#stack-tecnológica)
3. [Arquitetura](#arquitetura)
4. [Estrutura de Pastas](#estrutura-de-pastas)
5. [Backend — Camadas](#backend--camadas)
6. [Frontend — Componentes](#frontend--componentes)
7. [API-Football Integration](#api-football-integration)
8. [Sistema de Cache](#sistema-de-cache)
9. [Timezone](#timezone)
10. [Endpoints da API](#endpoints-da-api)
11. [Configurações](#configurações)

---

## 🎯 Visão Geral

### Status da Implementação

| Funcionalidade | Status | Descrição |
|----------------|--------|-----------|
| Frontend React | ✅ | Interface completa (React + TypeScript + Vite) |
| Backend FastAPI | ✅ | Controllers com API-Football real |
| API-Football | ✅ | Fixtures + Odds reais |
| Cache SQLite | ✅ | Cache persistente com TTL + incremental |
| Preload sob demanda | ✅ | Hoje, 3 ou 7 dias (apenas fixtures) |
| Odds sob demanda por liga | ✅ | Carrega odds ao selecionar liga no carrossel |
| Odds comparativas | ✅ | Tabela comparativa Bet365 vs Betano por partida |
| Comparação de bilhetes | ✅ | Lado a lado Bet365 vs Betano com recomendação |
| Análise de odds | ✅ | 3 estratégias + diversificação de mercados |
| Seletor de estratégia | ✅ | Na tela de Previsões (re-analisa ao trocar) |
| Resumo de previsões | ✅ | Exibe TODAS as odds de cada mercado por jogo |
| Carrossel de ligas | ✅ | Multi-select, busca, filtro país/tipo, seção ao vivo |
| Filtros avançados | ✅ | Status, odds, rodada, data, horário |
| Bilhete editável (modal) | ✅ | Trocar mercado/resultado de cada aposta |
| Acompanhamento ao vivo | ✅ | Placar, minuto, barra progresso, ganhando/perdendo |
| Bilhetes SQLite | ✅ | CRUD completo com status + dados ao vivo |
| Ligas ao vivo | ✅ | Seção no carrossel com jogos em andamento |
| Timezone | ✅ | America/Sao_Paulo configurável |
| Mocks | ❌ Removido | Sem dados mockados |

### Abordagem

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  API-Football → Fixtures + Odds → OddsAnalyzer → Recomendações             │
│                                                                             │
│  ✅ Dados reais (jogos, odds, times, status ao vivo)                        │
│  ✅ Comparação entre casas (Bet365, Betano) — por partida e por bilhete     │
│  ✅ Identificação de value bets                                             │
│  ✅ 3 estratégias personalizadas com diversificação                         │
│  ✅ Troca de estratégia na tela de previsões (re-analisa mesmo jogos)       │
│  ✅ Cache incremental em SQLite (fixtures e odds separados)                 │
│  ✅ Odds carregadas sob demanda POR LIGA (ao selecionar no carrossel)       │
│  ✅ Carrossel de ligas com multi-select, busca e filtros                    │
│  ✅ Filtros avançados (status, odds, rodada, data, horário)                 │
│  ✅ Bilhete editável com todas as opções de cada mercado                    │
│  ✅ Acompanhamento ao vivo (placar, minuto, barra progresso)               │
│  ✅ Seção de ligas ao vivo com jogos em andamento                           │
│  ✅ Timezone correto (America/Sao_Paulo)                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Tecnológica

### Backend

| Tecnologia | Uso |
|------------|-----|
| Python 3.14 | Linguagem principal |
| FastAPI | Framework web |
| Uvicorn | Servidor ASGI |
| Pydantic + pydantic-settings | Validação e configuração |
| httpx | Cliente HTTP (API-Football) |
| SQLite | Cache persistente + banco de tickets |
| zoneinfo + tzdata | Timezone (America/Sao_Paulo) |

### Frontend

| Tecnologia | Uso |
|------------|-----|
| React 18 | UI Library |
| TypeScript | Tipagem |
| Vite | Build tool + dev server + proxy |
| Fetch API | HTTP nativo |

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🌐 FRONTEND (React + Vite)                           │
│                         http://localhost:5173                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📄 Pages                   ⚡ Contexts                 🧩 Components       │
│  ├── Dashboard.tsx          ├── AppContext.tsx          ├── LeagueCarousel │
│  ├── Matches.tsx            ├── MatchesContext.tsx      ├── MatchCard.tsx  │
│  ├── Predictions.tsx        ├── BookmakerContext.tsx    ├── MatchList.tsx  │
│  └── Tickets.tsx            ├── PredictionContext.tsx   ├── StatusMultiSel │
│                             └── TicketContext.tsx       ├── PredictionCard │
│  🪝 Hooks                                              ├── BookmakerComp. │
│  └── useMatches.ts          🛠️ Services                ├── TicketBuilder  │
│     (preload + odds/liga)   ├── api/apiClient.ts       ├── TicketModal   │
│                             ├── api/apiEndpoints.ts    └── TicketHistory  │
│                             ├── notificationService.ts                     │
│                             └── storageService.ts                          │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │ HTTP/JSON (proxy /api → :8000)
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                        📡 BACKEND (FastAPI)                                  │
│                        http://localhost:8000                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🌐 WEB LAYER (web/)                                                        │
│  ├── controllers/                                                           │
│  │   ├── match_controller.py      GET /matches, /matches/live, /leagues    │
│  │   │                            GET /bookmakers                          │
│  │   │                            GET|POST /matches/{id}/odds              │
│  │   ├── prediction_controller.py POST /analyze (+ odds_by_bookmaker)      │
│  │   ├── ticket_controller.py     GET|POST /tickets, /stats/dashboard      │
│  │   │                            POST /tickets/update-results             │
│  │   │                            POST /tickets/{id}/update-result         │
│  │   └── preload_controller.py    POST /preload/fetch, /odds/league        │
│  │                                GET /preload/status                      │
│  ├── dtos/                        Requests + Responses (Pydantic)          │
│  └── mappers/                     Domain → DTO conversion                  │
│                                                                             │
│  📦 APPLICATION LAYER (application/)                                        │
│  └── services/                                                              │
│      ├── match_application_service.py   Lê cache, filtra ativos            │
│      ├── prediction_application_service.py  OddsAnalyzer + previsões       │
│      ├── preload_service.py             Cache incremental + odds por liga   │
│      ├── ticket_application_service.py  CRUD bilhetes                      │
│      └── ticket_updater_service.py      Atualiza resultados + dados ao vivo│
│                                                                             │
│  🧠 DOMAIN LAYER (domain/)                                                  │
│  ├── constants/constants.py     Ligas, status, thresholds                  │
│  ├── enums/                     MarketType, Strategy, TicketStatus, etc.   │
│  ├── interfaces/                Contratos abstratos (ABC)                  │
│  ├── models/                    Match, Odds, Ticket, Bet (+ live fields)   │
│  ├── services/odds_analyzer.py  Lógica de estratégias e value bets        │
│  └── utils/                     Validators, calculators, formatters        │
│                                                                             │
│  🔧 INFRASTRUCTURE LAYER (infrastructure/)                                  │
│  ├── cache/                                                                 │
│  │   └── sqlite_cache_manager.py  Cache SQLite com TTL (cache.db)          │
│  ├── database/                                                              │
│  │   ├── connection.py            SQLite para tickets (tickets.db)         │
│  │   └── repositories/            TicketRepository                         │
│  └── external/api_football/                                                 │
│      ├── client.py                HTTP client (httpx)                      │
│      ├── service.py               Fixtures + Odds + Live + Season          │
│      └── parsers/                 fixture_parser, odds_parser              │
│                                                                             │
│  ⚙️ CONFIG (config/)                                                        │
│  └── settings.py                  Pydantic Settings + timezone helpers      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas

```
component-betting-advisor-app/
├── start_all.bat / start_all.sh        # Inicia backend + frontend
├── docs/
│   ├── ARQUITETURA.md                  # Este documento
│   ├── FLUXO_FUNCIONAL.md             # Fluxo funcional
│   └── postman/                        # Collections Postman
│
├── web_api/                            # 🔙 BACKEND
│   ├── requirements.txt
│   ├── start.bat / start.sh
│   ├── data/
│   │   ├── cache.db                    # SQLite cache (fixtures, odds, seasons)
│   │   └── tickets.db                  # SQLite tickets (+ live fields)
│   ├── scripts/
│   │   ├── init_cache.py
│   │   └── init_database.py
│   ├── static/escudos/                 # 40+ escudos PNG locais
│   └── src/
│       ├── main.py
│       ├── config/
│       │   ├── .env
│       │   └── settings.py
│       ├── web/
│       │   ├── controllers/            # match, prediction, ticket, preload
│       │   ├── dtos/                   # requests/ + responses/
│       │   └── mappers/
│       ├── application/services/
│       │   ├── match_application_service.py
│       │   ├── prediction_application_service.py
│       │   ├── preload_service.py      # Inclui preload de odds por liga
│       │   ├── ticket_application_service.py
│       │   └── ticket_updater_service.py
│       ├── domain/
│       │   ├── constants/constants.py
│       │   ├── enums/
│       │   ├── interfaces/
│       │   ├── models/                 # Bet inclui elapsed, goals_home, goals_away
│       │   ├── services/odds_analyzer.py
│       │   └── utils/
│       └── infrastructure/
│           ├── cache/sqlite_cache_manager.py
│           ├── database/
│           │   ├── connection.py       # Migração automática de colunas live
│           │   └── repositories/ticket_repository.py
│           └── external/api_football/
│               ├── client.py
│               ├── service.py          # get_fixtures, get_odds, get_live, etc.
│               └── parsers/
│
└── web_app/                            # ⚛️ FRONTEND
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── src/
        ├── Main.tsx / App.tsx
        ├── components/
        │   ├── common/     Header, Loading
        │   ├── dashboard/  StatsCard, QuickGuide
        │   ├── matches/    LeagueCarousel, MatchList, MatchCard,
        │   │               StatusMultiSelect, LeagueMultiSelect
        │   ├── predictions/ BookmakerComparison, PredictionCard,
        │   │                ConfidenceMeter, PredictionPanel
        │   └── tickets/    TicketBuilder, TicketModal, TicketHistory
        ├── contexts/       App, Bookmaker, Matches, Prediction, Ticket
        ├── hooks/          useMatches.ts
        ├── pages/          Dashboard, Matches, Predictions, Tickets
        ├── services/       api/, notificationService, storageService
        ├── styles/         globals.css
        └── types/          index.ts
```

---

## 🔙 Backend — Camadas

### Config (`config/settings.py`)

```python
class Settings(BaseSettings):
    API_FOOTBALL_KEY: Optional[str] = None
    API_FOOTBALL_BASE_URL: str = "https://v3.football.api-sports.io"
    TIMEZONE: str = "America/Sao_Paulo"
    SUPPORTED_BOOKMAKERS: str = "bet365,betano"
    CACHE_TTL_FIXTURES: int = 21600   # 6h
    CACHE_TTL_ODDS: int = 1800        # 30min

    def today(self) -> date:
        return datetime.now(self.tz).date()

    def now(self) -> datetime:
        return datetime.now(self.tz)
```

### Web Layer (`web/controllers/`)

| Controller | Responsabilidade |
|-----------|-----------------|
| `match_controller` | Listar jogos, odds, leagues, bookmakers, jogos ao vivo |
| `prediction_controller` | Analisar jogos com OddsAnalyzer + `odds_by_bookmaker` |
| `ticket_controller` | CRUD bilhetes + dashboard stats + atualização de resultados |
| `preload_controller` | Preload sob demanda + odds por liga |

### Application Layer (`application/services/`)

| Service | Responsabilidade |
|---------|-----------------|
| `preload_service` | Cache incremental de fixtures (Hoje→3→7 dias) + odds por liga |
| `match_application_service` | Lê cache, filtra partidas ativas, atualiza dados ao vivo |
| `prediction_application_service` | OddsAnalyzer para previsões + `odds_by_bookmaker` |
| `ticket_application_service` | CRUD de bilhetes no SQLite |
| `ticket_updater_service` | Busca resultados reais + atualiza status/placar/minuto ao vivo |

### Domain Layer (`domain/`)

| Componente | Descrição |
|-----------|-----------|
| `constants.py` | ACTIVE_STATUSES, etc. |
| `enums/` | BettingStrategy (3: CONSERVATIVE, BALANCED, AGGRESSIVE), MarketType, TicketStatus |
| `models/bet_model.py` | `status`, `status_short`, `elapsed`, `goals_home`, `goals_away` |
| `services/odds_analyzer.py` | Lógica de estratégias e value bets com diversificação |

### Infrastructure Layer (`infrastructure/`)

| Componente | Descrição |
|-----------|-----------|
| `cache/sqlite_cache_manager.py` | Cache SQLite com TTL |
| `database/connection.py` | SQLite com migração automática de colunas live |
| `database/repositories/` | TicketRepository (CRUD com campos live nas bets) |
| `external/api_football/service.py` | get_fixtures, get_odds, get_fixture_result, get_live_fixtures |

---

## ⚛️ Frontend — Componentes

### Hook Principal: `useMatches.ts`

```typescript
export function useMatches() {
  // 1. fetchByPeriod(days) — POST /preload/fetch + GET /matches
  // 2. loadOddsByLeague(leagueId) — POST /preload/odds/league
  // 3. fetchLiveMatches() — GET /matches/live (polling)
  // 4. updateMatchOdds(id, odds) — atualiza state individual
  // 5. updateMatchOddsAndStatus(id, odds, status, statusShort) — refresh
}
```

### Contexts

| Context | Responsabilidade |
|---------|-----------------|
| `AppContext` | Tab ativa, estado global |
| `BookmakerContext` | Lista de bookmakers, seleção, nome por ID |
| `MatchesContext` | Matches, período, ligas, filtros |
| `PredictionContext` | Previsões, estratégia, re-análise |
| `TicketContext` | Pré-bilhete, bilhetes, modal, edição |

### Componentes Principais

| Componente | Descrição |
|-----------|-----------|
| `LeagueCarousel` | Carrossel multi-select com busca, filtro país/tipo (Liga/Copa), seção ao vivo |
| `MatchList` | Seletor de período (Hoje/3/7 dias), filtros avançados, expand/collapse |
| `MatchCard` | Badge de status, tabela comparativa de odds. Sem odds = desabilitado |
| `StatusMultiSelect` | Multi-select agrupado (Ao Vivo, Programados, Encerrados) |
| `BookmakerComparison` | 2 pré-bilhetes lado a lado com recomendação |
| `TicketModal` | Modal de criação/edição — troca mercado/resultado entre todas as alternativas |
| `TicketHistory` | Acompanhamento rico: placar, minuto, barra progresso, ganhando/perdendo |

### Filtros Avançados

| Filtro | Descrição |
|--------|-----------|
| 📊 Status | Multi-select: Ao Vivo, Não Iniciado, Encerrado |
| 💰 Com/Sem Odds | Jogos com odds carregadas |
| 🔄 Rodada | Fase do campeonato |
| 📅 Data | Dia específico dentro do período |
| 🕐 Horário | Turno (manhã, tarde, noite) |

### Fluxo de Telas

```
┌────────────┐    ┌─────────────────────┐    ┌───────────────────┐    ┌────────────────┐
│  Dashboard │    │       Jogos         │    │    Previsões      │    │    Bilhetes     │
│  stats     │    │  Período Hoje/3/7   │    │  3 Estratégias    │    │  Histórico      │
│            │    │  Carrossel de ligas  │───▶│  Todas as odds    │───▶│  Placar ao vivo │
│            │    │  Filtros avançados   │    │  Comparação casas │    │  Minuto/Barra   │
│            │    │  Odds por liga       │    │  Modal editável   │    │  Ganho/Perdendo │
└────────────┘    └─────────────────────┘    └───────────────────┘    └────────────────┘
```

---

## 🌐 API-Football Integration

### Endpoints Usados

| Endpoint API-Football | Uso no Sistema |
|---|---|
| `GET /fixtures?league={id}&date={date}&season={year}` | Buscar jogos por liga e data |
| `GET /odds?league={id}&date={date}&page={n}` | Buscar odds por liga/data (bulk) |
| `GET /fixtures?id={id}` | Resultado/status de partida |
| `GET /fixtures?live=all` | Buscar jogos ao vivo |
| `GET /leagues?id={id}&current=true` | Resolver season atual da liga |

### Carregamento de Odds — Por Liga

Em vez de buscar por fixture individual (1 request por jogo), busca por **liga + data** (bulk):

```
POST /api/v1/preload/odds/league
Body: { "league_id": 71 }

→ Backend: GET /odds?league=71&date=2026-02-27 (paginado)
→ Retorna todas as odds de todos os jogos da liga na data
→ Muito mais eficiente (1 request por liga/data vs N por fixture)
```

### Season Resolution

- Busca `GET /leagues?id={id}&current=true`
- Cacheia por 7 dias (`season:{league_id}`)

---

## 💾 Sistema de Cache

### TTLs

| Tipo | TTL | Motivo |
|------|-----|--------|
| Fixtures | 6h | Pouca mudança durante o dia |
| Odds | 30min | Mudam frequentemente |
| Season | 7 dias | Não muda durante a temporada |
| Preload meta | 24h | Controle de cache incremental |

---

## ⏰ Timezone

`zoneinfo.ZoneInfo('America/Sao_Paulo')` — configurável via `.env` (`TIMEZONE`).

---

## 📡 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/preload/fetch?days=N` | POST | Pré-carrega fixtures (1, 3, 7 dias) |
| `/api/v1/preload/status` | GET | Status do cache |
| `/api/v1/preload/odds` | POST | Odds em lote (body: fixture_ids) |
| `/api/v1/preload/odds/league` | POST | Odds por liga (body: league_id) |
| `/api/v1/matches` | GET | Lista jogos |
| `/api/v1/matches/live` | GET | Jogos ao vivo |
| `/api/v1/matches/{id}/odds` | GET | Odds de uma partida |
| `/api/v1/matches/{id}/odds/refresh` | POST | Refresh odds + status |
| `/api/v1/leagues` | GET | Campeonatos disponíveis |
| `/api/v1/bookmakers` | GET | Casas de apostas |
| `/api/v1/analyze` | POST | Analisa jogos |
| `/api/v1/tickets` | GET/POST | Lista / Cria bilhete |
| `/api/v1/tickets/{id}` | GET/DELETE | Detalhes / Deleta |
| `/api/v1/tickets/{id}/update-result` | POST | Atualiza resultado de um bilhete |
| `/api/v1/tickets/stats/dashboard` | GET | Estatísticas |
| `/api/v1/tickets/update-results` | POST | Atualiza todos os pendentes |
| `/health` | GET | Health check |

---

## ⚙️ Configurações

### `.env`

```bash
API_FOOTBALL_KEY=sua_chave_aqui
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
TIMEZONE=America/Sao_Paulo
SUPPORTED_BOOKMAKERS=bet365,betano
CACHE_TTL_FIXTURES=21600
CACHE_TTL_ODDS=1800
CACHE_TTL_LEAGUES=604800
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 📐 Banco de Dados (tickets.db)

### Tabela `bets`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | INTEGER PK | Auto-increment |
| ticket_id | TEXT FK | Referência ao ticket |
| match_id | TEXT | ID da partida |
| home_team | TEXT | Nome do mandante |
| away_team | TEXT | Nome do visitante |
| league | TEXT | Nome da liga |
| market | TEXT | MATCH_WINNER, OVER_UNDER, BTTS |
| predicted_outcome | TEXT | HOME, DRAW, AWAY, OVER, UNDER, YES, NO |
| odds | REAL | Odd da aposta |
| confidence | REAL | Confiança (0.0–1.0) |
| result | TEXT | WON, LOST, null |
| final_score | TEXT | "2 x 1" ou null |
| status | TEXT | Status longo da partida |
| status_short | TEXT | NS, 1H, HT, 2H, FT, etc. |
| elapsed | INTEGER | Minuto do jogo (ex: 45, 67, 90) |
| goals_home | INTEGER | Gols do time da casa |
| goals_away | INTEGER | Gols do time visitante |
