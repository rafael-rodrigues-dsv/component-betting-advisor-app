# 🎰 Betting Bot - Arquitetura do Sistema

> Sistema de sugestão de bilhetes de apostas esportivas usando IA

**Data:** 2026-02-14  
**Versão:** 1.0.0

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Decisões Técnicas](#decisões-técnicas)
3. [Arquitetura N-Camadas](#arquitetura-n-camadas)
4. [Estrutura de Pastas](#estrutura-de-pastas)
5. [Fluxo de Dados](#fluxo-de-dados)
6. [Interfaces e Contratos](#interfaces-e-contratos)
7. [Padrões de Projeto](#padrões-de-projeto)
8. [Componentes](#componentes)
9. [Regras de Dependência](#regras-de-dependência)

---

## 🎯 Visão Geral

Sistema que analisa dados esportivos e gera sugestões de apostas inteligentes usando **IA/ML**, utilizando a **API-Football** como fonte principal de dados (estatísticas + odds).

### Características Principais

- **Esporte:** Futebol
- **Fonte de Dados:** API-Football (estatísticas + odds de múltiplas casas)
- **Análise:** Modelos estatísticos (Poisson) e Machine Learning (XGBoost)
- **Interface:** React Web Application

---

## 🌐 API-Football - Fonte de Dados

### Sobre a API

A **API-Football** é uma API REST que fornece dados completos de futebol, incluindo estatísticas e odds de várias casas de apostas.

| Item | Detalhe |
|------|---------|
| **URL Base** | https://api-football-v1.p.rapidapi.com/v3 |
| **Documentação** | https://www.api-football.com/documentation-v3 |
| **Autenticação** | API Key via header `x-rapidapi-key` |

### Plano Gratuito

| Recurso | Limite |
|---------|--------|
| **Requests** | 100 por dia |
| **Rate Limit** | 30 requests por minuto |
| **Cobertura** | 900+ ligas e copas |
| **Histórico** | Últimas 2 temporadas |

### Endpoints Utilizados

| Endpoint | Descrição | Uso no Sistema |
|----------|-----------|----------------|
| `GET /fixtures` | Lista partidas por data/liga | Buscar jogos do dia |
| `GET /fixtures/statistics` | Estatísticas da partida | Análise detalhada |
| `GET /teams/statistics` | Estatísticas do time na temporada | Input para IA |
| `GET /fixtures/headtohead` | Histórico de confrontos | Análise H2H |
| `GET /odds` | Odds de várias casas de apostas | Buscar odds |
| `GET /odds/bookmakers` | Lista casas disponíveis | Configuração |
| `GET /predictions` | Previsões da própria API | Comparação |

### Casas de Apostas Disponíveis (via API)

A API-Football fornece odds das seguintes casas (entre outras):

- Bet365
- Betfair
- 1xBet
- Pinnacle
- Betano
- Sportingbet
- William Hill
- Unibet

### Exemplo de Response - Odds

```json
{
  "league": { "id": 39, "name": "Premier League" },
  "fixture": { "id": 123456 },
  "bookmakers": [
    {
      "id": 6,
      "name": "Bet365",
      "bets": [
        {
          "name": "Match Winner",
          "values": [
            { "value": "Home", "odd": "2.10" },
            { "value": "Draw", "odd": "3.40" },
            { "value": "Away", "odd": "3.20" }
          ]
        }
      ]
    }
  ]
}
```

---

## ⚙️ Decisões Técnicas

| Aspecto | Decisão |
|---------|---------|
| **Arquitetura** | N-Camadas (Layered Architecture) |
| **Padrão de Criação** | Factory Pattern |
| **Banco de Dados** | SQLite (auto-init no startup) |
| **Cache API-Football** | SQLite com TTL diferenciado por tipo de dado |
| **Execução** | Sob demanda (usuário trigger) |
| **Frontend** | React (Vite + TypeScript) |
| **Backend** | Python + FastAPI |
| **Comunicação** | REST API |
| **Acesso entre Camadas** | Via Interfaces (Inversão de Dependência) |

---

## 🏗️ Arquitetura N-Camadas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              BETTING BOT - N-LAYER + DEPENDENCY INVERSION                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         WEB LAYER                                    │   │
│  │                                                                      │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐  │   │
│  │  │   React     │    │ Controllers │    │      DTOs/Schemas       │  │   │
│  │  │   Web App   │───▶│  (Routes)   │───▶│  (Request/Response)     │  │   │
│  │  └─────────────┘    └──────┬──────┘    └───────────┬─────────────┘  │   │
│  │                            │                       │                 │   │
│  │                            │            DTO ──▶ Domain Model         │   │
│  │                            │              (Conversão via Mapper)     │   │
│  └────────────────────────────┼─────────────────────────────────────────┘   │
│                               │                                             │
│                               ▼ via Contracts                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      APPLICATION LAYER                               │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │              contracts/ (Service Contracts)                  │    │   │
│  │  │  MatchServiceContract │ PredictionServiceContract │ ...     │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │                               ▲                                      │   │
│  │                               │ implements                           │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    impl/ (Implementations)                   │    │   │
│  │  │  MatchServiceImpl │ PredictionServiceImpl │ TicketServiceImpl│   │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────┬──────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼ via Domain Contracts                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        DOMAIN LAYER                                  │   │
│  │                   (ZERO dependências externas)                       │   │
│  │                                                                      │   │
│  │  ┌───────────────────────────────────────────────────────────────┐  │   │
│  │  │                 contracts/ (Domain Contracts)                  │  │   │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐  │  │   │
│  │  │  │ Platform    │ │ DataSource  │ │ Analyzer                │  │  │   │
│  │  │  │ Contract    │ │ Contract    │ │ Contract                │  │  │   │
│  │  │  └─────────────┘ └─────────────┘ └─────────────────────────┘  │  │   │
│  │  │  ┌─────────────┐ ┌─────────────┐                              │  │   │
│  │  │  │ Repository  │ │  Factory    │                              │  │   │
│  │  │  │ Contract    │ │  Contract   │                              │  │   │
│  │  │  └─────────────┘ └─────────────┘                              │  │   │
│  │  └───────────────────────────────────────────────────────────────┘  │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────────────────────────────────┐    │   │
│  │  │   models/    │  │              services/                    │    │   │
│  │  │  (Entities)  │  │   contracts/ + impl/ (Domain Services)   │    │   │
│  │  └──────────────┘  └──────────────────────────────────────────┘    │   │
│  │                                                                      │   │
│  │  ┌──────────────┐  ┌──────────────────────────────────────────┐    │   │
│  │  │   utils/     │  │              factories/                   │    │   │
│  │  │              │  │   contracts/ + impl/ (Factory Pattern)   │    │   │
│  │  └──────────────┘  └──────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                 ▲                                           │
│                                 │ Implementa Contracts                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INFRASTRUCTURE LAYER                              │   │
│  │               (Implementações concretas dos Contracts)               │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  database/repositories/                                      │   │   │
│  │  │    contracts/ + impl/ (Repository Implementations)           │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  external/                                                   │   │   │
│  │  │    platforms/bet365/ (PlatformContract impl)                │   │   │
│  │  │    data_sources/sofascore/ (DataSourceContract impl)        │   │   │
│  │  │    analyzers/ (AnalyzerContract impl)                       │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────────────────┐  │   │
│  │  │   config/       │  │   container.py (DI Container)          │  │   │
│  │  └─────────────────┘  └─────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Pastas

```
betting-bot/
│
├── main.py                               # 🚀 Entry point (inicia API + React)
├── start.bat                             # 🪟 Script Windows para iniciar o sistema
├── start.sh                              # 🐧 Script Linux/Mac para iniciar o sistema
├── requirements.txt                      # Dependências Python
├── README.md                             # Documentação inicial
│
├── .venv/                                # 🐍 Ambiente virtual Python (criado pelo start)
│
├── .cache/                               # 📦 Cache local (não commitar)
│   ├── pip/                              # Cache de pacotes pip (evita re-download)
│   └── python/                           # Instalador Python 3.14 (Windows)
│
├── docs/                                 # 📚 Documentação
│   ├── ARQUITETURA.md
│   ├── FLUXO_FUNCIONAL.md
│   └── MODELO_IA.md
│
├── data/                                 # 💾 Banco de Dados e Dados (RAIZ)
│   ├── betting.db                        # Banco SQLite ÚNICO (criado pelo init)
│   │
│   ├── scripts/                          # Scripts de inicialização do DB
│   │   ├── __init__.py
│   │   └── init_database.py              # Cria banco se não existir (chamado pela main)
│   │
│   ├── raw/                              # Dados brutos
│   │   ├── football-data/                # CSVs do Football-Data.co.uk
│   │   │   ├── england/                  # Premier League, Championship
│   │   │   ├── spain/                    # La Liga
│   │   │   ├── italy/                    # Serie A
│   │   │   ├── germany/                  # Bundesliga
│   │   │   └── france/                   # Ligue 1
│   │   │
│   │   └── api_football/                 # Dados coletados da API
│   │       └── collected_matches.json
│   │
│   ├── processed/                        # Dados processados
│   │   ├── training_dataset.parquet      # Dataset final para treino
│   │   └── feature_stats.json            # Estatísticas normalização
│   │
│   └── models/                           # Modelos de ML
│       ├── xgboost_model.pkl             # Modelo em produção
│       ├── scaler.pkl                    # Normalizador
│       ├── model_metadata.json           # Métricas e versão
│       └── archive/                      # Versões anteriores
│
├── src/                                  # 📦 Código fonte
│   ├── __init__.py
│   │
│   ├── web/                              # 🌐 WEB LAYER
│   │   ├── __init__.py
│   │   │
│   │   ├── controllers/                  # API Controllers (Routes)
│   │   │   ├── __init__.py
│   │   │   ├── platform_controller.py
│   │   │   ├── match_controller.py
│   │   │   ├── prediction_controller.py
│   │   │   └── ticket_controller.py
│   │   │
│   │   ├── dtos/                         # DTOs (Request/Response)
│   │   │   ├── __init__.py
│   │   │   ├── requests/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── match_request.py
│   │   │   │   ├── prediction_request.py
│   │   │   │   └── ticket_request.py
│   │   │   │
│   │   │   └── responses/
│   │   │       ├── __init__.py
│   │   │       ├── match_response.py
│   │   │       ├── prediction_response.py
│   │   │       └── ticket_response.py
│   │   │
│   │   └── mappers/                      # DTO <-> Domain Model
│   │       ├── __init__.py
│   │       ├── match_mapper.py
│   │       ├── prediction_mapper.py
│   │       └── ticket_mapper.py
│   │
│   ├── application/                      # 📦 APPLICATION LAYER
│   │   ├── __init__.py
│   │   │
│   │   ├── contracts/                    # Contratos dos Services
│   │   │   ├── __init__.py
│   │   │   ├── match_service_contract.py
│   │   │   ├── prediction_service_contract.py
│   │   │   ├── ticket_service_contract.py
│   │   │   └── result_checker_service_contract.py
│   │   │
│   │   └── impl/                         # Implementações dos Services
│   │       ├── __init__.py
│   │       ├── match_service_impl.py
│   │       ├── prediction_service_impl.py
│   │       ├── ticket_service_impl.py
│   │       └── result_checker_service_impl.py
│   │
│   ├── domain/                           # 🧠 DOMAIN LAYER
│   │   ├── __init__.py
│   │   │
│   │   ├── models/                       # Domain Models (Entities)
│   │   │   ├── __init__.py
│   │   │   ├── match.py
│   │   │   ├── team.py
│   │   │   ├── bet.py
│   │   │   ├── ticket.py
│   │   │   ├── prediction.py
│   │   │   ├── betting_strategy.py       # Enum de estratégias de apostas
│   │   │   └── value_objects/
│   │   │       ├── __init__.py
│   │   │       ├── odds.py
│   │   │       └── confidence_score.py
│   │   │
│   │   ├── contracts/                    # Contratos/Ports (Abstrações)
│   │   │   ├── __init__.py
│   │   │   ├── odds_provider_contract.py
│   │   │   ├── data_source_contract.py
│   │   │   ├── analyzer_contract.py
│   │   │   ├── repository_contract.py
│   │   │   └── factory_contract.py
│   │   │
│   │   ├── services/                     # Domain Services (Regras de Negócio)
│   │   │   ├── __init__.py
│   │   │   ├── contracts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── value_bet_calculator_contract.py
│   │   │   │   ├── odds_comparator_contract.py
│   │   │   │   └── bankroll_manager_contract.py
│   │   │   │
│   │   │   └── impl/
│   │   │       ├── __init__.py
│   │   │       ├── value_bet_calculator_impl.py
│   │   │       ├── odds_comparator_impl.py
│   │   │       └── bankroll_manager_impl.py
│   │   │
│   │   ├── factories/                    # Factory (contracts + impl)
│   │   │   ├── __init__.py
│   │   │   ├── contracts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── odds_provider_factory_contract.py
│   │   │   │   ├── data_source_factory_contract.py
│   │   │   │   └── analyzer_factory_contract.py
│   │   │   │
│   │   │   └── impl/
│   │   │       ├── __init__.py
│   │   │       ├── odds_provider_factory_impl.py
│   │   │       ├── data_source_factory_impl.py
│   │   │       └── analyzer_factory_impl.py
│   │   │
│   │   └── utils/                        # Utilitários do Domain
│   │       ├── __init__.py
│   │       ├── validators_util.py        # Sufixo _util obrigatório
│   │       ├── calculators_util.py       # Sufixo _util obrigatório
│   │       ├── helpers_util.py           # Sufixo _util obrigatório
│   │       └── strategy_sorter_util.py   # Ordenação por estratégia de aposta
│   │
│   └── infrastructure/                   # 🔧 INFRASTRUCTURE LAYER
│       ├── __init__.py
│       │
│       ├── config/
│       │   ├── __init__.py
│       │   ├── settings.py
│       │   └── constants.py
│       │
│       ├── database/                     # Conexão e Repositórios
│       │   ├── __init__.py
│       │   ├── connection.py             # Conexão com data/betting.db
│       │   ├── models.py                 # SQLAlchemy Models
│       │   │
│       │   ├── cache/                    # 🗄️ Cache da API-Football
│       │   │   ├── __init__.py
│       │   │   ├── cache_config.py       # TTLs por tipo de dado
│       │   │   ├── cache_repository.py   # CRUD do cache
│       │   │   └── cache_models.py       # Modelo da tabela api_cache
│       │   │
│       │   ├── mappers/                  # DB Model <-> Domain Model
│       │   │   ├── __init__.py
│       │   │   ├── match_db_mapper.py
│       │   │   ├── ticket_db_mapper.py
│       │   │   └── prediction_db_mapper.py
│       │   │
│       │   └── repositories/             # Implementam Repository Contract
│       │       ├── __init__.py
│       │       ├── contracts/
│       │       │   ├── __init__.py
│       │       │   ├── match_repository_contract.py
│       │       │   ├── ticket_repository_contract.py
│       │       │   └── prediction_repository_contract.py
│       │       │
│       │       └── impl/
│       │           ├── __init__.py
│       │           ├── match_repository_impl.py
│       │           ├── ticket_repository_impl.py
│       │           └── prediction_repository_impl.py
│       │
│       ├── external/                     # Implementações Externas
│       │   ├── __init__.py
│       │   │
│       │   ├── api_football/             # API-Football (Dados + Odds)
│       │   │   ├── __init__.py
│       │   │   ├── api_football_client.py        # HTTP Client
│       │   │   ├── api_football_data_source_impl.py  # Implementa DataSourceContract
│       │   │   ├── api_football_odds_provider_impl.py # Implementa OddsProviderContract
│       │   │   ├── parsers/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── fixture_parser.py
│       │   │   │   ├── statistics_parser.py
│       │   │   │   └── odds_parser.py
│       │   │   └── mappers/
│       │   │       ├── __init__.py
│       │   │       ├── fixture_mapper.py
│       │   │       └── odds_mapper.py
│       │   │
│       │   └── analyzers/                # Implementam Analyzer Contract
│       │       ├── __init__.py
│       │       ├── poisson_analyzer_impl.py
│       │       └── xgboost_analyzer_impl.py
│       │
│       ├── scheduler/                    # ⏰ Jobs Agendados
│       │   ├── __init__.py
│       │   ├── scheduler_config.py       # Configuração APScheduler
│       │   └── jobs/
│       │       ├── __init__.py
│       │       └── result_checker_job.py # Verifica resultados a cada 1h
│       │
│       ├── container.py                  # 🏭 Dependency Injection Container
│       │
│       └── logging/
│           ├── __init__.py
│           └── logger.py
│
├── web-app/                              # ⚛️ REACT UI
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   │
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       │
│       ├── api/                          # API Client
│       │   ├── client.ts
│       │   └── endpoints.ts
│       │
│       ├── components/
│       │   ├── common/
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   └── Loading.tsx
│       │   │
│       │   ├── dashboard/
│       │   │   ├── StatsCard.tsx
│       │   │   └── RecentPredictions.tsx
│       │   │
│       │   ├── matches/
│       │   │   ├── MatchList.tsx
│       │   │   └── MatchCard.tsx
│       │   │
│       │   ├── predictions/
│       │   │   ├── PredictionPanel.tsx
│       │   │   ├── PredictionCard.tsx
│       │   │   └── ConfidenceMeter.tsx
│       │   │
│       │   └── tickets/
│       │       ├── TicketBuilder.tsx
│       │       └── TicketHistory.tsx
│       │
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── Matches.tsx
│       │   ├── Predictions.tsx
│       │   ├── Tickets.tsx
│       │   └── Settings.tsx
│       │
│       ├── hooks/
│       │   ├── useMatches.ts
│       │   └── usePredictions.ts
│       │
│       ├── types/
│       │   └── index.ts
│       │
│       └── styles/
│           └── globals.css
│
├── scripts/                              # Scripts CLI de treinamento
│   ├── download_historical_data.py       # Baixa CSVs Football-Data
│   ├── prepare_dataset.py                # Gera features
│   ├── train_model.py                    # Treina XGBoost
│   └── evaluate_model.py                 # Avalia modelo
│
└── notebooks/                            # Jupyter notebooks
    ├── 01_data_exploration.ipynb
    ├── 02_feature_engineering.ipynb
    └── 03_model_experiments.ipynb
```

### 🚀 Scripts de Inicialização

#### start.bat (Windows)

```batch
@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo    BETTING BOT - Iniciando Sistema
echo ========================================
echo.

REM ========================================
REM CONFIGURAÇÕES
REM ========================================
set PYTHON_VERSION=3.14
set PYTHON_INSTALLER=python-%PYTHON_VERSION%-amd64.exe
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%.0/%PYTHON_INSTALLER%
set PYTHON_LOCAL=.cache\python\%PYTHON_INSTALLER%
set PIP_CACHE_DIR=.cache\pip

REM ========================================
REM CRIA PASTA DE CACHE SE NÃO EXISTIR
REM ========================================
if not exist ".cache\" (
    echo [CACHE] Criando pasta de cache local...
    mkdir .cache
    mkdir .cache\pip
    mkdir .cache\python
)

REM ========================================
REM VERIFICA/INSTALA PYTHON 3.14
REM ========================================
echo [PYTHON] Verificando Python %PYTHON_VERSION%...

python --version 2>nul | findstr /C:"%PYTHON_VERSION%" >nul
if errorlevel 1 (
    echo [PYTHON] Python %PYTHON_VERSION% nao encontrado!
    
    REM Verifica se já tem o instalador em cache
    if exist "%PYTHON_LOCAL%" (
        echo [CACHE] Instalador encontrado em cache local.
    ) else (
        echo [DOWNLOAD] Baixando Python %PYTHON_VERSION%...
        echo [DOWNLOAD] URL: %PYTHON_URL%
        
        REM Usa PowerShell para baixar
        powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_LOCAL%'"
        
        if not exist "%PYTHON_LOCAL%" (
            echo [ERRO] Falha ao baixar Python. Verifique sua conexao.
            pause
            exit /b 1
        )
        echo [DOWNLOAD] Download concluido!
    )
    
    echo [PYTHON] Instalando Python %PYTHON_VERSION%...
    echo [PYTHON] IMPORTANTE: Marque "Add Python to PATH" durante a instalacao!
    start /wait "" "%PYTHON_LOCAL%" /passive InstallAllUsers=0 PrependPath=1
    
    echo [PYTHON] Instalacao concluida! Reinicie este script.
    pause
    exit /b 0
)

echo [OK] Python %PYTHON_VERSION% encontrado
echo.

REM ========================================
REM VERIFICA NODE.JS
REM ========================================
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado. Instale o Node.js 18+
    echo [INFO] Download: https://nodejs.org/
    pause
    exit /b 1
)

echo [OK] Node.js encontrado
echo.

REM ========================================
REM VERIFICA SE PASTA DATA EXISTE
REM Se não existir, recria venv do zero
REM ========================================
if not exist "data\" (
    echo [AVISO] Pasta data/ nao encontrada!
    echo [VENV] Recriando ambiente virtual do zero...
    
    REM Remove venv antigo se existir
    if exist ".venv\" (
        echo [VENV] Removendo .venv antigo...
        rmdir /s /q .venv
    )
    
    REM Cria novo venv
    echo [VENV] Criando novo ambiente virtual...
    python -m venv .venv
    
    REM Ativa venv e instala dependências com cache
    echo [VENV] Instalando dependencias (usando cache local)...
    call .venv\Scripts\activate.bat
    pip install --upgrade pip --cache-dir %PIP_CACHE_DIR%
    pip install -r requirements.txt --cache-dir %PIP_CACHE_DIR%
    
    echo [VENV] Ambiente virtual criado com sucesso!
    echo.
) else (
    REM Pasta data existe, verifica se venv existe
    if not exist ".venv\" (
        echo [VENV] Ambiente virtual nao encontrado. Criando...
        python -m venv .venv
        call .venv\Scripts\activate.bat
        pip install --upgrade pip --cache-dir %PIP_CACHE_DIR%
        pip install -r requirements.txt --cache-dir %PIP_CACHE_DIR%
    ) else (
        REM Ativa venv existente
        call .venv\Scripts\activate.bat
    )
)

echo.
echo [OK] Ambiente virtual ativado
echo [OK] Cache de libs em: %PIP_CACHE_DIR%
echo.
echo Iniciando o sistema...
python main.py

pause
```

#### start.sh (Linux/Mac)

```bash
#!/bin/bash

echo "========================================"
echo "   BETTING BOT - Iniciando Sistema"
echo "========================================"
echo ""

# ========================================
# CONFIGURAÇÕES
# ========================================
PYTHON_VERSION="3.14"
PIP_CACHE_DIR=".cache/pip"
PYTHON_CACHE_DIR=".cache/python"

# ========================================
# CRIA PASTA DE CACHE SE NÃO EXISTIR
# ========================================
if [ ! -d ".cache" ]; then
    echo "[CACHE] Criando pasta de cache local..."
    mkdir -p .cache/pip
    mkdir -p .cache/python
fi

# ========================================
# VERIFICA/INSTALA PYTHON 3.14
# ========================================
echo "[PYTHON] Verificando Python $PYTHON_VERSION..."

# Verifica se python3.14 está disponível
if command -v python3.14 &> /dev/null; then
    PYTHON_CMD="python3.14"
    echo "[OK] Python $PYTHON_VERSION encontrado"
elif python3 --version 2>&1 | grep -q "$PYTHON_VERSION"; then
    PYTHON_CMD="python3"
    echo "[OK] Python $PYTHON_VERSION encontrado"
else
    echo "[PYTHON] Python $PYTHON_VERSION nao encontrado!"
    echo ""
    
    # Detecta o sistema operacional
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - usa Homebrew
        echo "[INFO] macOS detectado. Instalando via Homebrew..."
        
        if ! command -v brew &> /dev/null; then
            echo "[ERRO] Homebrew nao encontrado. Instale em: https://brew.sh/"
            exit 1
        fi
        
        brew install python@3.14
        PYTHON_CMD="python3.14"
    else
        # Linux - usa pyenv ou apt
        echo "[INFO] Linux detectado."
        echo ""
        echo "Opcoes de instalacao:"
        echo "  1. Ubuntu/Debian: sudo apt install python3.14"
        echo "  2. Fedora: sudo dnf install python3.14"
        echo "  3. Pyenv: pyenv install 3.14.0"
        echo ""
        echo "Apos instalar, execute este script novamente."
        exit 1
    fi
fi

echo ""

# ========================================
# VERIFICA NODE.JS
# ========================================
if ! command -v node &> /dev/null; then
    echo "[ERRO] Node.js nao encontrado. Instale o Node.js 18+"
    echo "[INFO] Download: https://nodejs.org/"
    exit 1
fi

echo "[OK] Node.js encontrado"
echo ""

# ========================================
# VERIFICA SE PASTA DATA EXISTE
# Se não existir, recria venv do zero
# ========================================
if [ ! -d "data" ]; then
    echo "[AVISO] Pasta data/ nao encontrada!"
    echo "[VENV] Recriando ambiente virtual do zero..."
    
    # Remove venv antigo se existir
    if [ -d ".venv" ]; then
        echo "[VENV] Removendo .venv antigo..."
        rm -rf .venv
    fi
    
    # Cria novo venv
    echo "[VENV] Criando novo ambiente virtual..."
    $PYTHON_CMD -m venv .venv
    
    # Ativa venv e instala dependências com cache
    echo "[VENV] Instalando dependencias (usando cache local)..."
    source .venv/bin/activate
    pip install --upgrade pip --cache-dir $PIP_CACHE_DIR
    pip install -r requirements.txt --cache-dir $PIP_CACHE_DIR
    
    echo "[VENV] Ambiente virtual criado com sucesso!"
    echo ""
else
    # Pasta data existe, verifica se venv existe
    if [ ! -d ".venv" ]; then
        echo "[VENV] Ambiente virtual nao encontrado. Criando..."
        $PYTHON_CMD -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip --cache-dir $PIP_CACHE_DIR
        pip install -r requirements.txt --cache-dir $PIP_CACHE_DIR
    else
        # Ativa venv existente
        source .venv/bin/activate
    fi
fi

echo ""
echo "[OK] Ambiente virtual ativado"
echo "[OK] Cache de libs em: $PIP_CACHE_DIR"
echo ""
echo "Iniciando o sistema..."
python main.py
```

#### main.py (Entry Point)

```python
"""
Betting Bot - Entry Point
Inicializa o banco de dados (se necessário), API e React
"""

import os
import sys
import subprocess
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "betting.db"


def init_database():
    """Inicializa o banco de dados se não existir"""
    if not DB_PATH.exists():
        print("[DB] Banco de dados não encontrado. Criando...")
        
        # Importa e executa o script de inicialização
        sys.path.insert(0, str(DATA_DIR / "scripts"))
        from init_database import create_database
        
        create_database(DB_PATH)
        print(f"[DB] Banco de dados criado em: {DB_PATH}")
    else:
        print(f"[DB] Banco de dados encontrado: {DB_PATH}")


def start_api():
    """Inicia a API FastAPI"""
    print("[API] Iniciando FastAPI na porta 8000...")
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.web.app:app", 
         "--host", "0.0.0.0", "--port", "8000", "--reload"],
        cwd=ROOT_DIR
    )


def start_react():
    """Inicia o React App"""
    print("[REACT] Iniciando React na porta 5173...")
    web_app_dir = ROOT_DIR / "web-app"
    
    # Instala dependências se necessário
    if not (web_app_dir / "node_modules").exists():
        print("[REACT] Instalando dependências...")
        subprocess.run(["npm", "install"], cwd=web_app_dir, shell=True)
    
    subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=web_app_dir,
        shell=True
    )


def main():
    """Função principal"""
    print("=" * 50)
    print("       BETTING BOT - Sistema de Apostas")
    print("=" * 50)
    print()
    
    # 1. Inicializa banco de dados
    init_database()
    print()
    
    # 2. Inicia API
    start_api()
    print()
    
    # 3. Inicia React
    start_react()
    print()
    
    print("=" * 50)
    print("Sistema iniciado!")
    print("  - API: http://localhost:8000")
    print("  - React: http://localhost:5173")
    print("  - Docs: http://localhost:8000/docs")
    print("=" * 50)
    print()
    print("Pressione Ctrl+C para encerrar...")
    
    # Mantém o processo rodando
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nEncerrando sistema...")


if __name__ == "__main__":
    main()
```

#### data/scripts/init_database.py

```python
"""
Script de inicialização do banco de dados
Chamado pela main.py se o banco não existir
"""

import sqlite3
from pathlib import Path


def create_database(db_path: Path):
    """Cria o banco de dados com todas as tabelas necessárias"""
    
    # Garante que o diretório existe
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ==========================================
    # ESTRATÉGIA DE IDs: UUID v4
    # ==========================================
    # Todos os IDs são UUID v4 gerados automaticamente pelo SQLite.
    # Formato: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
    # A expressão DEFAULT gera UUID compatível com RFC 4122.
    # Benefícios:
    #   - IDs únicos globalmente (sem colisão)
    #   - Não expõe quantidade de registros
    #   - Seguro para APIs públicas
    #   - Facilita merge de bancos diferentes
    
    # ==========================================
    # TABELAS PRINCIPAIS
    # ==========================================
    
    # Tabela de times
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
            external_id INTEGER UNIQUE,
            name TEXT NOT NULL,
            country TEXT,
            logo_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de partidas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
            external_id INTEGER UNIQUE,
            home_team_id TEXT REFERENCES teams(id),
            away_team_id TEXT REFERENCES teams(id),
            league_id INTEGER,
            league_name TEXT,
            match_date DATETIME,
            status TEXT DEFAULT 'SCHEDULED',
            home_score INTEGER,
            away_score INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de previsões
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
            match_id TEXT REFERENCES matches(id),
            market TEXT NOT NULL,
            predicted_outcome TEXT NOT NULL,
            confidence REAL NOT NULL,
            odds REAL,
            expected_value REAL,
            recommendation TEXT,
            status TEXT DEFAULT 'PENDING',
            result TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de bilhetes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
            name TEXT,
            stake REAL,
            combined_odds REAL,
            potential_return REAL,
            status TEXT DEFAULT 'PENDING',
            result TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de associação bilhete-previsão
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_predictions (
            ticket_id TEXT REFERENCES tickets(id),
            prediction_id TEXT REFERENCES predictions(id),
            PRIMARY KEY (ticket_id, prediction_id)
        )
    """)
    
    # ==========================================
    # TABELA DE CACHE DA API
    # ==========================================
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_cache (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
            cache_key TEXT UNIQUE NOT NULL,
            endpoint TEXT NOT NULL,
            response_data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            hit_count INTEGER DEFAULT 0
        )
    """)
    
    # ==========================================
    # TABELA DE DADOS HISTÓRICOS (TREINAMENTO)
    # ==========================================
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historical_matches (
            id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
            source TEXT NOT NULL,
            season TEXT,
            league TEXT,
            match_date DATE,
            home_team TEXT,
            away_team TEXT,
            home_goals INTEGER,
            away_goals INTEGER,
            result TEXT,
            home_odds REAL,
            draw_odds REAL,
            away_odds REAL,
            over25_odds REAL,
            under25_odds REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ==========================================
    # ÍNDICES
    # ==========================================
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_date ON matches(match_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON api_cache(cache_key)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON api_cache(expires_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_historical_date ON historical_matches(match_date)")
    
    conn.commit()
    conn.close()
    
    print(f"[DB] Tabelas criadas com sucesso!")


if __name__ == "__main__":
    # Para testes diretos
    import sys
    if len(sys.argv) > 1:
        create_database(Path(sys.argv[1]))
    else:
        print("Uso: python init_database.py <caminho_do_banco>")
```

---

## 🔄 Fluxo de Dados

### Conversão DTO → Domain Model → Response

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    FLUXO: DTO → DOMAIN MODEL → RESPONSE                  │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  [1. REQUEST CHEGANDO]                                                   │
│                                                                          │
│  POST /api/v1/predictions/analyze                                        │
│  Body: { "platform": "bet365", "league": "premier-league" }              │
│                     │                                                    │
│                     ▼                                                    │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ WEB LAYER                                                          │ │
│  │                                                                    │ │
│  │  PredictionController                                              │ │
│  │    │                                                               │ │
│  │    ├──▶ Valida PredictionRequestDTO (Pydantic)                    │ │
│  │    │                                                               │ │
│  │    ├──▶ PredictionMapper.to_domain(dto) ──▶ PredictionParams      │ │
│  │    │                                        (Domain Model)         │ │
│  │    │                                                               │ │
│  │    └──▶ Chama IPredictionService.analyze(params)                  │ │
│  │                        │                                           │ │
│  └────────────────────────┼───────────────────────────────────────────┘ │
│                           │                                              │
│                           ▼ (via Interface)                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ APPLICATION LAYER                                                  │ │
│  │                                                                    │ │
│  │  PredictionService (implements IPredictionService)                 │ │
│  │    │                                                               │ │
│  │    ├──▶ Usa IPlatformFactory.create("bet365")                     │ │
│  │    ├──▶ Usa IDataSourceFactory.create("sofascore")                │ │
│  │    ├──▶ Usa IAnalyzerFactory.create("poisson")                    │ │
│  │    │                                                               │ │
│  │    └──▶ Retorna List[Prediction] (Domain Models)                  │ │
│  │                        │                                           │ │
│  └────────────────────────┼───────────────────────────────────────────┘ │
│                           │                                              │
│                           ▼                                              │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ WEB LAYER (Response)                                               │ │
│  │                                                                    │ │
│  │  PredictionController                                              │ │
│  │    │                                                               │ │
│  │    └──▶ PredictionMapper.to_response(predictions)                 │ │
│  │                        │                                           │ │
│  │                        ▼                                           │ │
│  │         List[PredictionResponseDTO] ──▶ JSON Response             │ │
│  │                                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### Workflow do Usuário (Sob Demanda)

```
┌────────────────────────────────────────────────────────────────┐
│                    FLUXO SOB DEMANDA                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  [Usuário no React]                                            │
│         │                                                      │
│         ▼                                                      │
│  1. Seleciona Casa de Apostas (Bet365, Betfair, etc.)         │
│         │                                                      │
│         ▼                                                      │
│  2. Seleciona Liga/Campeonato                                 │
│         │                                                      │
│         ▼                                                      │
│  3. Clica "Analisar Jogos" ──────▶ POST /api/v1/analyze       │
│         │                                                      │
│         ▼                                                      │
│  4. Backend:                                                   │
│     • Factory cria DataSource (API-Football)                  │
│     • Busca partidas e estatísticas                           │
│     • Factory cria OddsProvider (API-Football)                │
│     • Busca odds da casa selecionada                          │
│     • Factory cria Analyzer (Poisson/XGBoost)                 │
│     • Gera previsões                                          │
│         │                                                      │
│         ▼                                                      │
│  5. Retorna bilhetes sugeridos para o Web App                 │
│         │                                                      │
│         ▼                                                      │
│  6. Usuário visualiza/salva/exporta bilhetes                  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## 📜 Contratos (Contracts)

### OddsProviderContract (Provedor de Odds)

```python
# domain/contracts/odds_provider_contract.py

from abc import ABC, abstractmethod
from typing import List, Dict
from domain.models.match import Match
from domain.models.value_objects.odds import Odds


class OddsProviderContract(ABC):
    """Contrato abstrato para provedores de odds"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do provedor"""
        pass
    
    @abstractmethod
    def get_odds(
        self, 
        fixture_id: int, 
        bookmaker: str,
        market: str
    ) -> Odds:
        """Retorna odds de uma casa específica para um mercado"""
        pass
    
    @abstractmethod
    def get_odds_all_bookmakers(
        self, 
        fixture_id: int, 
        market: str
    ) -> Dict[str, Odds]:
        """Retorna odds de todas as casas para um mercado"""
        pass
    
    @abstractmethod
    def get_available_bookmakers(self) -> List[str]:
        """Retorna casas de apostas disponíveis"""
        pass
    
    @abstractmethod
    def get_available_markets(self) -> List[str]:
        """Retorna mercados disponíveis"""
        pass
```

### DataSourceContract (Fontes de Dados)

```python
# domain/contracts/data_source_contract.py

from abc import ABC, abstractmethod
from typing import List
from domain.models.match import Match
from domain.models.team import Team


class DataSourceContract(ABC):
    """Contrato abstrato para fontes de dados estatísticos"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome da fonte de dados"""
        pass
    
    @abstractmethod
    def get_team_stats(self, team_id: str) -> Team:
        """Retorna estatísticas do time"""
        pass
    
    @abstractmethod
    def get_head_to_head(self, team1_id: str, team2_id: str) -> List[Match]:
        """Retorna histórico de confrontos"""
        pass
    
    @abstractmethod
    def get_team_form(self, team_id: str, num_matches: int = 5) -> List[Match]:
        """Retorna últimos jogos do time"""
        pass
```

### AnalyzerContract (Analisadores/IA)

```python
# domain/contracts/analyzer_contract.py

from abc import ABC, abstractmethod
from typing import List
from domain.models.match import Match
from domain.models.prediction import Prediction


class AnalyzerContract(ABC):
    """Contrato abstrato para analisadores/modelos de IA"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do analisador"""
        pass
    
    @abstractmethod
    def analyze(self, match: Match, market: str) -> Prediction:
        """Analisa uma partida e retorna previsão"""
        pass
    
    @abstractmethod
    def get_supported_markets(self) -> List[str]:
        """Retorna mercados suportados pelo analisador"""
        pass
```

### OddsProviderFactoryContract (Factory de Provedores de Odds)

```python
# domain/factories/contracts/odds_provider_factory_contract.py

from abc import ABC, abstractmethod
from typing import List
from domain.contracts.odds_provider_contract import OddsProviderContract


class OddsProviderFactoryContract(ABC):
    """Contrato abstrato para factory de provedores de odds"""
    
    @abstractmethod
    def create(self, provider_name: str) -> OddsProviderContract:
        """Cria instância do provedor de odds"""
        pass
    
    @abstractmethod
    def get_available(self) -> List[str]:
        """Lista provedores disponíveis"""
        pass
```

### RepositoryContract (Repositórios)

```python
# domain/contracts/repository_contract.py

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class RepositoryContract(ABC, Generic[T]):
    """Contrato genérico para repositórios"""
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Busca entidade por ID"""
        pass
    
    @abstractmethod
    def get_all(self, limit: int = 100) -> List[T]:
        """Retorna todas as entidades"""
        pass
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Salva uma entidade"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Remove uma entidade"""
        pass
```

### PredictionServiceContract (Application Service)

```python
# application/contracts/prediction_service_contract.py

from abc import ABC, abstractmethod
from typing import List
from domain.models.prediction import Prediction
from domain.models.prediction_params import PredictionParams


class PredictionServiceContract(ABC):
    """Contrato para o serviço de previsões"""
    
    @abstractmethod
    def analyze(self, params: PredictionParams) -> List[Prediction]:
        """Executa análise e retorna previsões"""
        pass
    
    @abstractmethod
    def get_by_id(self, prediction_id: str) -> Prediction:
        """Busca previsão por ID"""
        pass
    
    @abstractmethod
    def get_history(self, limit: int = 50) -> List[Prediction]:
        """Retorna histórico de previsões"""
        pass
```

---

## 🏭 Padrões de Projeto

### Factory Pattern

```python
# domain/factories/impl/data_source_factory_impl.py

from typing import Dict, Type, List
from domain.factories.contracts.data_source_factory_contract import DataSourceFactoryContract
from domain.contracts.data_source_contract import DataSourceContract


class DataSourceFactoryImpl(DataSourceFactoryContract):
    """Implementação concreta da factory de fontes de dados"""
    
    def __init__(self):
        self._data_sources: Dict[str, Type[DataSourceContract]] = {}
    
    def register(self, name: str, data_source_class: Type[DataSourceContract]) -> None:
        """Registra uma fonte de dados"""
        self._data_sources[name.lower()] = data_source_class
    
    def create(self, data_source_name: str) -> DataSourceContract:
        """Cria instância da fonte de dados"""
        data_source_class = self._data_sources.get(data_source_name.lower())
        
        if not data_source_class:
            raise ValueError(
                f"Fonte de dados '{data_source_name}' não registrada. "
                f"Disponíveis: {self.get_available()}"
            )
        
        return data_source_class()
    
    def get_available(self) -> List[str]:
        """Lista fontes de dados disponíveis"""
        return list(self._data_sources.keys())
```

### Dependency Injection Container

```python
# infrastructure/container.py

from domain.factories.contracts.odds_provider_factory_contract import OddsProviderFactoryContract
from domain.factories.contracts.data_source_factory_contract import DataSourceFactoryContract
from domain.factories.contracts.analyzer_factory_contract import AnalyzerFactoryContract
from infrastructure.database.repositories.contracts.prediction_repository_contract import PredictionRepositoryContract

from domain.factories.impl.odds_provider_factory_impl import OddsProviderFactoryImpl
from domain.factories.impl.data_source_factory_impl import DataSourceFactoryImpl
from domain.factories.impl.analyzer_factory_impl import AnalyzerFactoryImpl

from infrastructure.database.repositories.impl.prediction_repository_impl import PredictionRepositoryImpl
from infrastructure.external.api_football.api_football_data_source_impl import ApiFootballDataSourceImpl
from infrastructure.external.api_football.api_football_odds_provider_impl import ApiFootballOddsProviderImpl
from infrastructure.external.analyzers.poisson_analyzer_impl import PoissonAnalyzerImpl

from application.contracts.prediction_service_contract import PredictionServiceContract
from application.impl.prediction_service_impl import PredictionServiceImpl


class Container:
    """Dependency Injection Container"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa e registra todas as dependências"""
        
        # Factories
        self._odds_provider_factory = OddsProviderFactoryImpl()
        self._odds_provider_factory.register("api_football", ApiFootballOddsProviderImpl)
        
        self._data_source_factory = DataSourceFactoryImpl()
        self._data_source_factory.register("api_football", ApiFootballDataSourceImpl)
        
        self._analyzer_factory = AnalyzerFactoryImpl()
        self._analyzer_factory.register("poisson", PoissonAnalyzerImpl)
        
        # Repositories
        self._prediction_repository = PredictionRepositoryImpl()
        
        # Services
        self._prediction_service = PredictionServiceImpl(
            odds_provider_factory=self._odds_provider_factory,
            data_source_factory=self._data_source_factory,
            analyzer_factory=self._analyzer_factory,
            prediction_repository=self._prediction_repository
        )
    
    # Getters retornam contracts, não implementações
    
    def get_odds_provider_factory(self) -> OddsProviderFactoryContract:
        return self._odds_provider_factory
    
    def get_data_source_factory(self) -> DataSourceFactoryContract:
        return self._data_source_factory
    
    def get_prediction_service(self) -> PredictionServiceContract:
        return self._prediction_service


# Singleton instance
container = Container()
```

### Mapper Pattern (DTO ↔ Domain Model)

```python
# web/mappers/prediction_mapper.py

from typing import List
from datetime import date

from web.dtos.requests.prediction_request import PredictionRequestDTO
from web.dtos.responses.prediction_response import PredictionResponseDTO
from domain.models.prediction import Prediction
from domain.models.prediction_params import PredictionParams


class PredictionMapper:
    """Mapper: DTO <-> Domain Model"""
    
    @staticmethod
    def to_domain(dto: PredictionRequestDTO) -> PredictionParams:
        """Converte DTO de request para Domain Model"""
        return PredictionParams(
            bookmaker=dto.bookmaker,
            league=dto.league,
            match_date=dto.match_date or date.today(),
            markets=dto.markets
        )
    
    @staticmethod
    def to_response(prediction: Prediction) -> PredictionResponseDTO:
        """Converte Domain Model para DTO de response"""
        return PredictionResponseDTO(
            id=prediction.id,
            match_id=prediction.match.id,
            home_team=prediction.match.home_team.name,
            away_team=prediction.match.away_team.name,
            market=prediction.market,
            predicted_outcome=prediction.predicted_outcome,
            confidence=prediction.confidence.value,
            odds=prediction.odds.value,
            expected_value=prediction.expected_value,
            recommendation=prediction.get_recommendation(),
            created_at=prediction.created_at.isoformat()
        )
```

---

## 🧩 Componentes

### Camadas e Responsabilidades

| Camada | Responsabilidade |
|--------|------------------|
| **Web** | Controllers, DTOs, Mappers, Validação de entrada, React UI |
| **Application** | Interfaces de Services, Orquestração, Casos de uso |
| **Domain** | Regras de negócio, Models, Interfaces, Factories, Utils |
| **Infrastructure** | Banco de dados, APIs externas, Configs, Logging, DI Container |

### Mercados de Futebol (MVP)

| Mercado | Código | Descrição |
|---------|--------|-----------|
| Match Result | `1X2` | Resultado final |
| Over/Under | `OU_2.5` | Mais/menos de X gols |
| Both Teams Score | `BTTS` | Ambas marcam |
| Double Chance | `DC` | Dupla chance |
| Draw No Bet | `DNB` | Empate não aposta |

### Stack Tecnológica

| Componente | Tecnologia |
|------------|------------|
| Linguagem Backend | Python 3.11+ |
| Framework API | FastAPI |
| Banco de Dados | SQLite + SQLAlchemy |
| Frontend | React + Vite + TypeScript |
| IA/ML | scikit-learn, XGBoost |
| HTTP Client | httpx, requests |
| Validação | Pydantic |

---

## 🔒 Regras de Dependência

```
┌─────────────────────────────────────────────────────────────────┐
│                  DEPENDENCY RULES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        DOMAIN                                   │
│                   (Contracts + Models)                          │
│                          ▲                                      │
│                          │                                      │
│         ┌────────────────┼────────────────┐                    │
│         │                │                │                    │
│         │                │                │                    │
│    APPLICATION     INFRASTRUCTURE       WEB                    │
│    (implements     (implements        (usa via                 │
│     Service        OddsProvider,      Contract)                │
│     Contract)      DataSource,                                 │
│                    Repository,                                 │
│                    Analyzer)                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Regras

✅ **Domain Layer** não depende de nenhuma outra camada  
✅ **Application Layer** depende apenas de contracts do Domain  
✅ **Infrastructure Layer** implementa contracts do Domain  
✅ **Web Layer** depende de Application via contracts  
✅ **DTOs** existem apenas na Web Layer  
✅ **Domain Models** são usados internamente entre camadas  
✅ **Todas as camadas acessam outras via Contract, nunca implementação**

---

## 📌 MVP (Fase 1)

- ✅ Fonte de Dados e Odds: API-Football
- ✅ Casas de Apostas: Bet365, Betfair, 1xBet (via API-Football)
- ✅ Esporte: Futebol
- ✅ Mercados: 1X2, Over/Under 2.5, BTTS
- ✅ IA Preditiva: Modelo estatístico (Poisson) + XGBoost
- ✅ Dados Históricos: Football-Data.co.uk (treino) + API-Football (atualização)
- ✅ Estratégias de Apostas: Conservador, Value Bet, Agressivo, Balanceado
- ✅ Interface: React Web App
- ✅ DB: SQLite (auto-init)
- ✅ Cache: TTL diferenciado por tipo de dado (economia de ~70% requests)
- ✅ Limite: 100 requests/dia (plano gratuito)
- ✅ Verificação automática de resultados (scheduler)

---

## 🎯 Estratégias de Apostas

O usuário pode escolher a estratégia de ordenação das sugestões de apostas, definindo qual critério terá prioridade.

### Estratégias Disponíveis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    🎯 ESTRATÉGIAS DE APOSTAS                                │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   🛡️ CONSERVADOR (Maior Confiança)                                 │  │
│   │   ─────────────────────────────────                                │  │
│   │                                                                     │  │
│   │   Ordenação: confidence DESC                                       │  │
│   │   Prioriza: Apostas com maior chance de acertar                   │  │
│   │   Perfil: Odds menores, lucro menor, mais consistente             │  │
│   │   Ideal para: Acumuladores, iniciantes, quem quer consistência    │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   📊 VALUE BET (Maior Valor Matemático)                            │  │
│   │   ─────────────────────────────────────                            │  │
│   │                                                                     │  │
│   │   Ordenação: expected_value DESC                                   │  │
│   │   Prioriza: Apostas com maior valor esperado (edge sobre a casa)  │  │
│   │   Perfil: Melhor retorno a longo prazo                            │  │
│   │   Ideal para: Apostadores experientes, estratégia de longo prazo  │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   🎰 AGRESSIVO (Maior Retorno Potencial)                           │  │
│   │   ──────────────────────────────────────                           │  │
│   │                                                                     │  │
│   │   Ordenação: (odds * confidence) DESC                              │  │
│   │   Prioriza: Odds altas com confiança razoável                     │  │
│   │   Perfil: Maior risco, maior recompensa                           │  │
│   │   Ideal para: Bilhetes de alto risco, apostas ocasionais          │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   ⚖️ BALANCEADO (Score Combinado) - PADRÃO                         │  │
│   │   ────────────────────────────────────────                         │  │
│   │                                                                     │  │
│   │   Ordenação: score DESC                                            │  │
│   │   Fórmula: (confidence × 0.4) + (expected_value × 0.4)            │  │
│   │            + (normalized_odds × 0.2)                               │  │
│   │   Prioriza: Equilíbrio entre todos os fatores                     │  │
│   │   Ideal para: Maioria dos usuários, uso geral                     │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Comparativo das Estratégias

| Estratégia | Ordenação | Risco | Retorno | Consistência |
|------------|-----------|-------|---------|--------------|
| 🛡️ Conservador | `confidence DESC` | Baixo | Baixo | Alta |
| 📊 Value Bet | `expected_value DESC` | Médio | Médio-Alto | Média |
| 🎰 Agressivo | `odds * confidence DESC` | Alto | Alto | Baixa |
| ⚖️ Balanceado | `score DESC` | Médio | Médio | Média |

### Implementação na Arquitetura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    📦 IMPLEMENTAÇÃO                                         │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   DOMAIN LAYER                                                     │  │
│   │   ────────────                                                     │  │
│   │   src/domain/models/betting_strategy.py                           │  │
│   │                                                                     │  │
│   │   class BettingStrategy(Enum):                                    │  │
│   │       CONSERVATIVE = "conservative"  # Maior confiança            │  │
│   │       VALUE_BET = "value_bet"        # Maior valor esperado       │  │
│   │       AGGRESSIVE = "aggressive"      # Maior retorno potencial    │  │
│   │       BALANCED = "balanced"          # Score combinado (padrão)   │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   DOMAIN LAYER - UTILS                                             │  │
│   │   ────────────────────                                             │  │
│   │   src/domain/utils/strategy_sorter_util.py                        │  │
│   │                                                                     │  │
│   │   def sort_by_strategy(predictions, strategy: BettingStrategy):   │  │
│   │       if strategy == CONSERVATIVE:                                 │  │
│   │           return sorted(predictions, key=lambda p: p.confidence,  │  │
│   │                        reverse=True)                               │  │
│   │       elif strategy == VALUE_BET:                                  │  │
│   │           return sorted(predictions, key=lambda p: p.expected_value│ │
│   │                        reverse=True)                               │  │
│   │       elif strategy == AGGRESSIVE:                                 │  │
│   │           return sorted(predictions,                               │  │
│   │                        key=lambda p: p.odds * p.confidence,       │  │
│   │                        reverse=True)                               │  │
│   │       else:  # BALANCED                                           │  │
│   │           return sorted(predictions,                               │  │
│   │                        key=lambda p: calculate_score(p),          │  │
│   │                        reverse=True)                               │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   APPLICATION LAYER                                                │  │
│   │   ─────────────────                                                │  │
│   │   src/application/impl/prediction_service_impl.py                 │  │
│   │                                                                     │  │
│   │   def analyze(self, params: AnalyzeParams) -> List[Prediction]:   │  │
│   │       predictions = self._generate_predictions(params)            │  │
│   │       # Ordena de acordo com a estratégia escolhida               │  │
│   │       return sort_by_strategy(predictions, params.strategy)       │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   WEB LAYER - REQUEST DTO                                          │  │
│   │   ───────────────────────                                          │  │
│   │   src/web/dtos/requests/prediction_request.py                     │  │
│   │                                                                     │  │
│   │   class PredictionRequestDTO(BaseModel):                          │  │
│   │       platform: str                                                │  │
│   │       league: str                                                  │  │
│   │       markets: List[str]                                          │  │
│   │       strategy: str = "balanced"  # Estratégia padrão             │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Cache da API-Football

O sistema utiliza cache local (SQLite) para reduzir o consumo de requests da API-Football, respeitando o limite de 100 requests/dia do plano gratuito.

### Estratégia: TTL Diferenciado por Tipo de Dado

Cada tipo de dado tem um tempo de expiração (TTL) baseado na frequência real de atualização na fonte:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    🗄️ ESTRATÉGIA DE CACHE                                   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   CONFIGURAÇÃO DE TTL POR ENDPOINT                                 │  │
│   │   ────────────────────────────────                                 │  │
│   │                                                                     │  │
│   │   Endpoint              │ TTL      │ Justificativa                 │  │
│   │   ──────────────────────┼──────────┼─────────────────────────────  │  │
│   │   /leagues              │ 30 dias  │ Dados estáticos               │  │
│   │   /teams                │ 30 dias  │ Dados estáticos               │  │
│   │   /fixtures/headtohead  │ 7 dias   │ Histórico, raramente muda     │  │
│   │   /teams/statistics     │ 24 horas │ Atualiza após cada rodada     │  │
│   │   /fixtures             │ 6 horas  │ Jogos agendados mudam pouco   │  │
│   │   /odds                 │ 30 min   │ Atualiza frequentemente       │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   ECONOMIA DE REQUESTS                                             │  │
│   │   ────────────────────────                                         │  │
│   │                                                                     │  │
│   │   Endpoint              │ Sem Cache │ Com Cache │ Economia         │  │
│   │   ──────────────────────┼───────────┼───────────┼────────────────  │  │
│   │   /leagues              │ 1/análise │ 1/mês     │ ~99%             │  │
│   │   /teams                │ 1/análise │ 1/mês     │ ~99%             │  │
│   │   /fixtures/headtohead  │ 2/análise │ 2/semana  │ ~95%             │  │
│   │   /teams/statistics     │ 2/análise │ 2/dia     │ ~80%             │  │
│   │   /fixtures             │ 1/análise │ 4/dia     │ ~70%             │  │
│   │   /odds                 │ 1/análise │ 2/hora    │ ~50%             │  │
│   │                                                                     │  │
│   │   TOTAL: ~41 req/análise → ~8-15 req/análise (~70% economia)      │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Impacto na Capacidade Diária

| Métrica | Sem Cache | Com Cache |
|---------|-----------|-----------|
| **Requests por análise (10 jogos)** | ~41 | ~8-15 |
| **Análises por dia** | ~2 | ~6-12 |
| **Bilhetes triplos por dia** | ~7 | ~20-30 |

### Estrutura da Tabela de Cache

```sql
-- Tabela: api_cache
-- Nota: SQLite gera UUID v4 automaticamente via expressão DEFAULT
CREATE TABLE api_cache (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    cache_key TEXT UNIQUE NOT NULL,      -- Ex: "teams_statistics_123_2026"
    endpoint TEXT NOT NULL,               -- Ex: "/teams/statistics"
    response_data TEXT NOT NULL,          -- JSON da resposta
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,         -- created_at + TTL
    hit_count INTEGER DEFAULT 0           -- Quantas vezes foi usado
);

CREATE INDEX idx_cache_key ON api_cache(cache_key);
CREATE INDEX idx_expires_at ON api_cache(expires_at);
```

### Fluxo de Cache

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    🔄 FLUXO DE CACHE                                        │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   1. REQUISIÇÃO CHEGA                                              │  │
│   │   ──────────────────────                                           │  │
│   │                                                                     │  │
│   │   api_football_client.get_team_statistics(team_id=123)            │  │
│   │                                                                     │  │
│   └──────────────────────────────┬──────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   2. VERIFICA CACHE                                                │  │
│   │   ─────────────────                                                │  │
│   │                                                                     │  │
│   │   cache_key = "teams_statistics_123_2026"                          │  │
│   │   cached = cache_repository.get(cache_key)                         │  │
│   │                                                                     │  │
│   │   if cached and not cached.is_expired:                             │  │
│   │       return cached.response_data  # ✅ CACHE HIT                  │  │
│   │                                                                     │  │
│   └──────────────────────────────┬──────────────────────────────────────┘  │
│                                  │                                          │
│                          CACHE MISS                                         │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   3. CHAMA API-FOOTBALL                                            │  │
│   │   ─────────────────────                                            │  │
│   │                                                                     │  │
│   │   response = http_client.get("/teams/statistics?team=123")         │  │
│   │                                                                     │  │
│   └──────────────────────────────┬──────────────────────────────────────┘  │
│                                  │                                          │
│                                  ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                                                                     │  │
│   │   4. SALVA NO CACHE                                                │  │
│   │   ─────────────────                                                │  │
│   │                                                                     │  │
│   │   ttl = CACHE_TTL["/teams/statistics"]  # 24 horas                │  │
│   │   cache_repository.save(                                           │  │
│   │       cache_key=cache_key,                                         │  │
│   │       endpoint="/teams/statistics",                                │  │
│   │       response_data=response.json(),                               │  │
│   │       expires_at=now() + ttl                                       │  │
│   │   )                                                                │  │
│   │                                                                     │  │
│   │   return response.json()                                           │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Configuração de TTL (código)

```python
# infrastructure/database/cache/cache_config.py

from datetime import timedelta

CACHE_TTL = {
    # Dados estáticos (raramente mudam)
    "/leagues": timedelta(days=30),
    "/teams": timedelta(days=30),
    
    # Dados históricos
    "/fixtures/headtohead": timedelta(days=7),
    
    # Dados que mudam por rodada
    "/teams/statistics": timedelta(hours=24),
    
    # Dados de jogos agendados
    "/fixtures": timedelta(hours=6),
    
    # Odds (atualizam frequentemente)
    "/odds": timedelta(minutes=30),
}

def get_ttl_for_endpoint(endpoint: str) -> timedelta:
    """Retorna TTL para um endpoint, default 1 hora"""
    for key, ttl in CACHE_TTL.items():
        if key in endpoint:
            return ttl
    return timedelta(hours=1)
```

### Limpeza de Cache Expirado

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                    🧹 LIMPEZA AUTOMÁTICA                                    │
│                                                                             │
│   Job agendado para rodar a cada 1 hora:                                   │
│                                                                             │
│   DELETE FROM api_cache WHERE expires_at < CURRENT_TIMESTAMP;              │
│                                                                             │
│   Isso mantém o banco limpo e evita crescimento indefinido.                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⏰ Scheduler de Verificação de Resultados

O sistema possui um job agendado que roda periodicamente para verificar os resultados dos jogos.

### Funcionamento

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESULT CHECKER SCHEDULER                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Frequência: A cada 1 hora                                      │
│  Tecnologia: APScheduler                                        │
│                                                                 │
│  Fluxo:                                                         │
│  ───────                                                        │
│  1. Busca previsões com status "PENDING"                       │
│  2. Filtra jogos que já terminaram (datetime + 2h)             │
│  3. Para cada jogo:                                             │
│     • GET /fixtures?id={fixture_id} na API-Football            │
│     • Extrai resultado (score)                                  │
│     • Compara com previsão                                      │
│     • Atualiza status: WON ou LOST                             │
│  4. Recalcula estatísticas (ROI, hit rate)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Estrutura (Application Layer)

```python
# application/contracts/result_checker_service_contract.py

class ResultCheckerServiceContract(ABC):
    
    @abstractmethod
    def check_pending_predictions(self) -> int:
        """Verifica previsões pendentes e retorna quantidade atualizada"""
        pass
    
    @abstractmethod
    def verify_single_prediction(self, prediction_id: str) -> bool:
        """Verifica uma previsão específica"""
        pass
```

### Regras de Verificação por Mercado

| Mercado | Previsão | Condição de Acerto |
|---------|----------|-------------------|
| 1X2 | HOME (1) | home_score > away_score |
| 1X2 | DRAW (X) | home_score == away_score |
| 1X2 | AWAY (2) | away_score > home_score |
| Over 2.5 | OVER | total_goals > 2 |
| Over 2.5 | UNDER | total_goals < 3 |
| BTTS | YES | home_score > 0 AND away_score > 0 |
| BTTS | NO | home_score == 0 OR away_score == 0 |

---

## 🚀 Próximos Passos

1. [ ] Configurar conta na API-Football (RapidAPI)
2. [ ] Implementar Domain Models e Contracts
3. [ ] Implementar Infrastructure (DB, API-Football Client)
4. [ ] Implementar Application Services
5. [ ] Implementar Result Checker Service + Scheduler
6. [ ] Implementar Web Layer (Controllers, DTOs)
7. [ ] Implementar Web App React
8. [ ] Testes unitários e integração
9. [ ] Deploy

---

*Documento gerado em 2026-02-14*

