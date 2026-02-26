# 🎰 Betting Advisor - Arquitetura do Sistema

> Sistema de sugestão de bilhetes de apostas esportivas — API-Football integrada

**Data:** 2026-02-26  
**Versão:** 4.0.0  
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
| Preload sob demanda | ✅ | 3, 7 ou 14 dias (apenas fixtures) |
| Odds sob demanda | ✅ | Batch automático após preload + refresh individual |
| Odds comparativas | ✅ | Tabela comparativa Bet365 vs Betano por partida |
| Comparação de bilhetes | ✅ | Lado a lado Bet365 vs Betano com recomendação |
| Análise de odds | ✅ | 4 estratégias + diversificação de mercados |
| Seletor de estratégia | ✅ | Na tela de Previsões (re-analisa ao trocar) |
| Bilhetes SQLite | ✅ | CRUD completo com status de partidas |
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
│  ✅ 4 estratégias personalizadas com diversificação                         │
│  ✅ Troca de estratégia na tela de previsões (re-analisa mesmo jogos)       │
│  ✅ Cache incremental em SQLite (fixtures e odds separados)                 │
│  ✅ Odds carregadas sob demanda (batch + refresh individual)                │
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
│  ├── Dashboard.tsx          ├── AppContext.tsx          ├── MatchCard.tsx   │
│  ├── Matches.tsx            ├── MatchesContext.tsx      ├── MatchList.tsx   │
│  ├── Predictions.tsx        ├── PredictionContext.tsx   ├── PredictionCard │
│  └── Tickets.tsx            └── TicketContext.tsx       ├── BookmakerComp. │
│                                                        ├── TicketBuilder  │
│  🪝 Hooks                   🛠️ Services                └── TicketHistory  │
│  └── useMatches.ts          ├── api/apiClient.ts                           │
│     (preload + odds batch)  ├── api/apiEndpoints.ts                        │
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
│  │   ├── match_controller.py      GET /matches, /leagues, /bookmakers      │
│  │   │                            GET|POST /matches/{id}/odds              │
│  │   │                            POST /matches/odds/batch                 │
│  │   ├── prediction_controller.py POST /analyze (+ odds_by_bookmaker)      │
│  │   ├── ticket_controller.py     GET|POST /tickets, /stats/dashboard      │
│  │   └── preload_controller.py    POST /preload/fetch, GET /preload/status │
│  ├── dtos/                        Requests + Responses (Pydantic)          │
│  └── mappers/                     Domain → DTO conversion                  │
│                                                                             │
│  📦 APPLICATION LAYER (application/)                                        │
│  └── services/                                                              │
│      ├── match_application_service.py   Lê cache, filtra ativos            │
│      ├── prediction_application_service.py  OddsAnalyzer + previsões       │
│      ├── preload_service.py             Cache incremental de fixtures       │
│      ├── ticket_application_service.py  CRUD bilhetes                      │
│      └── ticket_updater_service.py      Atualiza resultados + status       │
│                                                                             │
│  🧠 DOMAIN LAYER (domain/)                                                  │
│  ├── constants/constants.py     Ligas, status, thresholds                  │
│  ├── enums/                     MarketType, Strategy, TicketStatus, etc.   │
│  ├── interfaces/                Contratos abstratos (ABC)                  │
│  ├── models/                    Match, Odds, Ticket, Bet (+ status fields) │
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
│      ├── service.py               Fixtures + Odds + Season resolution      │
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
│   ├── requirements.txt                # fastapi, httpx, pydantic, tzdata
│   ├── start.bat / start.sh
│   ├── data/
│   │   ├── cache.db                    # SQLite cache (fixtures, odds, seasons)
│   │   └── tickets.db                  # SQLite tickets (+ status partidas)
│   ├── scripts/
│   │   ├── init_cache.py               # Inicializa cache.db
│   │   └── init_database.py            # Inicializa tickets.db
│   ├── static/escudos/                 # 40+ escudos PNG locais
│   └── src/
│       ├── main.py                     # FastAPI app + startup
│       ├── config/
│       │   ├── .env                    # API_FOOTBALL_KEY, TIMEZONE, etc.
│       │   └── settings.py             # Pydantic Settings + today()/now()
│       ├── web/
│       │   ├── controllers/            # match, prediction, ticket, preload
│       │   ├── dtos/                   # requests/ + responses/
│       │   └── mappers/                # match_mapper, prediction_mapper, etc.
│       ├── application/services/       # Lógica de aplicação
│       │   ├── match_application_service.py
│       │   ├── prediction_application_service.py
│       │   ├── preload_service.py
│       │   ├── ticket_application_service.py
│       │   └── ticket_updater_service.py
│       ├── domain/
│       │   ├── constants/constants.py  # ACTIVE_STATUSES, MAIN_LEAGUES, etc.
│       │   ├── enums/                  # Strategy, MarketType, TicketStatus...
│       │   ├── interfaces/             # ABC abstratos
│       │   ├── models/                 # Match, Team, Odds, Ticket, Bet, Prediction
│       │   ├── services/odds_analyzer.py
│       │   └── utils/
│       └── infrastructure/
│           ├── cache/sqlite_cache_manager.py
│           ├── database/
│           │   ├── connection.py       # Tabelas: tickets, bets (+ status fields)
│           │   └── repositories/ticket_repository.py
│           └── external/api_football/
│               ├── client.py           # httpx client
│               ├── service.py          # get_fixtures, get_odds, get_fixture_result
│               └── parsers/
│                   ├── fixture_parser.py
│                   └── odds_parser.py
│
└── web_app/                            # ⚛️ FRONTEND
    ├── package.json
    ├── vite.config.ts                  # Proxy /api → localhost:8000
    ├── tsconfig.json
    └── src/
        ├── Main.tsx / App.tsx
        ├── components/
        │   ├── common/     Header, Loading
        │   ├── dashboard/  StatsCard, QuickGuide
        │   ├── matches/    MatchList, MatchCard
        │   ├── predictions/ BookmakerComparison, PredictionCard, ConfidenceMeter
        │   └── tickets/    TicketBuilder, TicketHistory
        ├── contexts/       App, Matches, Prediction, Ticket
        ├── hooks/          useMatches.ts (preload + odds batch)
        ├── pages/          Dashboard, Matches, Predictions, Tickets
        ├── services/       api/, notificationService, storageService
        ├── styles/         globals.css
        └── types/          index.ts
