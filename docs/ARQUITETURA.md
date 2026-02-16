# 🎰 Betting Bot - Arquitetura do Sistema (V2)

> Sistema de sugestão de bilhetes de apostas esportivas - **Implementação Real**

**Data:** 2026-02-17  
**Versão:** 2.0.0  
**Status:** ✅ POC Implementada (Frontend + Backend Mock)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológica](#stack-tecnológica)
3. [Arquitetura Atual (POC)](#arquitetura-atual-poc)
4. [Estrutura de Pastas Real](#estrutura-de-pastas-real)
5. [Endpoints da API](#endpoints-da-api)
6. [Fluxo de Dados](#fluxo-de-dados)
7. [Componentes Frontend](#componentes-frontend)
8. [Estado Global (Contexts)](#estado-global-contexts)
9. [Próximos Passos](#próximos-passos)

---

## 🎯 Visão Geral

### Status Atual da Implementação

O sistema está atualmente em **fase de POC (Proof of Concept)** com:
- ✅ **Frontend completo** (React + TypeScript + Vite)
- ✅ **Backend com controllers mockados** (FastAPI)
- ✅ **Estrutura de dados definida** (DTOs e Types)
- ⏳ **Integração com API-Football** (próxima etapa)
- ⏳ **Modelos de IA** (próxima etapa)

### Características Principais

| Característica | Status | Descrição |
|---------------|---------|-----------|
| **Frontend React** | ✅ Implementado | Interface completa com todas as telas |
| **Backend FastAPI** | ✅ Implementado | Controllers com dados mockados |
| **DTOs e Types** | ✅ Implementado | Contratos de dados TypeScript/Python |
| **Escudos dos Times** | ✅ Implementado | 130+ escudos servidos pelo backend |
| **Estado Global** | ✅ Implementado | Contexts API (React) |
| **Cache API-Football** | ⏳ Planejado | Sistema de cache com TTL |
| **Modelos de IA** | ⏳ Planejado | Poisson + XGBoost |

---

## 🛠️ Stack Tecnológica

### Backend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.14 | Linguagem principal |
| **FastAPI** | 0.109.0 | Framework web |
| **Uvicorn** | 0.27.0 | Servidor ASGI |
| **Pydantic** | 2.5.3 | Validação de dados |
| **httpx** | 0.26.0 | Cliente HTTP (API-Football) |
| **python-dotenv** | 1.0.0 | Variáveis de ambiente |

### Frontend

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **React** | 18.x | UI Library |
| **TypeScript** | 5.x | Linguagem |
| **Vite** | 5.x | Build tool |
| **Fetch API** | Native | Cliente HTTP |

---

## 🏗️ Arquitetura Atual (POC)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🌐 FRONTEND (React + Vite)                           │
│                         http://localhost:5173                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📄 Pages (Rotas)           ⚡ Contexts (Estado)      🧩 Components         │
│  ├── Dashboard.tsx          ├── AppContext            ├── MatchCard         │
│  ├── Matches.tsx            ├── BookmakerContext     ├── MatchList         │
│  ├── Predictions.tsx        ├── PredictionContext    ├── PredictionCard    │
│  └── Tickets.tsx            └── TicketContext        └── TicketBuilder     │
│                                                                             │
│  🛠️ Services                                                                │
│  ├── api/apiClient.ts          (HTTP Client)                               │
│  ├── api/apiEndpoints.ts       (Endpoints)                                 │
│  ├── notificationService.ts    (Toasts)                                    │
│  └── storageService.ts         (LocalStorage)                              │
│                                                                             │
└──────────────────────────────┬──────────────────────────────────────────────┘
                               │
                               │ HTTP/JSON
                               │
┌──────────────────────────────▼──────────────────────────────────────────────┐
│                        📡 BACKEND (FastAPI)                                  │
│                        http://localhost:8000                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  🎮 Controllers (web/controllers/)                                          │
│  ├── match_controller.py                                                   │
│  │   ├── GET  /api/v1/matches         → Lista jogos (mockado)              │
│  │   ├── GET  /api/v1/leagues         → Lista ligas (mockado)              │
│  │   └── GET  /api/v1/bookmakers      → Lista casas (mockado)              │
│  │                                                                          │
│  ├── prediction_controller.py                                              │
│  │   └── POST /api/v1/analyze         → Analisa jogos (mockado)            │
│  │                                                                          │
│  └── ticket_controller.py                                                  │
│      ├── GET  /api/v1/tickets         → Lista bilhetes                     │
│      ├── POST /api/v1/tickets         → Cria bilhete                       │
│      ├── GET  /api/v1/tickets/stats/dashboard → Estatísticas              │
│      └── POST /api/v1/tickets/{id}/simulate → Simula resultado            │
│                                                                             │
│  📦 DTOs (web/dtos/responses/)                                              │
│  ├── logo_dto.py              → LogoDTO (url + type: LOCAL/EXT)            │
│  ├── match_response.py        → Match, Team, League, Bookmaker             │
│  ├── prediction_response.py   → Prediction, MarketPrediction               │
│  └── ticket_response.py       → Ticket, TicketBet                          │
│                                                                             │
│  📁 Static Files                                                            │
│  └── /static/escudos/         → 130+ escudos PNG (servido via StaticFiles) │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas Real

```
component-betting-advisor-app/
│
├── start_all.bat                         # 🪟 Inicia backend + frontend
├── start_all.sh                          # 🐧 Inicia backend + frontend
├── .gitignore                            # Git ignore global
├── README.md
│
├── docs/                                 # 📚 Documentação
│   ├── ARQUITETURA.md                    # Arquitetura completa (planejada)
│   ├── ARQUITETURA_V2.md                 # Este documento (implementação real)
│   ├── FLUXO_FUNCIONAL.md               # Fluxo funcional detalhado
│   └── MODELO_IA.md                     # Modelos de IA
│
├── data/                                 # 💾 Banco de Dados (futuro)
│   └── (vazio - será criado quando necessário)
│
├── web_api/                              # 🔙 BACKEND
│   ├── start.bat                         # Inicia apenas backend
│   ├── start.sh
│   ├── requirements.txt                  # fastapi, uvicorn, pydantic, httpx
│   ├── README.md
│   │
│   ├── src/                              # Código fonte
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app
│   │   │
│   │   ├── web/                          # Web Layer
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── controllers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── match_controller.py   # 410 linhas
│   │   │   │   ├── prediction_controller.py  # 310 linhas
│   │   │   │   └── ticket_controller.py  # 280 linhas
│   │   │   │
│   │   │   └── dtos/
│   │   │       ├── __init__.py
│   │   │       ├── requests/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── match_request.py
│   │   │       │   ├── prediction_request.py
│   │   │       │   └── ticket_request.py
│   │   │       │
│   │   │       └── responses/
│   │   │           ├── __init__.py
│   │   │           ├── logo_dto.py       # LogoDTO (url + type)
│   │   │           ├── match_response.py # 146 linhas
│   │   │           ├── prediction_response.py
│   │   │           └── ticket_response.py
│   │   │
│   │   └── static/                       # Arquivos estáticos
│   │       └── escudos/                  # 130+ escudos PNG
│   │           ├── flamengo.png
│   │           ├── palmeiras.png
│   │           ├── corinthians.png
│   │           ├── manchester-city.png
│   │           ├── arsenal.png
│   │           └── ... (130+ arquivos)
│   │
│   └── .venv/                            # Ambiente virtual
│
└── web_app/                              # ⚛️ FRONTEND
    ├── start.bat                         # Inicia apenas frontend
    ├── start.sh
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    │
    ├── .gitignore                        # Ignora dist/ e node_modules/
    │
    ├── public/
    │   └── vite.svg
    │
    └── src/
        ├── main.tsx                      # Entry point
        ├── App.tsx                       # Root component
        │
        ├── components/                   # Componentes React
        │   ├── common/
        │   │   ├── Header.tsx            # 118 linhas
        │   │   ├── Sidebar.tsx           # 95 linhas
        │   │   └── Loading.tsx           # 18 linhas
        │   │
        │   ├── dashboard/
        │   │   ├── index.ts              # Barrel export
        │   │   ├── StatsCard.tsx         # 42 linhas
        │   │   └── QuickGuide.tsx        # 65 linhas
        │   │
        │   ├── matches/
        │   │   ├── MatchList.tsx         # 233 linhas (com collapse/expand)
        │   │   └── MatchCard.tsx         # 95 linhas
        │   │
        │   ├── predictions/
        │   │   ├── PredictionPanel.tsx   # 187 linhas
        │   │   ├── PredictionCard.tsx    # 142 linhas
        │   │   └── ConfidenceMeter.tsx   # 48 linhas
        │   │
        │   └── tickets/
        │       ├── TicketBuilder.tsx     # 156 linhas
        │       └── TicketHistory.tsx     # 198 linhas
        │
        ├── contexts/                     # Context API
        │   ├── AppContext.tsx            # Estado da aplicação
        │   ├── BookmakerContext.tsx      # Casas de apostas
        │   ├── PredictionContext.tsx     # Previsões
        │   └── TicketContext.tsx         # Bilhetes
        │
        ├── hooks/
        │   └── useMatches.ts             # Hook de jogos
        │
        ├── pages/
        │   ├── index.ts                  # Barrel export
        │   ├── Dashboard.tsx             # 156 linhas
        │   ├── Matches.tsx               # 189 linhas
        │   ├── Predictions.tsx           # 142 linhas
        │   └── Tickets.tsx               # 178 linhas
        │
        ├── services/
        │   ├── notificationService.ts    # Toast notifications
        │   ├── storageService.ts         # LocalStorage tipado
        │   │
        │   └── api/
        │       ├── apiClient.ts          # HTTP Client (fetch)
        │       ├── apiEndpoints.ts       # 108 linhas
        │       └── index.ts              # Barrel export
        │
        ├── styles/
        │   └── globals.css               # 1594 linhas (CSS completo)
        │
        └── types/
            └── index.ts                  # 141 linhas (todas as interfaces)
```

---

## 🔌 Endpoints da API

### 📊 Match Controller

#### `GET /api/v1/matches`
Lista jogos disponíveis para análise.

**Query Params:**
- `date` (optional): Data no formato `YYYY-MM-DD`
- `league_id` (optional): ID da liga (`l1`, `l2`, `l3`)

**Response:**
```json
{
  "success": true,
  "date": "2026-02-17",
  "count": 10,
  "matches": [
    {
      "id": "uuid",
      "league": {
        "id": "l1",
        "name": "Brasileirão Série A",
        "country": "Brazil",
        "logo": "🇧🇷",
        "type": "league"
      },
      "home_team": {
        "id": "t1",
        "name": "Flamengo",
        "logo": {
          "url": "/static/escudos/flamengo.png",
          "type": "LOCAL"
        },
        "country": "Brazil"
      },
      "away_team": {
        "id": "t2",
        "name": "Palmeiras",
        "logo": {
          "url": "/static/escudos/palmeiras.png",
          "type": "LOCAL"
        },
        "country": "Brazil"
      },
      "date": "2026-02-17T15:00:00Z",
      "status": "NS",
      "round": {
        "type": "round",
        "number": 5,
        "name": "Rodada 5"
      },
      "venue": {
        "name": "Maracanã",
        "city": "Rio de Janeiro"
      },
      "odds": {
        "bet365": {
          "home": 2.10,
          "draw": 3.20,
          "away": 2.80,
          "over_25": 1.85,
          "under_25": 1.90,
          "btts_yes": 1.75,
          "btts_no": 1.95
        },
        "betano": {
          "home": 2.12,
          "draw": 3.18,
          "away": 2.85,
          "over_25": 1.88,
          "under_25": 1.87,
          "btts_yes": 1.78,
          "btts_no": 1.92
        }
      }
    }
  ]
}
```

#### `GET /api/v1/leagues`
Lista ligas/campeonatos disponíveis.

**Response:**
```json
{
  "success": true,
  "count": 3,
  "leagues": [
    {
      "id": "l1",
      "name": "Brasileirão Série A",
      "country": "Brazil",
      "logo": "🇧🇷",
      "type": "league"
    },
    {
      "id": "l2",
      "name": "Copa do Brasil",
      "country": "Brazil",
      "logo": "🏆",
      "type": "cup"
    },
    {
      "id": "l3",
      "name": "Premier League",
      "country": "England",
      "logo": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
      "type": "league"
    }
  ]
}
```

#### `GET /api/v1/bookmakers`
Lista casas de apostas disponíveis.

**Response:**
```json
{
  "success": true,
  "count": 2,
  "bookmakers": [
    {
      "id": "bet365",
      "name": "Bet365",
      "logo": "🎰",
      "is_default": true
    },
    {
      "id": "betano",
      "name": "Betano",
      "logo": "⚡",
      "is_default": false
    }
  ]
}
```

---

### 🧠 Prediction Controller

#### `POST /api/v1/analyze`
Analisa jogos selecionados e retorna previsões.

**Request Body:**
```json
{
  "match_ids": ["uuid1", "uuid2", "uuid3"],
  "strategy": "BALANCED"
}
```

**Estratégias disponíveis:**
- `BALANCED` - Balanceada (confiança + value)
- `CONSERVATIVE` - Conservadora (alta confiança)
- `VALUE_BET` - Value Bet (foco em value)
- `AGGRESSIVE` - Agressiva (odds altas)

**Response:**
```json
{
  "success": true,
  "predictions": [
    {
      "match_id": "uuid1",
      "match_name": "Flamengo vs Palmeiras",
      "league": "Brasileirão Série A",
      "bookmaker_id": "bet365",
      "markets": [
        {
          "market_type": "1X2",
          "market_name": "Resultado Final",
          "prediction": "HOME",
          "prediction_label": "Vitória Flamengo",
          "confidence": 72.5,
          "odd": 2.10,
          "value_bet_percentage": 12.3,
          "expected_value": 1.52,
          "is_recommended": true,
          "risk_level": "MEDIUM"
        }
      ]
    }
  ],
  "pre_ticket": {
    "bets": [...],
    "total_bets": 3,
    "combined_odds": 6.84,
    "message": "Pré-bilhete criado com 3 apostas"
  }
}
```

---

### 🎫 Ticket Controller

#### `GET /api/v1/tickets`
Lista todos os bilhetes criados.

**Response:**
```json
{
  "success": true,
  "tickets": [
    {
      "id": "uuid",
      "name": "Bilhete 17/02/2026, 15:30",
      "bookmaker_id": "bet365",
      "stake": 100.0,
      "total_odds": 6.84,
      "potential_return": 684.0,
      "status": "PENDING",
      "result": null,
      "created_at": "2026-02-17T15:30:00Z",
      "bets": [
        {
          "match_id": "uuid1",
          "match_name": "Flamengo vs Palmeiras",
          "market_type": "1X2",
          "prediction": "HOME",
          "prediction_label": "Vitória Flamengo",
          "odd": 2.10,
          "confidence": 72.5,
          "status": "PENDING",
          "result": null,
          "match_result": null
        }
      ]
    }
  ]
}
```

#### `POST /api/v1/tickets`
Cria um novo bilhete.

**Request Body:**
```json
{
  "name": "Meu Bilhete",
  "stake": 100.0,
  "bookmaker_id": "bet365",
  "bets": [
    {
      "match_id": "uuid1",
      "match_name": "Flamengo vs Palmeiras",
      "market_type": "1X2",
      "prediction": "HOME",
      "prediction_label": "Vitória Flamengo",
      "odd": 2.10,
      "confidence": 72.5
    }
  ]
}
```

#### `GET /api/v1/tickets/stats/dashboard`
Retorna estatísticas para o dashboard.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_tickets": 25,
    "won_tickets": 18,
    "lost_tickets": 5,
    "pending_tickets": 2,
    "success_rate": 78.26,
    "total_staked": 2500.0,
    "total_profit": 450.0
  }
}
```

#### `POST /api/v1/tickets/{ticket_id}/simulate`
Simula resultado de um bilhete (desenvolvimento).

**Response:**
```json
{
  "success": true,
  "message": "Resultado simulado com sucesso",
  "ticket": {
    "id": "uuid",
    "status": "WON",
    "result": {
      "total_correct": 3,
      "total_wrong": 0,
      "profit": 584.0
    }
  }
}
```

---

## 🔄 Fluxo de Dados

### 1️⃣ Carregar Jogos

```
Frontend                 Backend
   │                        │
   ├─ GET /matches?─────────▶│
   │  league_id=l1           │
   │                         │
   │                         ├─ Gera jogos mockados
   │                         ├─ Ordena por data/hora
   │                         ├─ Retorna JSON
   │                         │
   │◀────── 200 OK ──────────┤
   │ { matches: [...] }      │
   │                         │
   ├─ Agrupa por data        │
   ├─ Renderiza MatchList    │
   └─ (collapse/expand)      │
```

### 2️⃣ Analisar Jogos

```
Frontend                 Backend
   │                        │
   ├─ Seleciona jogos       │
   ├─ Escolhe estratégia    │
   ├─ Clica "Analisar"      │
   │                        │
   ├─ POST /analyze ────────▶│
   │ { match_ids, strategy }│
   │                         │
   │                         ├─ Busca jogos no cache
   │                         ├─ Calcula previsões (mock)
   │                         ├─ Aplica estratégia
   │                         ├─ Cria pré-bilhete
   │                         │
   │◀────── 200 OK ──────────┤
   │ { predictions, pre_ticket }
   │                         │
   ├─ Exibe PredictionPanel │
   ├─ Mostra pré-bilhete    │
   └─ Permite ajustes       │
```

### 3️⃣ Criar Bilhete

```
Frontend                 Backend
   │                        │
   ├─ Confirma apostas      │
   ├─ Define stake          │
   ├─ Clica "Criar Bilhete" │
   │                        │
   ├─ POST /tickets ────────▶│
   │ { name, stake, bets }  │
   │                         │
   │                         ├─ Valida dados
   │                         ├─ Cria ticket em memória
   │                         ├─ Retorna ticket criado
   │                         │
   │◀────── 201 Created ─────┤
   │ { ticket }              │
   │                         │
   ├─ Navega para /tickets  │
   ├─ Exibe TicketHistory   │
   └─ (aguarda resultado)   │
```

### 4️⃣ Simular Resultado (Dev)

```
Frontend                 Backend
   │                        │
   ├─ (5s após criar)       │
   │                        │
   ├─ POST /tickets/{id}/───▶│
   │      simulate           │
   │                         │
   │                         ├─ Simula resultado (random)
   │                         ├─ Atualiza status
   │                         ├─ Calcula lucro/prejuízo
   │                         │
   │◀────── 200 OK ──────────┤
   │ { ticket updated }      │
   │                         │
   ├─ Atualiza lista        │
   └─ Destaca resultado     │
      (verde=ganho, vermelho=perda)
```

---

## 🧩 Componentes Frontend

### Hierarquia de Componentes

```
App.tsx (Providers)
│
├─ AppContext            (tab, strategy, selectedLeague)
├─ BookmakerContext      (bookmakers, selectedBookmaker)
├─ PredictionContext     (predictions, analyzing)
└─ TicketContext         (tickets, preTicket)
   │
   ├─ Header.tsx         (navegação de tabs)
   ├─ Sidebar.tsx        (menu lateral - futuro)
   │
   └─ Pages/
      │
      ├─ Dashboard.tsx   ─┬─ StatsCard.tsx (4x)
      │                   └─ QuickGuide.tsx
      │
      ├─ Matches.tsx     ─┬─ MatchList.tsx
      │                   │  ├─ Filtros (estratégia, liga, casa)
      │                   │  ├─ Botão "Minimizar Todas"
      │                   │  ├─ Grupos por data (collapse/expand)
      │                   │  └─ MatchCard.tsx (N)
      │                   │     ├─ Escudos (logo.url LOCAL/EXT)
      │                   │     ├─ Data/hora
      │                   │     ├─ Estádio
      │                   │     └─ Odds (casa selecionada)
      │                   │
      │                   └─ Botão "Analisar Selecionados"
      │
      ├─ Predictions.tsx ─┬─ PredictionPanel.tsx
      │                   │  └─ PredictionCard.tsx (N)
      │                   │     ├─ ConfidenceMeter.tsx
      │                   │     ├─ Mercados disponíveis
      │                   │     └─ Checkbox para bilhete
      │                   │
      │                   └─ TicketBuilder.tsx (pré-bilhete)
      │                      ├─ Lista de apostas
      │                      ├─ Odds combinadas
      │                      ├─ Stake
      │                      └─ Botão "Criar Bilhete"
      │
      └─ Tickets.tsx     ─┬─ TicketBuilder.tsx (atual)
                          │
                          └─ TicketHistory.tsx
                             └─ Card por ticket
                                ├─ Status (PENDING/WON/LOST)
                                ├─ Lista de apostas
                                │  └─ Icones (✓ green / ✗ red)
                                ├─ Odds + Stake
                                └─ Resultado final
```

### Componentes Chave

#### MatchCard.tsx
```typescript
// Exibe um jogo individual
interface MatchCardProps {
  match: Match;
  isSelected: boolean;
  onSelect: (matchId: string) => void;
  selectedBookmaker: string;
}

// Features:
// - Escudos dos times (via backend /static/escudos/)
// - LogoDTO (LOCAL ou EXT)
// - Data/hora formatada (pt-BR)
// - Estádio real do time mandante
// - Odds da casa selecionada
// - Click para selecionar
```

#### MatchList.tsx
```typescript
// Lista com filtros e agrupamento por data
// Features:
// - Filtros: estratégia, liga, casa
// - Agrupamento por data com collapse/expand
// - Botão "Minimizar/Expandir Todas"
// - Ícones: ▼ (expandido) / ► (colapsado)
// - Headers de data com contador de jogos
// - Ordenação por data e horário
```

#### PredictionCard.tsx
```typescript
// Exibe previsão de um jogo
// Features:
// - Múltiplos mercados (1X2, Over/Under, BTTS)
// - Confiança visual (ConfidenceMeter)
// - Value Bet % destacado
// - Checkbox para incluir no bilhete
// - Explicação da previsão (futuro: via IA)
```

#### TicketHistory.tsx
```typescript
// Lista de bilhetes criados
// Features:
// - Agrupamento por status
// - Destaque de apostas ganhas/perdidas
// - Cálculo de lucro/prejuízo
// - Simulação automática após 5s (dev)
// - Indicadores visuais (✓/✗)
```

---

## ⚡ Estado Global (Contexts)

### AppContext
```typescript
// Estado geral da aplicação
{
  activeTab: 'matches' | 'predictions' | 'tickets' | 'dashboard',
  strategy: 'BALANCED' | 'CONSERVATIVE' | 'VALUE_BET' | 'AGGRESSIVE',
  selectedLeague: string,
  setActiveTab,
  setStrategy,
  setSelectedLeague
}
```

### BookmakerContext
```typescript
// Casas de apostas
{
  bookmakers: Bookmaker[],
  selectedBookmaker: string,  // 'bet365' por padrão
  setSelectedBookmaker,
  loadBookmakers  // GET /bookmakers
}
```

### PredictionContext
```typescript
// Previsões e análises
{
  predictions: Prediction[],
  analyzing: boolean,
  analyzeMatches: (matchIds, strategy) => Promise<void>,  // POST /analyze
  clearPredictions
}
```

### TicketContext
```typescript
// Bilhetes
{
  tickets: Ticket[],
  preTicket: PreTicket | null,
  ticketsInBet: Set<string>,
  addToBet,
  removeFromBet,
  createTicket,  // POST /tickets
  loadTickets,   // GET /tickets
  simulateResult  // POST /tickets/{id}/simulate
}
```

---

## 🚀 Próximos Passos

### Fase 2: Integração com API-Football

#### Backend
- [ ] Implementar cliente HTTP para API-Football
- [ ] Sistema de cache com TTL por tipo de dado
- [ ] Parser de fixtures e estatísticas
- [ ] Parser de odds de múltiplas casas
- [ ] Mapeamento de ligas e times reais

#### Tabela de Cache
```sql
CREATE TABLE api_cache (
    id UUID PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_key ON api_cache(cache_key);
CREATE INDEX idx_expires_at ON api_cache(expires_at);
```

#### TTLs Recomendados
| Tipo de Dado | TTL | Motivo |
|--------------|-----|--------|
| Fixtures (futuros) | 6 horas | Pouco mudança |
| Odds | 30 minutos | Mudam frequentemente |
| Estatísticas time | 24 horas | Atualiza por rodada |
| Histórico H2H | 7 dias | Não muda |
| Previsões API | 12 horas | Comparação |

### Fase 3: Modelos de IA

#### Implementar
- [ ] Modelo Poisson para Over/Under e BTTS
- [ ] Modelo XGBoost para Resultado 1X2
- [ ] Ensemble (combinação dos dois)
- [ ] Value Bet Calculator
- [ ] Sistema de confiança ajustável por estratégia

#### Dataset
- [ ] Baixar CSVs históricos (Football-Data.co.uk)
- [ ] Feature engineering
- [ ] Treinar modelo inicial
- [ ] Pipeline de atualização contínua

### Fase 4: Melhorias UX

- [ ] Explicação das previsões via IA (texto gerado)
- [ ] Gráficos de histórico de H2H
- [ ] Filtros avançados (por odds, confiança, value)
- [ ] Modo escuro/claro
- [ ] Export de bilhetes (PDF/Imagem)
- [ ] Notificações de resultado

### Fase 5: Banco de Dados

- [ ] Migrar de mock para SQLite
- [ ] Persistir bilhetes
- [ ] Histórico de previsões
- [ ] Estatísticas de acurácia
- [ ] Logs de uso

---

## 📊 Métricas do Projeto

### Código Frontend

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `globals.css` | 1594 | CSS completo |
| `MatchList.tsx` | 233 | Lista com collapse |
| `TicketHistory.tsx` | 198 | Histórico de bilhetes |
| `Matches.tsx` | 189 | Página de jogos |
| `PredictionPanel.tsx` | 187 | Painel de previsões |
| `Tickets.tsx` | 178 | Página de bilhetes |
| **Total Frontend** | **~3500** | TypeScript + CSS |

### Código Backend

| Arquivo | Linhas | Descrição |
|---------|--------|-----------|
| `match_controller.py` | 480 | Controller de jogos |
| `prediction_controller.py` | 310 | Controller de previsões |
| `ticket_controller.py` | 280 | Controller de bilhetes |
| `match_response.py` | 146 | DTOs de resposta |
| **Total Backend** | **~1300** | Python (mock) |

### Assets

| Tipo | Quantidade |
|------|------------|
| **Escudos PNG** | 130+ |
| **Componentes React** | 15 |
| **Contexts** | 4 |
| **Endpoints API** | 9 |
| **DTOs** | 12 |

---

## 🎉 Conclusão

O sistema está com a **POC completa implementada**, incluindo:

✅ Frontend totalmente funcional  
✅ Backend com controllers mockados  
✅ Estrutura de dados bem definida  
✅ Fluxo de usuário completo  
✅ Visual profissional  
✅ Pronto para integração com API-Football  
✅ Pronto para implementação dos modelos de IA  

**Próximo passo:** Integrar API-Football e implementar cache! 🚀

