# 🎰 Betting Bot - Arquitetura do Sistema

> Sistema de sugestão de bilhetes de apostas esportivas - **Implementação Real**

**Data:** 2026-02-17  
**Versão:** 1.0.0  
**Status:** ✅ Em Desenvolvimento (Frontend + Backend Mock)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [API-Football Integration](#api-football-integration)
3. [Stack Tecnológica](#stack-tecnológica)
4. [Arquitetura Atual](#arquitetura-atual)
5. [Estrutura de Pastas Real](#estrutura-de-pastas-real)
6. [Endpoints da API](#endpoints-da-api)
7. [Lógica de Análise](#lógica-de-análise)
8. [Fluxo de Dados](#fluxo-de-dados)
9. [Componentes Frontend](#componentes-frontend)
10. [Estado Global (Contexts)](#estado-global-contexts)
11. [Próximos Passos](#próximos-passos)

---

## 🎯 Visão Geral

### Status Atual da Implementação

O sistema está atualmente em **fase de desenvolvimento** com:
- ✅ **Frontend completo** (React + TypeScript + Vite)
- ✅ **Backend com controllers mockados** (FastAPI)
- ✅ **Estrutura de dados definida** (DTOs e Types)
- ⏳ **Integração com API-Football** (próxima etapa)
- ⏳ **Análise inteligente de odds** (próxima etapa)

### Abordagem do Sistema

**Sistema baseado em análise inteligente de odds da API-Football:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🎯 ABORDAGEM SIMPLIFICADA E EFICAZ                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  API-Football → Fixtures + Odds → Análise por Estratégia → Recomendações   │
│                                                                             │
│  ✅ Dados reais de jogos e odds                                             │
│  ✅ Comparação entre casas (Bet365, Betano, etc.)                           │
│  ✅ Análise inteligente baseada em odds                                     │
│  ✅ Identificação de value bets                                             │
│  ✅ Estratégias personalizadas                                              │
│                                                                             │
│  ❌ SEM complexidade de IA/ML                                               │
│  ❌ SEM necessidade de dados históricos                                     │
│  ❌ SEM treinamento de modelos                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Características Principais

| Característica | Status | Descrição |
|---------------|---------|-----------|
| **Frontend React** | ✅ Implementado | Interface completa com todas as telas |
| **Backend FastAPI** | ✅ Implementado | Controllers com dados mockados |
| **DTOs e Types** | ✅ Implementado | Contratos de dados TypeScript/Python |
| **Escudos dos Times** | ✅ Implementado | 130+ escudos servidos pelo backend |
| **Estado Global** | ✅ Implementado | Contexts API (React) |
| **API-Football** | ⏳ Planejado | Fixtures + Odds reais |
| **Cache Inteligente** | ⏳ Planejado | Sistema de cache com TTL |
| **Análise de Odds** | ⏳ Planejado | Comparação e value bets |

---

## 🌐 API-Football Integration

### Por que API-Football?

A **API-Football** fornece dados completos e confiáveis de futebol em tempo real:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       🎯 VANTAGENS DA API-FOOTBALL                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ Dados Reais                                                             │
│     • Jogos acontecendo agora                                               │
│     • Times e ligas oficiais                                                │
│     • Resultados em tempo real                                              │
│                                                                             │
│  ✅ Odds de Múltiplas Casas                                                 │
│     • Bet365, Betano, Pinnacle, 1xBet, etc.                                 │
│     • Comparação automática entre casas                                     │
│     • Identificação de discrepâncias (value bets)                           │
│                                                                             │
│  ✅ Cobertura Completa                                                      │
│     • 900+ ligas e copas                                                    │
│     • Todas as grandes ligas europeias                                      │
│     • Brasileirão Série A e B                                               │
│     • Copa do Brasil, Libertadores, etc.                                    │
│                                                                             │
│  ✅ Atualização Frequente                                                   │
│     • Odds atualizadas a cada 30 minutos                                    │
│     • Fixtures atualizados a cada 6 horas                                   │
│     • Status dos jogos em tempo real                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Endpoints Utilizados

| Endpoint | Descrição | Uso no Sistema | TTL Cache |
|----------|-----------|----------------|-----------|
| `GET /fixtures` | Jogos por data/liga | Buscar jogos do dia | 6 horas |
| `GET /odds` | Odds de várias casas | Comparar odds | 30 minutos |
| `GET /odds/bookmakers` | Lista casas disponíveis | Configuração | 24 horas |
| `GET /leagues` | Ligas disponíveis | Filtro de campeonatos | 7 dias |

### Exemplo de Response - Fixtures

```json
{
  "response": [
    {
      "fixture": {
        "id": 1035148,
        "date": "2026-02-17T18:00:00+00:00",
        "status": {
          "short": "NS",
          "long": "Not Started"
        },
        "venue": {
          "name": "Maracanã",
          "city": "Rio de Janeiro"
        }
      },
      "league": {
        "id": 71,
        "name": "Série A",
        "country": "Brazil",
        "logo": "https://media.api-sports.io/football/leagues/71.png",
        "round": "Regular Season - 5"
      },
      "teams": {
        "home": {
          "id": 127,
          "name": "Flamengo",
          "logo": "https://media.api-sports.io/football/teams/127.png"
        },
        "away": {
          "id": 128,
          "name": "Palmeiras",
          "logo": "https://media.api-sports.io/football/teams/128.png"
        }
      }
    }
  ]
}
```

### Exemplo de Response - Odds

```json
{
  "response": [
    {
      "fixture": {
        "id": 1035148
      },
      "bookmakers": [
        {
          "id": 6,
          "name": "Bet365",
          "bets": [
            {
              "id": 1,
              "name": "Match Winner",
              "values": [
                { "value": "Home", "odd": "2.10" },
                { "value": "Draw", "odd": "3.20" },
                { "value": "Away", "odd": "2.80" }
              ]
            },
            {
              "id": 5,
              "name": "Goals Over/Under",
              "values": [
                { "value": "Over 2.5", "odd": "1.85" },
                { "value": "Under 2.5", "odd": "1.90" }
              ]
            },
            {
              "id": 8,
              "name": "Both Teams Score",
              "values": [
                { "value": "Yes", "odd": "1.75" },
                { "value": "No", "odd": "1.95" }
              ]
            }
          ]
        },
        {
          "id": 85,
          "name": "Betano",
          "bets": [
            {
              "id": 1,
              "name": "Match Winner",
              "values": [
                { "value": "Home", "odd": "2.15" },
                { "value": "Draw", "odd": "3.18" },
                { "value": "Away", "odd": "2.75" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

### Sistema de Cache

```python
# TTLs recomendados por tipo de dado
CACHE_TTL = {
    "fixtures": 6 * 60 * 60,      # 6 horas (pouca mudança)
    "odds": 30 * 60,               # 30 minutos (mudam frequentemente)
    "leagues": 7 * 24 * 60 * 60,  # 7 dias (não mudam)
    "bookmakers": 24 * 60 * 60     # 24 horas (raramente mudam)
}

# Exemplo de implementação
@cache(ttl=CACHE_TTL["fixtures"])
async def get_fixtures(league_id: int, date: str):
    """Busca fixtures com cache de 6 horas"""
    response = await api_football_client.get(
        "/fixtures",
        params={"league": league_id, "date": date}
    )
    return response.json()
```

### Limites do Plano Gratuito

| Recurso | Limite Gratuito | Recomendação |
|---------|-----------------|--------------|
| **Requests/Dia** | 100 | Use cache agressivo |
| **Requests/Minuto** | 30 | Batch requests |
| **Histórico** | 2 anos | Suficiente |
| **Cobertura** | 900+ ligas | Excelente |

**Estratégia de Otimização:**
- ✅ Cache de 6h para fixtures → 1 request/liga/dia
- ✅ Cache de 30min para odds → 2 requests/hora
- ✅ Buscar apenas ligas selecionadas pelo usuário
- ✅ Batch de jogos de uma vez

**Total estimado:** 10-20 requests/dia (bem dentro do limite)

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

## 🏗️ Arquitetura Atual

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

### Implementação com API-Football (Sem Mocks)

```
component-betting-advisor-app/
│
├── start_all.bat                         # 🪟 Inicia backend + frontend
├── start_all.sh                          # 🐧 Inicia backend + frontend
├── .gitignore                            # Ignora .env, .venv, etc.
├── README.md
│
├── docs/                                 # 📚 Documentação
│   ├── ARQUITETURA.md                    # Este documento
│   └── FLUXO_FUNCIONAL.md               # Fluxo funcional
│
├── data/                                 # 💾 Banco de Dados
│   └── betting.db                        # SQLite (cache + tickets)
│
├── web_api/                              # 🔙 BACKEND
│   ├── start.bat
│   ├── start.sh
│   ├── requirements.txt                  # fastapi, httpx, sqlalchemy
│   │
│   ├── .venv/                            # 🐍 Ambiente virtual Python
│   │
│   ├── scripts/                          # 📜 Scripts de inicialização
│   │   ├── __init__.py
│   │   └── init_database.py              # Cria tabelas do SQLite
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app
│   │   │
│   │   ├── static/                       # 📁 Arquivos estáticos
│   │   │   └── escudos/                  # 🖼️ Logos dos times (cache local)
│   │   │       ├── flamengo.png
│   │   │       ├── palmeiras.png
│   │   │       ├── manchester-city.png
│   │   │       └── ... (populado dinamicamente)
│   │   │
│   │   ├── config/                       # ⚙️ Configurações
│   │   │   ├── .env                      # 🔑 API_FOOTBALL_KEY
│   │   │   ├── .env.example              # Template do .env
│   │   │   ├── __init__.py
│   │   │   └── settings.py               # Load .env
│   │   │
│   │   ├── web/                          # 🌐 WEB LAYER
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── controllers/              # Controllers (usa Application Services)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── match_controller.py   # Usa MatchApplicationService
│   │   │   │   ├── prediction_controller.py  # Usa PredictionApplicationService
│   │   │   │   └── ticket_controller.py  # Usa TicketApplicationService
│   │   │   │
│   │   │   └── dtos/                     # DTOs
│   │   │       ├── __init__.py
│   │   │       ├── requests/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── analyze_request.py
│   │   │       │   └── ticket_request.py
│   │   │       │
│   │   │       └── responses/
│   │   │           ├── __init__.py
│   │   │           ├── logo_dto.py       # type: EXT (API)
│   │   │           ├── match_response.py
│   │   │           ├── prediction_response.py
│   │   │           └── ticket_response.py
│   │   │
│   │   ├── application/                  # 📦 APPLICATION LAYER
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   └── services/                 # Application Services
│   │   │       ├── __init__.py
│   │   │       ├── match_application_service.py
│   │   │       ├── prediction_application_service.py
│   │   │       └── ticket_application_service.py
│   │   │
│   │   ├── domain/                       # 🧠 DOMAIN LAYER (CORE - SEM DEPENDÊNCIAS)
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── models/                   # 📦 Domain Models (Entities)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── match_model.py        # Match, Fixture
│   │   │   │   ├── team_model.py         # Team (com Logo)
│   │   │   │   ├── logo_model.py         # Logo (LOCAL ou EXTERNAL)
│   │   │   │   ├── league_model.py       # League, Competition
│   │   │   │   ├── odds_model.py         # Odds, BookmakerOdds
│   │   │   │   ├── ticket_model.py       # Ticket (Bilhete)
│   │   │   │   ├── bet_model.py          # Bet (Aposta individual)
│   │   │   │   └── prediction_model.py   # Prediction, Analysis
│   │   │   │
│   │   │   ├── enums/                    # 🔢 Domain Enums
│   │   │   │   ├── __init__.py
│   │   │   │   ├── match_status_enum.py  # NS, LIVE, FT, CANC, etc.
│   │   │   │   ├── market_type_enum.py   # MATCH_WINNER, OVER_UNDER, BTTS
│   │   │   │   ├── betting_strategy_enum.py  # CONSERVATIVE, VALUE_BET, etc.
│   │   │   │   ├── ticket_status_enum.py # PENDING, WON, LOST
│   │   │   │   ├── provider_type_enum.py # API_FOOTBALL, FOOTBALL_DATA, etc.
│   │   │   │   ├── logo_type_enum.py     # LOCAL, EXTERNAL
│   │   │   │   └── risk_level_enum.py    # LOW, MEDIUM, HIGH
│   │   │   │
│   │   │   ├── interfaces/               # 📋 Interfaces (Contratos Abstratos)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── football_provider_interface.py  # ABC genérico
│   │   │   │   └── odds_provider_interface.py      # ABC genérico
│   │   │   │
│   │   │   ├── services/                 # 🧠 Domain Services (Lógica de Negócio)
│   │   │   │   ├── __init__.py
│   │   │   │   └── odds_analyzer.py      # Lógica de estratégias
│   │   │   │
│   │   │   ├── constants/                # 📏 Domain Constants (Regras de Negócio)
│   │   │   │   ├── __init__.py
│   │   │   │   └── constants.py          # Thresholds, ranges, estratégias
│   │   │   │
│   │   │   └── utils/                    # 🛠️ Domain Utils
│   │   │       ├── __init__.py
│   │   │       ├── validators_util.py
│   │   │       ├── calculators_util.py
│   │   │       └── formatters_util.py
│   │   │
│   │   └── infrastructure/               # 🔧 INFRASTRUCTURE
│   │       ├── __init__.py
│   │       │
│   │       ├── database/                 # SQLite
│   │       │   ├── __init__.py
│   │       │   ├── connection.py         # Engine
│   │       │   ├── models.py             # SQLAlchemy
│   │       │   │
│   │       │   └── repositories/
│   │       │       ├── __init__.py
│   │       │       ├── ticket_repository.py
│   │       │
│   │       ├── external/                 # 🔌 Providers (Implementam Interfaces)
│   │       │   ├── __init__.py
│   │       │   │
│   │       │   ├── api_football/         # 🌐 Provider: API-Football
│   │       │   │   ├── __init__.py
│   │       │   │   ├── api_football_client.py       # HTTP Client (httpx)
│   │       │   │   ├── api_football_provider.py     # Implementa FootballProviderInterface
│   │       │   │   │
│   │       │   │   ├── mappers/          # 🔄 API → Domain (De-Para)
│   │       │   │   │   ├── __init__.py
│   │       │   │   │   ├── fixture_to_match_mapper.py    # JSON → Match (domain)
│   │       │   │   │   ├── team_mapper.py                # JSON → Team (domain)
│   │       │   │   │   ├── league_mapper.py              # JSON → League (domain)
│   │       │   │   │   └── odds_mapper.py                # JSON → Odds (domain)
│   │       │   │   │
│   │       │   │   └── parsers/          # 🔍 Parse JSON da API
│   │       │   │       ├── __init__.py
│   │       │   │       ├── fixture_parser.py
│   │       │   │       ├── odds_parser.py
│   │       │   │       └── league_parser.py
│   │       │   │
│   │       │   └── football_data/        # 🔄 Futuro: Outro Provider (exemplo)
│   │       │       ├── __init__.py
│   │       │       ├── football_data_client.py
│   │       │       ├── football_data_provider.py    # Implementa FootballProviderInterface
│   │       │       └── mappers/
│   │       │           └── ...
│   │       │
│   │       ├── factories/                # 🏭 Factories
│   │       │   ├── __init__.py
│   │       │   └── provider_factory.py   # Cria provider baseado em config
│   │       │
│   │       └── cache/                    # Cache System
│   │           ├── __init__.py
│   │           ├── cache_manager.py      # TTL logic
│   │           └── cache_config.py       # TTL constants
│
└── web_app/                              # ⚛️ FRONTEND
    ├── start.bat
    ├── start.sh
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── index.html
    │
    ├── .gitignore                        # dist/, node_modules/
    │
    ├── public/
    │   └── vite.svg
    │
    └── src/
        ├── main.tsx
        ├── App.tsx
        │
        ├── components/
        │   ├── common/
        │   │   ├── Header.tsx
        │   │   ├── Sidebar.tsx
        │   │   └── Loading.tsx
        │   │
        │   ├── dashboard/
        │   │   ├── index.ts
        │   │   ├── StatsCard.tsx
        │   │   └── QuickGuide.tsx
        │   │
        │   ├── matches/
        │   │   ├── MatchList.tsx         # Collapse/expand
        │   │   └── MatchCard.tsx         # Logo EXT (API)
        │   │
        │   ├── predictions/
        │   │   ├── PredictionPanel.tsx
        │   │   ├── PredictionCard.tsx    # Value bet %
        │   │   └── ConfidenceMeter.tsx
        │   │
        │   └── tickets/
        │       ├── TicketBuilder.tsx
        │       └── TicketHistory.tsx
        │
        ├── contexts/
        │   ├── AppContext.tsx
        │   ├── BookmakerContext.tsx
        │   ├── PredictionContext.tsx
        │   └── TicketContext.tsx
        │
        ├── hooks/
        │   └── useMatches.ts
        │
        ├── pages/
        │   ├── index.ts
        │   ├── Dashboard.tsx
        │   ├── Matches.tsx
        │   ├── Predictions.tsx
        │   └── Tickets.tsx
        │
        ├── services/
        │   ├── notificationService.ts
        │   ├── storageService.ts
        │   │
        │   └── api/
        │       ├── apiClient.ts
        │       ├── apiEndpoints.ts
        │       └── index.ts
        │
        ├── styles/
        │   └── globals.css
        │
        └── types/
            └── index.ts
```

---

## 🏭 Factory Pattern - Isolamento de Providers

### Por que Factory Pattern?

O **Factory Pattern** permite **trocar facilmente** de provider (API-Football → outro) sem impactar o domínio:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🎯 ISOLAMENTO COM FACTORY PATTERN                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1️⃣ Domain tem Interface Abstrata (ABC)                                     │
│     └─ FootballProviderInterface (não conhece API-Football!)               │
│                                                                             │
│  2️⃣ Infrastructure tem Implementações Concretas                             │
│     ├─ APIFootballProvider (implementa interface)                           │
│     └─ FootballDataProvider (implementa interface)                          │
│                                                                             │
│  3️⃣ Factory cria instância baseada em config                                │
│     └─ ProviderFactory.create(PROVIDER_TYPE)                                │
│                                                                             │
│  4️⃣ Application usa apenas a Interface                                      │
│     └─ Não sabe qual provider está usando!                                 │
│                                                                             │
│  ✅ VANTAGEM: Trocar provider = mudar 1 linha no .env                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🖼️ Lógica de Logos dos Times

### Estratégia: Local First, Provider Fallback

O sistema usa uma estratégia inteligente para logos dos times:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🎯 LÓGICA DE LOGOS (FALLBACK)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1️⃣ Verifica se existe logo LOCAL                                           │
│     └─ web_api/src/static/escudos/{team_slug}.png                          │
│                                                                             │
│  2️⃣ Se encontrar → usa LOCAL                                                │
│     └─ logo: { url: "/static/escudos/flamengo.png", type: "LOCAL" }        │
│                                                                             │
│  3️⃣ Se NÃO encontrar → usa PROVIDER                                         │
│     └─ logo: { url: "https://api.../logo.png", type: "EXTERNAL" }          │
│                                                                             │
│  ✅ VANTAGEM:                                                               │
│     • Performance (cache local)                                             │
│     • Offline-first                                                         │
│     • Fallback automático                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Domain Model: Logo

```python
# domain/models/logo_model.py

from dataclasses import dataclass
from enum import Enum

class LogoType(Enum):
    """Tipo do logo"""
    LOCAL = "LOCAL"       # Arquivo local (web_api/src/static/escudos/)
    EXTERNAL = "EXTERNAL" # URL externa (provider)

@dataclass
class Logo:
    """
    Logo de um time.
    
    Usa estratégia de fallback: Local First → Provider Fallback
    """
    url: str           # URL ou caminho relativo
    type: LogoType     # LOCAL ou EXTERNAL
    
    @staticmethod
    def local(filename: str) -> 'Logo':
        """Cria logo local"""
        return Logo(
            url=f"/static/escudos/{filename}",
            type=LogoType.LOCAL
        )
    
    @staticmethod
    def external(url: str) -> 'Logo':
        """Cria logo externo (provider)"""
        return Logo(
            url=url,
            type=LogoType.EXTERNAL
        )
```

### Domain Model: Team (com Logo)

```python
# domain/models/team_model.py

from dataclasses import dataclass
from domain.models.logo_model import Logo

@dataclass
class Team:
    """Time de futebol"""
    id: str
    name: str
    logo: Logo          # Logo com fallback automático
    country: str = None
    
    def slug(self) -> str:
        """
        Gera slug para buscar logo local.
        
        Exemplo: "Flamengo" → "flamengo.png"
                 "São Paulo" → "sao-paulo.png"
        """
        import re
        slug = self.name.lower()
        # Remove acentos
        slug = re.sub(r'[àáâãäå]', 'a', slug)
        slug = re.sub(r'[èéêë]', 'e', slug)
        slug = re.sub(r'[ìíîï]', 'i', slug)
        slug = re.sub(r'[òóôõö]', 'o', slug)
        slug = re.sub(r'[ùúûü]', 'u', slug)
        slug = re.sub(r'[ç]', 'c', slug)
        # Substitui caracteres especiais por -
        slug = re.sub(r'[^a-z0-9-]', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        return f"{slug}.png"
```

### Mapper com Fallback Automático

```python
# infrastructure/external/api_football/mappers/team_mapper.py

from pathlib import Path
from domain.models.team_model import Team
from domain.models.logo_model import Logo

class TeamMapper:
    """
    Mapeia Team da API-Football com fallback de logo.
    
    Verifica se existe logo local, senão usa do provider.
    """
    
    # Caminho dos escudos locais
    ESCUDOS_PATH = Path(__file__).parent.parent.parent.parent / "static" / "escudos"
    
    @classmethod
    def to_domain(cls, api_json: dict) -> Team:
        """
        API-Football JSON → domain.models.Team
        
        Com fallback automático de logo.
        """
        team_id = str(api_json['id'])
        team_name = api_json['name']
        provider_logo_url = api_json['logo']
        
        # Cria Team temporário para gerar slug
        temp_team = Team(
            id=team_id,
            name=team_name,
            logo=None,
            country=api_json.get('country')
        )
        
        # Gera slug do time
        slug = temp_team.slug()
        local_logo_path = cls.ESCUDOS_PATH / slug
        
        # Verifica se existe logo local
        if local_logo_path.exists():
            logo = Logo.local(slug)
        else:
            logo = Logo.external(provider_logo_url)
        
        # Retorna Team com logo correto
        return Team(
            id=team_id,
            name=team_name,
            logo=logo,
            country=temp_team.country
        )
```

### Vantagens

| Vantagem | Descrição |
|----------|-----------|
| **Performance** | Logos locais são servidos direto (sem request externa) |
| **Offline-first** | Funciona mesmo se provider estiver fora |
| **Cache automático** | Uma vez baixado, sempre disponível |
| **Fallback transparente** | Frontend não precisa saber a origem |

---

### 1. Interface Genérica (Domain)

```python
# domain/interfaces/football_provider_interface.py

from abc import ABC, abstractmethod
from domain.models.match_model import Match
from domain.models.league_model import League
from domain.models.odds_model import Odds

class FootballProviderInterface(ABC):
    """
    Interface genérica para qualquer provider de dados de futebol.
    
    Domain não conhece API-Football, FootballData, etc.
    Apenas esta interface abstrata!
    """
    
    @abstractmethod
    async def get_fixtures(self, league_id: int, date: str) -> list[Match]:
        """Retorna partidas (já mapeadas para domain.models.Match)"""
        pass
    
    @abstractmethod
    async def get_odds(self, match_id: str) -> Odds:
        """Retorna odds (já mapeadas para domain.models.Odds)"""
        pass
    
    @abstractmethod
    async def get_leagues(self) -> list[League]:
        """Retorna ligas (já mapeadas para domain.models.League)"""
        pass
```

### 2. Factory que Cria Provider

```python
# infrastructure/factories/provider_factory.py

from domain.interfaces.football_provider_interface import FootballProviderInterface
from domain.enums.provider_type_enum import ProviderType
from config.settings import settings

class ProviderFactory:
    """
    Factory que cria provider baseado em .env
    
    Para trocar de API: mudar FOOTBALL_PROVIDER no .env
    """
    
    @staticmethod
    def create() -> FootballProviderInterface:
        provider_type = settings.FOOTBALL_PROVIDER
        
        if provider_type == ProviderType.API_FOOTBALL:
            from infrastructure.external.api_football.api_football_provider import APIFootballProvider
            return APIFootballProvider()
        
        elif provider_type == ProviderType.FOOTBALL_DATA:
            from infrastructure.external.football_data.football_data_provider import FootballDataProvider
            return FootballDataProvider()
        
        raise ValueError(f"Provider desconhecido: {provider_type}")
```

### 3. Mapper (De-Para API → Domain)

```python
# infrastructure/external/api_football/mappers/fixture_to_match_mapper.py

from domain.models.match_model import Match
from domain.models.team_model import Team

class FixtureToMatchMapper:
    """
    Converte JSON da API-Football para domain.models.Match
    
    Se trocar de API, cria outro mapper!
    Domain Models não mudam.
    """
    
    @staticmethod
    def to_domain(api_json: dict) -> Match:
        """API-Football JSON → domain.models.Match"""
        
        return Match(
            id=str(api_json['fixture']['id']),
            date=api_json['fixture']['date'],
            home_team=Team(
                id=str(api_json['teams']['home']['id']),
                name=api_json['teams']['home']['name'],
                logo_url=api_json['teams']['home']['logo']
            ),
            away_team=Team(
                id=str(api_json['teams']['away']['id']),
                name=api_json['teams']['away']['name'],
                logo_url=api_json['teams']['away']['logo']
            )
        )
```

### ✅ Como Trocar de Provider

```bash
# 1. Mudar .env
# ANTES:
FOOTBALL_PROVIDER=API_FOOTBALL

# DEPOIS:
FOOTBALL_PROVIDER=FOOTBALL_DATA
```

```python
# 2. Criar novo provider
# infrastructure/external/football_data/football_data_provider.py

class FootballDataProvider(FootballProviderInterface):
    async def get_fixtures(self, league_id, date):
        # Implementação específica
        pass
```

```python
# 3. Adicionar no Factory
elif provider_type == ProviderType.FOOTBALL_DATA:
    return FootballDataProvider()
```

**PRONTO!** ✅ Domain, Application, Controllers **não mudam!**

---

### 🔑 Arquivos de Configuração

#### `web_api/src/config/.env`
```bash
# Football Provider
FOOTBALL_PROVIDER=API_FOOTBALL    # API_FOOTBALL, FOOTBALL_DATA, etc.

# API-Football
API_FOOTBALL_KEY=sua_chave_aqui
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io

# Cache TTLs (segundos)
CACHE_TTL_FIXTURES=21600    # 6 horas
CACHE_TTL_ODDS=1800          # 30 minutos
CACHE_TTL_LEAGUES=604800     # 7 dias
```

#### `web_api/src/config/.env.example` (Template)
```bash
# Football Provider (API_FOOTBALL, FOOTBALL_DATA, etc.)
FOOTBALL_PROVIDER=API_FOOTBALL

# API-Football (Obtenha sua chave em: https://www.api-football.com/)
API_FOOTBALL_KEY=your_api_key_here
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io

# Cache TTLs (segundos)
CACHE_TTL_FIXTURES=21600
CACHE_TTL_ODDS=1800
CACHE_TTL_LEAGUES=604800
```

**Nota:** O `.env` será ignorado pelo `.gitignore` global da raiz do projeto.

#### `requirements.txt`
```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0

# HTTP Client
httpx==0.26.0

# Database
sqlalchemy==2.0.25

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Utils
python-dotenv==1.0.0
```

### 📦 Componentes Principais

#### 0. **Settings** (Carrega .env)
```python
# src/config/settings.py

from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Football Provider
    FOOTBALL_PROVIDER: str = "API_FOOTBALL"
    
    # API-Football
    API_FOOTBALL_KEY: str
    API_FOOTBALL_BASE_URL: str = "https://v3.football.api-sports.io"
    
    # Cache TTLs
    CACHE_TTL_FIXTURES: int = 21600  # 6 horas
    CACHE_TTL_ODDS: int = 1800       # 30 minutos
    CACHE_TTL_LEAGUES: int = 604800  # 7 dias
    
    class Config:
        # Busca .env no mesmo diretório (src/config/.env)
        env_file = Path(__file__).parent / ".env"
        env_file_encoding = "utf-8"

# Instância global
settings = Settings()
```

#### 1. **APIFootballClient** (HTTP)
```python
# infrastructure/external/api_football/client.py

import httpx
from config.settings import settings

class APIFootballClient:
    """Cliente HTTP para API-Football"""
    
    def __init__(self):
        self.base_url = settings.API_FOOTBALL_BASE_URL
        self.headers = {
            "x-rapidapi-key": settings.API_FOOTBALL_KEY,
            "x-rapidapi-host": "v3.football.api-sports.io"
        }
    
    async def get(self, endpoint: str, params: dict = None):
        """GET request"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
```

#### 2. **APIFootballService** (Business Logic)
```python
# infrastructure/external/api_football/service.py

class APIFootballService:
    """Serviço de integração com API-Football"""
    
    def __init__(self, client, cache_manager):
        self.client = client
        self.cache = cache_manager
    
    async def get_fixtures(self, league_id: int, date: str):
        """Busca fixtures com cache (6h)"""
        cache_key = f"fixtures:{league_id}:{date}"
        
        # Cache hit
        if cached := await self.cache.get(cache_key):
            return cached
        
        # API call
        data = await self.client.get("/fixtures", {
            "league": league_id,
            "date": date
        })
        
        # Parse & Map
        fixtures = FixtureParser.parse(data)
        mapped = [FixtureMapper.to_domain(f) for f in fixtures]
        
        # Cache (6 horas)
        await self.cache.set(cache_key, mapped, ttl=21600)
        
        return mapped
    
    async def get_odds(self, fixture_id: int):
        """Busca odds com cache (30min)"""
        cache_key = f"odds:{fixture_id}"
        
        if cached := await self.cache.get(cache_key):
            return cached
        
        data = await self.client.get("/odds", {
            "fixture": fixture_id
        })
        
        odds = OddsParser.parse(data)
        mapped = OddsMapper.to_domain(odds)
        
        # Cache (30 minutos)
        await self.cache.set(cache_key, mapped, ttl=1800)
        
        return mapped
```

#### 3. **OddsAnalyzer** (Estratégias)
```python
# domain/services/odds_analyzer.py

class OddsAnalyzer:
    """Analisa odds por estratégia"""
    
    def analyze(self, match, odds_by_bookmaker, strategy):
        if strategy == "CONSERVATIVE":
            return self._conservative(odds_by_bookmaker)
        elif strategy == "VALUE_BET":
            return self._value_bet(odds_by_bookmaker)
        # ...
    
    def _conservative(self, odds):
        """Favorito seguro (1.50-2.00)"""
        # Lógica
        pass
    
    def _value_bet(self, odds):
        """Compara entre casas"""
        # Lógica
        pass
```

#### 4. **Application Services** (Camada Intermediária)

Os **Application Services** orquestram a lógica de negócio, intermediando entre **Controllers** e **Domain/Infrastructure**.

##### **MatchApplicationService**
```python
# application/services/match_application_service.py

class MatchApplicationService:
    """Serviço de aplicação para partidas"""
    
    def __init__(
        self,
        api_football_service: APIFootballService,
        match_repository: MatchRepository
    ):
        self.api_football = api_football_service
        self.match_repo = match_repository
    
    async def get_matches(self, league_id: int, date: str):
        """
        Busca partidas (orquestra API + Repository)
        """
        # 1. Busca na API-Football (com cache)
        fixtures = await self.api_football.get_fixtures(league_id, date)
        
        # 2. Enriquece com odds
        for fixture in fixtures:
            odds = await self.api_football.get_odds(fixture.id)
            fixture.odds = odds
        
        # 3. Persiste no repositório (opcional)
        # await self.match_repo.save_all(fixtures)
        
        return fixtures
    
    async def get_leagues(self):
        """Retorna ligas disponíveis"""
        return await self.api_football.get_leagues()
    
    async def get_bookmakers(self):
        """Retorna casas de apostas"""
        return await self.api_football.get_bookmakers()
```

##### **PredictionApplicationService**
```python
# application/services/prediction_application_service.py

class PredictionApplicationService:
    """Serviço de aplicação para previsões"""
    
    def __init__(
        self,
        match_application_service: MatchApplicationService,
        odds_analyzer: OddsAnalyzer,
        validators_util: ValidatorsUtil
    ):
        self.match_service = match_application_service
        self.odds_analyzer = odds_analyzer
        self.validators = validators_util
    
    async def analyze_matches(self, match_ids: list[str], strategy: str):
        """
        Analisa partidas e gera previsões
        """
        # 1. Valida entrada
        self.validators.validate_strategy(strategy)
        self.validators.validate_match_ids(match_ids)
        
        # 2. Busca dados das partidas
        matches = []
        for match_id in match_ids:
            match = await self.match_service.get_match_by_id(match_id)
            matches.append(match)
        
        # 3. Analisa com OddsAnalyzer (Domain Service)
        predictions = []
        for match in matches:
            analysis = self.odds_analyzer.analyze(
                match,
                match.odds,
                strategy
            )
            predictions.append(analysis)
        
        # 4. Cria pré-bilhete
        pre_ticket = self._create_pre_ticket(predictions)
        
        return {
            "predictions": predictions,
            "pre_ticket": pre_ticket
        }
    
    def _create_pre_ticket(self, predictions):
        """Cria pré-bilhete com melhores apostas"""
        # Lógica de criação
        pass
```

##### **TicketApplicationService**
```python
# application/services/ticket_application_service.py

class TicketApplicationService:
    """Serviço de aplicação para bilhetes"""
    
    def __init__(
        self,
        ticket_repository: TicketRepository,
        calculators_util: CalculatorsUtil
    ):
        self.ticket_repo = ticket_repository
        self.calculators = calculators_util
    
    async def create_ticket(self, name: str, stake: float, bets: list):
        """
        Cria um novo bilhete
        """
        # 1. Calcula odds combinadas
        total_odds = self.calculators.calculate_combined_odds(bets)
        
        # 2. Calcula retorno potencial
        potential_return = self.calculators.calculate_return(stake, total_odds)
        
        # 3. Cria entidade de domínio
        ticket = Ticket(
            name=name,
            stake=stake,
            total_odds=total_odds,
            potential_return=potential_return,
            bets=bets,
            status="PENDING"
        )
        
        # 4. Persiste no repositório
        saved_ticket = await self.ticket_repo.save(ticket)
        
        return saved_ticket
    
    async def get_all_tickets(self):
        """Lista todos os bilhetes"""
        return await self.ticket_repo.find_all()
    
    async def get_dashboard_stats(self):
        """Retorna estatísticas do dashboard"""
        tickets = await self.ticket_repo.find_all()
        
        stats = {
            "total_tickets": len(tickets),
            "won_tickets": len([t for t in tickets if t.status == "WON"]),
            "lost_tickets": len([t for t in tickets if t.status == "LOST"]),
            "pending_tickets": len([t for t in tickets if t.status == "PENDING"]),
        }
        
        # Calcula taxa de sucesso
        finished = stats["won_tickets"] + stats["lost_tickets"]
        if finished > 0:
            stats["success_rate"] = (stats["won_tickets"] / finished) * 100
        else:
            stats["success_rate"] = 0
        
        return stats
```

#### 5. **Domain Utils** (Utilitários)

Os **Utils** contêm funções auxiliares reutilizáveis. **Todos devem terminar com `_util.py`**.

##### **ValidatorsUtil**
```python
# domain/utils/validators_util.py

class ValidatorsUtil:
    """Validações de domínio"""
    
    @staticmethod
    def validate_strategy(strategy: str):
        """Valida estratégia"""
        valid_strategies = ["CONSERVATIVE", "VALUE_BET", "BALANCED", "AGGRESSIVE"]
        if strategy not in valid_strategies:
            raise ValueError(f"Estratégia inválida: {strategy}")
    
    @staticmethod
    def validate_match_ids(match_ids: list):
        """Valida lista de IDs"""
        if not match_ids or len(match_ids) == 0:
            raise ValueError("Lista de partidas vazia")
        
        if len(match_ids) > 10:
            raise ValueError("Máximo 10 partidas por análise")
    
    @staticmethod
    def validate_stake(stake: float):
        """Valida valor da aposta"""
        if stake <= 0:
            raise ValueError("Stake deve ser maior que zero")
        
        if stake > 10000:
            raise ValueError("Stake máximo: R$ 10.000")
```

##### **CalculatorsUtil**
```python
# domain/utils/calculators_util.py

class CalculatorsUtil:
    """Cálculos de domínio"""
    
    @staticmethod
    def calculate_combined_odds(bets: list) -> float:
        """Calcula odds combinadas (multiplicação)"""
        combined = 1.0
        for bet in bets:
            combined *= bet['odd']
        return round(combined, 2)
    
    @staticmethod
    def calculate_return(stake: float, odds: float) -> float:
        """Calcula retorno potencial"""
        return round(stake * odds, 2)
    
    @staticmethod
    def calculate_profit(stake: float, return_value: float) -> float:
        """Calcula lucro"""
        return round(return_value - stake, 2)
    
    @staticmethod
    def calculate_confidence_from_odd(odd: float) -> float:
        """Calcula confiança a partir da odd"""
        implied_prob = (1 / odd) * 100
        adjusted = implied_prob * 1.06  # Remove margem ~6%
        return max(10, min(90, adjusted))
```

##### **FormattersUtil**
```python
# domain/utils/formatters_util.py

from datetime import datetime

class FormattersUtil:
    """Formatadores de dados"""
    
    @staticmethod
    def format_currency(value: float) -> str:
        """Formata para moeda brasileira"""
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Formata porcentagem"""
        return f"{value:.2f}%"
    
    @staticmethod
    def format_date_br(date: datetime) -> str:
        """Formata data para padrão brasileiro"""
        return date.strftime("%d/%m/%Y %H:%M")
    
    @staticmethod
    def format_odds(odd: float) -> str:
        """Formata odd"""
        return f"{odd:.2f}"
```

---

### 📊 Fluxo Completo com Application Services

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🔄 FLUXO DE DADOS COMPLETO                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1️⃣ Controller (Web Layer)                                                  │
│     ├─ Recebe HTTP Request                                                  │
│     ├─ Valida DTO (Pydantic)                                                │
│     └─ Chama Application Service                                            │
│                                                                             │
│  2️⃣ Application Service (Orquestração)                                      │
│     ├─ Valida regras de negócio (Validators Util)                           │
│     ├─ Chama Domain Services                                                │
│     ├─ Chama Repositories                                                   │
│     ├─ Chama Infrastructure Services (API-Football)                         │
│     ├─ Usa Utils para cálculos (Calculators Util)                           │
│     └─ Retorna resultado                                                    │
│                                                                             │
│  3️⃣ Domain Service (Lógica de Negócio)                                      │
│     ├─ Aplica estratégias                                                   │
│     ├─ Analisa odds                                                         │
│     └─ Retorna análise                                                      │
│                                                                             │
│  4️⃣ Infrastructure (Acesso a Dados)                                         │
│     ├─ APIFootballService → API-Football                                    │
│     ├─ Repository → SQLite                                                  │
│     └─ CacheManager → Cache                                                 │
│                                                                             │
│  5️⃣ Controller (resposta)                                                   │
│     ├─ Mapeia para DTO Response                                             │
│     └─ Retorna HTTP Response                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 🎯 Exemplo Prático

```python
# web/controllers/prediction_controller.py

@router.post("/analyze")
async def analyze_matches(
    request: AnalyzeRequest,
    prediction_service: PredictionApplicationService = Depends()
):
    """Controller delega para Application Service"""
    
    result = await prediction_service.analyze_matches(
        match_ids=request.match_ids,
        strategy=request.strategy
    )
    
    return result
```

---
```python
# infrastructure/cache/cache_manager.py

class CacheManager:
    """Gerencia cache com TTL"""
    
    async def get(self, key: str):
        """Busca no cache"""
        item = db.query(Cache).filter_by(key=key).first()
        
        if not item or datetime.now() > item.expires_at:
            return None
        
        return json.loads(item.data)
    
    async def set(self, key: str, data, ttl: int):
        """Salva no cache"""
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        cache = Cache(
            key=key,
            data=json.dumps(data),
            expires_at=expires_at
        )
        
        db.merge(cache)
        db.commit()
```

### 🗄️ Schema do Banco (SQLite)

```sql
-- Cache da API-Football
CREATE TABLE api_cache (
    key TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cache_expires ON api_cache(expires_at);

-- Bilhetes
CREATE TABLE tickets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    bookmaker_id TEXT NOT NULL,
    stake REAL NOT NULL,
    total_odds REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Apostas
CREATE TABLE ticket_bets (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    fixture_id TEXT NOT NULL,
    match_name TEXT NOT NULL,
    market_type TEXT NOT NULL,
    prediction TEXT NOT NULL,
    odd REAL NOT NULL,
    status TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);
```

### 🚀 Fluxo de Implementação

```
1️⃣ Criar web_api/src/config/.env com API_FOOTBALL_KEY
2️⃣ Criar web_api/src/config/.env.example (template)
3️⃣ Atualizar .gitignore da raiz (*.env)
4️⃣ Estrutura de pastas (domain, infrastructure)
5️⃣ APIFootballClient (httpx)
6️⃣ CacheManager (SQLite)
7️⃣ Parsers (fixture, odds, league)
8️⃣ Mappers (API → Domain)
9️⃣ APIFootballService
🔟 OddsAnalyzer (estratégias)
1️⃣1️⃣ Pré-carregamento de Ligas (startup)
1️⃣2️⃣ Atualizar Controllers
1️⃣3️⃣ Frontend (logo.type = EXT)
```

### ⚡ Pré-carregamento de Ligas Principais

**Executado automaticamente ao iniciar o backend (1x por dia):**

**COM PRO PLAN (7.500 req/dia):**

```python
# web_api/src/main.py

@app.on_event("startup")
async def preload_main_leagues():
    """
    Pré-carrega fixtures das ligas principais ao iniciar.
    
    PRO PLAN (7.500 req/dia): Carrega HOJE até DOMINGO (semana completa).
    
    Executa apenas se não houver carga do dia atual no cache.
    """
    from application.services.preload_service import PreloadService
    
    preload_service = PreloadService()
    
    # Verifica se já tem carga de hoje
    if await preload_service.has_todays_cache():
        logger.info("✅ Cache do dia já existe. Pré-carregamento ignorado.")
        return
    
    logger.info("🚀 Iniciando pré-carregamento de ligas principais...")
    logger.info("📅 Período: Hoje até Domingo (até 7 dias)")
    
    # Pré-carrega 7 ligas × 7 dias
    await preload_service.preload_fixtures([
        # Brasil
        71,   # Brasileirão Série A
        73,   # Copa do Brasil
        
        # Europa - Top 5 Leagues
        39,   # Premier League (Inglaterra)
        140,  # La Liga (Espanha)
        78,   # Bundesliga (Alemanha)
        61,   # Ligue 1 (França)
        135   # Serie A (Itália)
    ])
    
    logger.info("✅ Pré-carregamento concluído! 7 ligas da semana prontas.")
```

**Benefícios:**
- ✅ **Semana completa de 7 ligas** pré-carregada
- ✅ **~224 requests usados** no startup (2,99% do limite PRO)
- ✅ **Cache válido** até meia-noite de cada dia
- ✅ **Não recarrega** se já tiver dados do dia
- ✅ **Sobra 7.276 requests** para uso normal (97,01%)

**Impacto em Requests (PRO PLAN - 7.500 req/dia):**
```
Pré-carregamento (startup):
- 7 ligas × 7 dias = 49 req (fixtures)
- ~25 jogos/dia × 7 dias = ~175 jogos
- 175 jogos = ~175 req (odds)
- TOTAL: ~224 req (2,99% do limite diário)

Usuário acessa:
- Fixtures: 0 req (cache hit)
- Odds: 0 req (cache hit)
- Total: 0 req ✅

Cobertura:
- 🇧🇷 Brasil: Brasileirão + Copa do Brasil
- 🇪🇺 Europa: Premier, La Liga, Bundesliga, Ligue 1, Serie A
- 📅 Período: Toda a semana (hoje até domingo)

Economia vs Free Plan:
- Free Plan: 100 req/dia (224 req = inviável)
- PRO Plan: 7.500 req/dia (224 req = 2,99%)
- Sobra PRO: 7.276 requests (97,01% disponíveis)
```

**Fórmula de Requests:**
```
Total = (ligas × dias_até_domingo) + (jogos_totais)
Total = (7 × 7) + (~175) ≈ 224 requests
Percentual = 224 / 7.500 = 2,99%
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

## 🧠 Lógica de Análise

### Análise Inteligente Baseada em Odds

O sistema **não usa IA/ML complexa**, mas aplica **lógica inteligente** sobre as odds da API-Football:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🎯 COMO FUNCIONA A ANÁLISE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1️⃣ COLETA DE DADOS                                                         │
│     API-Football → Fixtures + Odds de múltiplas casas                       │
│                                                                             │
│  2️⃣ ANÁLISE POR ESTRATÉGIA                                                  │
│     Aplica regras baseadas na estratégia escolhida                          │
│                                                                             │
│  3️⃣ COMPARAÇÃO ENTRE CASAS                                                  │
│     Identifica discrepâncias de odds entre Bet365, Betano, etc.             │
│                                                                             │
│  4️⃣ CÁLCULO DE VALUE BET                                                    │
│     Compara odds entre casas para encontrar oportunidades                   │
│                                                                             │
│  5️⃣ RECOMENDAÇÃO FINAL                                                      │
│     Sugere a melhor aposta baseada na estratégia + value bet                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Estratégias de Análise

#### 1️⃣ CONSERVATIVE (Conservadora)
```python
def analyze_conservative(match, odds):
    """
    Foca em apostas seguras (favoritos com odd razoável)
    """
    # Identifica o favorito (menor odd)
    favorite = min(odds['1X2'], key=odds['1X2'].get)
    favorite_odd = odds['1X2'][favorite]
    
    # Regras:
    # - Odd do favorito >= 1.50 (não muito baixa)
    # - Odd do favorito <= 2.00 (não arriscado)
    if 1.50 <= favorite_odd <= 2.00:
        confidence = calculate_confidence_from_odd(favorite_odd)
        return {
            "prediction": favorite,
            "odd": favorite_odd,
            "confidence": confidence,
            "reason": "Favorito com odd razoável e segura"
        }
    
    return None  # Não recomenda se fora dos critérios
```

**Características:**
- ✅ Foco em favoritos
- ✅ Odds entre 1.50 e 2.00
- ✅ Menor risco
- ✅ Retorno moderado

#### 2️⃣ VALUE_BET (Foco em Value)
```python
def analyze_value_bet(match, odds_by_bookmaker):
    """
    Procura discrepâncias entre casas de apostas
    """
    value_bets = []
    
    # Compara odds de cada mercado entre casas
    for market in ['1X2', 'OVER_UNDER', 'BTTS']:
        for outcome in market_outcomes:
            odds_comparison = {}
            
            # Coleta odds de cada casa
            for bookmaker, odds in odds_by_bookmaker.items():
                odds_comparison[bookmaker] = odds[market][outcome]
            
            # Identifica melhor odd
            best_bookmaker = max(odds_comparison, key=odds_comparison.get)
            best_odd = odds_comparison[best_bookmaker]
            avg_odd = sum(odds_comparison.values()) / len(odds_comparison)
            
            # Calcula value bet %
            value_percentage = ((best_odd - avg_odd) / avg_odd) * 100
            
            # Se value >= 5%, é uma oportunidade
            if value_percentage >= 5.0:
                value_bets.append({
                    "market": market,
                    "outcome": outcome,
                    "best_bookmaker": best_bookmaker,
                    "best_odd": best_odd,
                    "avg_odd": avg_odd,
                    "value_percentage": value_percentage,
                    "confidence": calculate_confidence_from_value(value_percentage)
                })
    
    # Ordena por maior value
    return sorted(value_bets, key=lambda x: x['value_percentage'], reverse=True)
```

**Características:**
- ✅ Compara todas as casas
- ✅ Identifica discrepâncias >= 5%
- ✅ Melhor value = melhor retorno esperado
- ✅ Risco variável

#### 3️⃣ BALANCED (Balanceada)
```python
def analyze_balanced(match, odds_by_bookmaker):
    """
    Balanceia segurança (favorito) com value bet
    """
    # Análise conservadora
    conservative_bet = analyze_conservative(match, odds_by_bookmaker['bet365'])
    
    # Análise de value
    value_bets = analyze_value_bet(match, odds_by_bookmaker)
    
    # Combina: favorito com value razoável
    if conservative_bet and value_bets:
        # Prioriza favorito SE também tem value
        for vb in value_bets:
            if vb['outcome'] == conservative_bet['prediction'] and vb['value_percentage'] >= 3:
                return {
                    **conservative_bet,
                    "value_percentage": vb['value_percentage'],
                    "best_bookmaker": vb['best_bookmaker'],
                    "reason": "Favorito seguro COM value bet"
                }
        
        # Se não, pega melhor value com odd razoável (1.70-3.00)
        for vb in value_bets:
            if 1.70 <= vb['best_odd'] <= 3.00:
                return {
                    "prediction": vb['outcome'],
                    "odd": vb['best_odd'],
                    "confidence": vb['confidence'],
                    "value_percentage": vb['value_percentage'],
                    "best_bookmaker": vb['best_bookmaker'],
                    "reason": "Boa odd com value bet"
                }
    
    # Fallback: conservadora
    return conservative_bet
```

**Características:**
- ✅ Melhor dos dois mundos
- ✅ Segurança + Value
- ✅ Risco moderado
- ✅ Retorno equilibrado

#### 4️⃣ AGGRESSIVE (Agressiva)
```python
def analyze_aggressive(match, odds_by_bookmaker):
    """
    Foca em odds altas (zebras) com maior value
    """
    aggressive_bets = []
    
    for bookmaker, odds in odds_by_bookmaker.items():
        for market, outcomes in odds.items():
            for outcome, odd in outcomes.items():
                # Busca odds >= 2.50 (zebras)
                if odd >= 2.50:
                    # Calcula probabilidade implícita
                    implied_prob = (1 / odd) * 100
                    
                    # Confiança ajustada (menor para zebras)
                    confidence = implied_prob * 0.8  # 20% de desconto
                    
                    aggressive_bets.append({
                        "market": market,
                        "outcome": outcome,
                        "bookmaker": bookmaker,
                        "odd": odd,
                        "confidence": confidence,
                        "implied_probability": implied_prob,
                        "reason": "Odd alta com potencial retorno elevado"
                    })
    
    # Ordena por maior odd (maior retorno)
    return sorted(aggressive_bets, key=lambda x: x['odd'], reverse=True)
```

**Características:**
- ✅ Odds >= 2.50
- ✅ Foco em zebras/underdogs
- ✅ Alto risco
- ✅ Alto retorno potencial

### Cálculo de Confiança (Sem IA)

```python
def calculate_confidence_from_odd(odd: float) -> float:
    """
    Calcula confiança baseada na odd (probabilidade implícita)
    
    Odd 1.50 → 66.7% de confiança
    Odd 2.00 → 50.0% de confiança
    Odd 3.00 → 33.3% de confiança
    """
    implied_probability = (1 / odd) * 100
    
    # Ajusta para remover margem da casa (~5-8%)
    # Assume 6% de margem
    adjusted_probability = implied_probability * 1.06
    
    # Limita entre 10% e 90%
    return max(10, min(90, adjusted_probability))
```

### Identificação de Value Bet

```python
def calculate_value_bet(odds_by_bookmaker, market, outcome):
    """
    Calcula value bet comparando odds entre casas
    
    Value Bet % = ((Melhor Odd - Média Odds) / Média Odds) × 100
    
    Exemplo:
    - Bet365: 2.10
    - Betano: 2.15
    - Média: 2.125
    - Value: ((2.15 - 2.125) / 2.125) × 100 = +1.18%
    """
    odds_list = []
    
    for bookmaker, odds in odds_by_bookmaker.items():
        if market in odds and outcome in odds[market]:
            odds_list.append(odds[market][outcome])
    
    if len(odds_list) < 2:
        return {"value_percentage": 0, "best_bookmaker": None}
    
    best_odd = max(odds_list)
    avg_odd = sum(odds_list) / len(odds_list)
    value_percentage = ((best_odd - avg_odd) / avg_odd) * 100
    
    best_bookmaker = next(
        bm for bm, odds in odds_by_bookmaker.items()
        if odds[market][outcome] == best_odd
    )
    
    return {
        "best_odd": best_odd,
        "avg_odd": avg_odd,
        "value_percentage": round(value_percentage, 2),
        "best_bookmaker": best_bookmaker,
        "has_value": value_percentage > 0
    }
```

### Resumo da Lógica

| Estratégia | Foco | Odd Range | Risco | Retorno |
|------------|------|-----------|-------|---------|
| **CONSERVATIVE** | Favoritos | 1.50-2.00 | Baixo | Moderado |
| **VALUE_BET** | Discrepâncias | Variável | Médio | Bom |
| **BALANCED** | Favorito + Value | 1.70-3.00 | Médio | Equilibrado |
| **AGGRESSIVE** | Zebras | >= 2.50 | Alto | Alto |

**Vantagens desta Abordagem:**
- ✅ Sem necessidade de IA/ML
- ✅ Dados 100% reais da API-Football
- ✅ Lógica clara e transparente
- ✅ Implementação rápida (1 semana)
- ✅ Manutenção zero
- ✅ Value bets reais (comparação entre casas)

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

### Fase 1: Integração com API-Football ⏳

#### Setup Inicial
- [ ] Criar `web_api/src/config/.env` com API_FOOTBALL_KEY
- [ ] Criar `web_api/src/config/.env.example` (template para outros devs)
- [ ] Atualizar `.gitignore` da raiz para incluir `*.env`

#### Backend
- [ ] Implementar `settings.py` para carregar .env
- [ ] Implementar cliente HTTP para API-Football
- [ ] Sistema de cache com TTL por tipo de dado
- [ ] Parser de fixtures da API
- [ ] Parser de odds de múltiplas casas
- [ ] Mapeamento de ligas e times reais
- [ ] Tratamento de rate limits (100 req/dia)

#### Estrutura de Cache
```python
# infrastructure/cache/api_football_cache.py

class APIFootballCache:
    def __init__(self):
        self.cache = {}  # Em memória por enquanto
    
    async def get_fixtures(self, league_id: int, date: str):
        """Cache de 6 horas"""
        cache_key = f"fixtures:{league_id}:{date}"
        
        if self.is_valid(cache_key, ttl=6*60*60):
            return self.cache[cache_key]
        
        # Busca na API
        data = await api_football_client.get_fixtures(league_id, date)
        self.cache[cache_key] = {
            "data": data,
            "expires_at": datetime.now() + timedelta(hours=6)
        }
        return data
    
    async def get_odds(self, fixture_id: int):
        """Cache de 30 minutos"""
        cache_key = f"odds:{fixture_id}"
        
        if self.is_valid(cache_key, ttl=30*60):
            return self.cache[cache_key]
        
        # Busca na API
        data = await api_football_client.get_odds(fixture_id)
        self.cache[cache_key] = {
            "data": data,
            "expires_at": datetime.now() + timedelta(minutes=30)
        }
        return data
```

#### TTLs Recomendados
| Tipo de Dado | TTL | Justificativa |
|--------------|-----|---------------|
| Fixtures | 6 horas | Horários não mudam frequentemente |
| Odds | 30 minutos | Mudam constantemente |
| Ligas | 7 dias | Não mudam |
| Bookmakers | 24 horas | Raramente mudam |

### Fase 2: Lógica de Análise ⏳

#### Implementar Estratégias
- [ ] Conservative (favoritos seguros)
- [ ] Value Bet (comparação entre casas)
- [ ] Balanced (favorito + value)
- [ ] Aggressive (odds altas)

#### Exemplo de Implementação
```python
# domain/services/odds_analyzer.py

class OddsAnalyzer:
    def analyze(self, match, odds_by_bookmaker, strategy):
        """Analisa match baseado na estratégia"""
        
        if strategy == "CONSERVATIVE":
            return self._analyze_conservative(match, odds_by_bookmaker)
        
        elif strategy == "VALUE_BET":
            return self._analyze_value_bet(match, odds_by_bookmaker)
        
        elif strategy == "BALANCED":
            return self._analyze_balanced(match, odds_by_bookmaker)
        
        elif strategy == "AGGRESSIVE":
            return self._analyze_aggressive(match, odds_by_bookmaker)
    
    def _analyze_conservative(self, match, odds):
        # Implementação da lógica conservadora
        pass
    
    def _analyze_value_bet(self, match, odds):
        # Implementação da comparação entre casas
        pass
```

### Fase 3: Melhorias UX 🎨

- [ ] Explicação detalhada das recomendações
- [ ] Comparação visual de odds entre casas
- [ ] Gráficos de histórico de value bets encontrados
- [ ] Filtros avançados (por odds, value %, etc.)
- [ ] Modo escuro/claro
- [ ] Export de bilhetes (PDF/Imagem)
- [ ] Notificações de novos jogos/odds

### Fase 4: Banco de Dados 💾

- [ ] Migrar de mock para SQLite
- [ ] Persistir bilhetes criados
- [ ] Histórico de apostas
- [ ] Estatísticas de acerto por estratégia
- [ ] Logs de uso da API-Football

#### Schema Básico
```sql
-- Bilhetes
CREATE TABLE tickets (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    bookmaker_id TEXT NOT NULL,
    stake REAL NOT NULL,
    total_odds REAL NOT NULL,
    potential_return REAL NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Apostas do bilhete
CREATE TABLE ticket_bets (
    id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    match_id TEXT NOT NULL,
    match_name TEXT NOT NULL,
    market_type TEXT NOT NULL,
    prediction TEXT NOT NULL,
    odd REAL NOT NULL,
    confidence REAL NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);

-- Cache da API-Football
CREATE TABLE api_cache (
    cache_key TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_expires_at ON api_cache(expires_at);
```

### Fase 5: Melhorias Futuras (Opcional) 🚀

#### Estatísticas Simples (Sem IA)
Se quiser adicionar mais inteligência **SEM IA complexa**:

```python
# Usar apenas dados da própria API-Football
def get_team_simple_stats(team_id):
    """Busca estatísticas básicas do time"""
    fixtures = api_football.get_team_fixtures(team_id, last=5)
    
    stats = {
        "wins": sum(1 for f in fixtures if f.winner == team_id),
        "draws": sum(1 for f in fixtures if f.winner is None),
        "losses": sum(1 for f in fixtures if f.winner != team_id),
        "goals_scored": sum(f.goals_for for f in fixtures),
        "goals_conceded": sum(f.goals_against for f in fixtures)
    }
    
    # Forma recente (simples)
    stats["form_percentage"] = (stats["wins"] * 3 + stats["draws"]) / 15 * 100
    
    return stats

# Usar na análise
def analyze_with_basic_stats(match, odds, strategy):
    """Análise + estatísticas básicas"""
    base_analysis = analyze(match, odds, strategy)
    
    home_stats = get_team_simple_stats(match.home_team.id)
    away_stats = get_team_simple_stats(match.away_team.id)
    
    # Ajusta confiança baseado em forma
    if home_stats["form_percentage"] > 70:
        base_analysis["confidence"] += 5
    if away_stats["form_percentage"] < 30:
        base_analysis["confidence"] += 5
    
    base_analysis["reasoning"] = f"""
    Forma {match.home_team.name}: {home_stats["form_percentage"]}%
    Forma {match.away_team.name}: {away_stats["form_percentage"]}%
    """
    
    return base_analysis
```

**Vantagens:**
- ✅ Usa dados reais da API-Football
- ✅ Sem treinamento de modelos
- ✅ Adiciona contexto às recomendações
- ✅ Implementação simples

---

## 📊 Cronograma Estimado

| Fase | Descrição | Tempo Estimado | Prioridade |
|------|-----------|----------------|------------|
| **Fase 1** | Integração API-Football | 1 semana | 🔴 Alta |
| **Fase 2** | Lógica de Análise | 3-4 dias | 🔴 Alta |
| **Fase 3** | Melhorias UX | 1 semana | 🟡 Média |
| **Fase 4** | Banco de Dados | 3-4 dias | 🟡 Média |
| **Fase 5** | Stats Básicas | 2-3 dias | 🟢 Baixa |

**Total (MVP funcional):** 2-3 semanas

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

O sistema está **implementado** com frontend e backend funcionais, incluindo:

✅ Frontend totalmente funcional  
✅ Backend com controllers mockados  
✅ Estrutura de dados bem definida  
✅ Fluxo de usuário completo  
✅ Visual profissional  
✅ Pronto para integração com API-Football  
✅ Pronto para implementação dos modelos de IA  

**Próximo passo:** Integrar API-Football e implementar cache! 🚀