```

---

## 🔙 Backend — Camadas

### Config (`config/settings.py`)

Pydantic Settings carregando `.env`:

```python
class Settings(BaseSettings):
    API_FOOTBALL_KEY: Optional[str] = None
    API_FOOTBALL_BASE_URL: str = "https://v3.football.api-sports.io"
    TIMEZONE: str = "America/Sao_Paulo"
    SUPPORTED_BOOKMAKERS: str = "bet365,betano"
    MAIN_LEAGUES: str = "71,73,39,140,78,61,135"
    CACHE_TTL_FIXTURES: int = 21600   # 6h
    CACHE_TTL_ODDS: int = 1800        # 30min

    def today(self) -> date:
        return datetime.now(self.tz).date()

    def now(self) -> datetime:
        return datetime.now(self.tz)
```

### Web Layer (`web/controllers/`)

Controllers HTTP — delegam para Application Services:

| Controller | Responsabilidade |
|-----------|-----------------|
| `match_controller` | Listar jogos, odds, leagues, bookmakers |
| `prediction_controller` | Analisar jogos com OddsAnalyzer + `odds_by_bookmaker` |
| `ticket_controller` | CRUD bilhetes + dashboard stats |
| `preload_controller` | Disparar preload sob demanda |

### Application Layer (`application/services/`)

| Service | Responsabilidade |
|---------|-----------------|
| `preload_service` | Cache incremental de fixtures (3→7→14 dias), SEM odds |
| `match_application_service` | Lê cache, filtra partidas ativas, odds filtradas por bookmaker |
| `prediction_application_service` | Usa OddsAnalyzer para gerar previsões + retorna `odds_by_bookmaker` |
| `ticket_application_service` | CRUD de bilhetes no SQLite |
| `ticket_updater_service` | Busca resultados reais na API-Football + atualiza status/status_short |

### Domain Layer (`domain/`)

| Componente | Descrição |
|-----------|-----------|
| `constants.py` | ACTIVE_STATUSES, MAIN_LEAGUES, LEAGUE_NAMES, etc. |
| `enums/` | BettingStrategy, MarketType, TicketStatus, RiskLevel |
| `models/` | Match, Team, League, Odds, Prediction, Ticket, Bet |
| `models/bet_model.py` | Inclui `status` e `status_short` (status da partida) |
| `services/odds_analyzer.py` | Lógica de estratégias e value bets com diversificação |
| `utils/` | Validators, calculators, formatters |

### Infrastructure Layer (`infrastructure/`)

| Componente | Descrição |
|-----------|-----------|
| `cache/sqlite_cache_manager.py` | Cache SQLite com TTL (get/set/delete_by_prefix) |
| `database/connection.py` | SQLite para tickets (inclui migração de colunas status) |
| `database/repositories/` | TicketRepository (CRUD com status/status_short nas bets) |
| `external/api_football/client.py` | HTTP client httpx |
| `external/api_football/service.py` | get_fixtures, get_odds, get_fixture_result, _get_current_season |
| `external/api_football/parsers/` | fixture_parser (com timezone local), odds_parser |

---

## ⚛️ Frontend — Componentes

### Hook Principal: `useMatches.ts`

Gerencia todo o fluxo de carregamento:

```typescript
export function useMatches() {
  // 1. fetchByPeriod(days) — POST /preload/fetch + GET /matches
  // 2. loadAllOdds(matches) — POST /matches/odds/batch (chunks de 10)
  // 3. updateMatchOdds(id, odds) — atualiza state individual
  // 4. updateMatchOddsAndStatus(id, odds, status, statusShort) — refresh individual
}
```

### Contexts

| Context | Responsabilidade |
|---------|-----------------|
| `AppContext` | Tab ativa, liga selecionada |
| `MatchesContext` | Matches carregados, período, filtros |
| `PredictionContext` | Previsões, estratégia atual, re-análise, lastMatchIds |
| `TicketContext` | Pré-bilhete, bilhetes criados |

> **Nota:** `BookmakerContext` foi removido. A seleção de casa de apostas agora acontece na comparação de bilhetes (Predictions).

### Componentes Principais

| Componente | Descrição |
|-----------|-----------|
| `MatchList` | Seletor de período, filtro por liga, select all/by day, expand/collapse |
| `MatchCard` | Badge de status, tabela comparativa de odds, botão refresh 🔄 |
| `BookmakerComparison` | **Novo** — 2 pré-bilhetes lado a lado (Bet365 vs Betano) com recomendação |
| `PredictionCard` | Mercado, confiança, value bet %, recomendação (usado no resumo compacto) |
| `TicketBuilder` | Bilhete editável, stake, retorno potencial, badge da casa de apostas |
| `TicketHistory` | Lista de bilhetes com badges de status das partidas |

### Fluxo de Telas

```
┌────────────┐    ┌─────────────────┐    ┌──────────────────────┐    ┌────────────┐
│  Dashboard │    │      Jogos      │    │     Previsões        │    │  Bilhetes  │
│  stats     │    │  Período 3/7/14 │    │  Estratégia (troca)  │    │  Histórico │
│            │    │  Filtro Liga    │───▶│  Resumo compacto     │───▶│  Status    │
│            │    │  Select All/Day │    │  Comparação casas    │    │  Resultado │
│            │    │  Odds comparar  │    │  Bilhete editável    │    │            │
└────────────┘    └─────────────────┘    └──────────────────────┘    └────────────┘
```

---

## 🌐 API-Football Integration

### Endpoints Usados

| Endpoint API-Football | Uso no Sistema |
|---|---|
| `GET /fixtures?league={id}&date={date}&season={year}` | Buscar jogos por liga e data |
| `GET /odds?fixture={id}` | Buscar odds de uma partida |
| `GET /fixtures?id={id}` | Resultado/status de partida |
| `GET /leagues?id={id}&current=true` | Resolver season atual da liga |

### Season Resolution

A API-Football requer o parâmetro `season` para fixtures. O sistema resolve automaticamente:
- Busca `GET /leagues?id={id}&current=true`
- Cacheia por 7 dias (`season:{league_id}`)
- Ligas europeias: ano de início (ex: 2025 para 2025/2026)
- Ligas brasileiras: ano corrente (ex: 2026)

### Filtro de Bookmakers

O `odds_parser` retorna odds de todas as casas. O `match_application_service` filtra apenas as casas em `SUPPORTED_BOOKMAKERS` (padrão: `bet365,betano`), definido em `config/settings.py`.

---

## 💾 Sistema de Cache

### SQLite Cache (`data/cache.db`)

```
┌─────────────────────────────────────────────────────────────────┐
│ Tabela: cache                                                    │
├──────────────────┬──────────────┬────────────────────────────────┤
│ key (PK)         │ value (JSON) │ expires_at (TIMESTAMP)         │
├──────────────────┼──────────────┼────────────────────────────────┤
│ fixtures:71:...  │ [...]        │ 2026-02-26 23:00:00           │
│ odds:1234567     │ {...}        │ 2026-02-26 17:30:00           │
│ season:71        │ 2026         │ 2026-03-05 14:00:00           │
│ preload:last_date│ "2026-02-26" │ 2026-02-27 14:00:00           │
│ preload:last_days│ 7            │ 2026-02-27 14:00:00           │
└──────────────────┴──────────────┴────────────────────────────────┘
```

### Cache Incremental (Preload)

```python
# PreloadService.preload_fixtures()
1. _get_cached_period() → ex: 3 (já tem 3 dias cacheados hoje)
2. Se pedir 7 dias e já tem 3 → busca apenas dias 4-7
3. Se pedir 3 dias e já tem 7 → não faz nada (cache cobre)
4. Se dia mudou → limpa cache antigo, busca tudo de novo
```

**Importante:** O preload carrega APENAS fixtures (jogos). Odds são carregadas separadamente via batch automático ou refresh individual.

### TTLs

| Tipo | TTL | Motivo |
|------|-----|--------|
| Fixtures | 6h | Pouca mudança durante o dia |
| Odds | 30min | Mudam frequentemente |
| Season | 7 dias | Não muda durante a temporada |
| Preload meta | 24h | Controle de cache incremental |

---

## ⏰ Timezone

O sistema usa `zoneinfo.ZoneInfo('America/Sao_Paulo')` para todos os cálculos de data:

- `settings.today()` → data de hoje na timezone configurada
- `settings.now()` → datetime atual na timezone configurada
- `fixture_parser.py` → converte timestamps da API para timezone local

Configurável via `.env`:
```
TIMEZONE=America/Sao_Paulo
```

Dependência: `tzdata` (necessário no Windows).

---

## 📡 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/preload/fetch?days=N` | POST | Pré-carrega fixtures (3, 7, 14 dias) |
| `/api/v1/preload/status` | GET | Status do cache |
| `/api/v1/matches` | GET | Lista jogos (query: date_from, date_to, league_id) |
| `/api/v1/matches/{id}/odds` | GET | Odds de uma partida (cache ou API) |
| `/api/v1/matches/{id}/odds/refresh` | POST | Força refresh de odds + status |
| `/api/v1/matches/odds/batch` | POST | Odds em lote (body: fixture_ids) |
| `/api/v1/leagues` | GET | Lista campeonatos disponíveis |
| `/api/v1/bookmakers` | GET | Lista casas de apostas suportadas |
| `/api/v1/analyze` | POST | Analisa jogos (body: match_ids, strategy) — retorna `odds_by_bookmaker` |
| `/api/v1/tickets` | GET | Lista bilhetes (com status das partidas) |
| `/api/v1/tickets` | POST | Cria bilhete |
| `/api/v1/tickets/{id}` | GET | Detalhes de um bilhete |
| `/api/v1/tickets/{id}` | DELETE | Deleta bilhete |
| `/api/v1/tickets/stats/dashboard` | GET | Estatísticas do dashboard |
| `/api/v1/tickets/update-results` | POST | Atualiza resultados reais (+ status_short) |
| `/health` | GET | Health check |

---

## ⚙️ Configurações

### `.env` (web_api/src/config/.env)

```bash
# API-Football (obrigatório)
API_FOOTBALL_KEY=sua_chave_aqui
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io

# Timezone
TIMEZONE=America/Sao_Paulo

# Casas de apostas
SUPPORTED_BOOKMAKERS=bet365,betano

# Ligas principais
MAIN_LEAGUES=71,73,39,140,78,61,135

# Cache TTLs (segundos)
CACHE_TTL_FIXTURES=21600
CACHE_TTL_ODDS=1800
CACHE_TTL_LEAGUES=604800

# Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=false
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### `requirements.txt`

```
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.10.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
httpx>=0.28.0
tzdata>=2024.1
```

### Vite Proxy (`vite.config.ts`)

```typescript
export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true }
    }
  }
})
```

---

## 🖼️ Logos dos Times

Estratégia **Local First, API Fallback**:

1. `fixture_parser` verifica se existe logo local em `static/escudos/`
2. Se encontrar → `{ url: "/static/escudos/flamengo.png", type: "LOCAL" }`
3. Se não → `{ url: "https://media.api-sports.io/...", type: "EXT" }`

Frontend trata transparentemente:
```typescript
const getTeamLogoUrl = (logo: Logo): string => {
  if (logo.type === 'EXT') return logo.url;
  return `http://localhost:8000${logo.url}`;
};
```

---

## 📐 Banco de Dados (tickets.db)

### Tabela `tickets`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | TEXT PK | UUID do bilhete |
| name | TEXT | Nome do bilhete |
| stake | REAL | Valor apostado |
| bookmaker_id | TEXT | Casa de apostas (bet365, betano) |
| status | TEXT | PENDING, WON, LOST |
| created_at | TIMESTAMP | Data de criação |

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
| predicted_outcome | TEXT | HOME, DRAW, AWAY, OVER_2.5, etc. |
| odds | REAL | Odd da aposta |
| confidence | REAL | Confiança (0.0–1.0) |
| result | TEXT | WON, LOST, null |
| final_score | TEXT | "2 x 1" ou null |
| status | TEXT | Status longo da partida |
| status_short | TEXT | NS, 1H, HT, 2H, FT, etc. |

