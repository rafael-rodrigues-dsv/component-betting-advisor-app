# 🔌 Integração com API-Football

> Documentação do fluxo de integração com a API-Football — dados reais, sem mocks.

**Versão:** 4.0.0  
**Status:** ✅ Produção

---

## 📊 Visão Geral

O **Betting Advisor** utiliza a API-Football como fonte de dados para:
- ✅ Buscar fixtures (jogos) por liga, data e season
- ✅ Obter odds de múltiplas casas de apostas (Bet365, Betano)
- ✅ Consultar status e resultados de partidas
- ✅ Resolver season atual de cada liga automaticamente
- ✅ Cachear dados em SQLite para otimizar requests

**Base URL:** `https://v3.football.api-sports.io`  
**Autenticação:** `x-rapidapi-key` header  
**Limite:** 100 requests/dia (plano gratuito)

---

## 🔄 Diagrama de Fluxo Principal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     FLUXO PRINCIPAL — BETTING ADVISOR                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐                                                          │
│  │   USUÁRIO    │                                                          │
│  └──────┬───────┘                                                          │
│         │ 1. Clica "3 Dias" na tela de Jogos                               │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  FRONTEND (React)                    │                                  │
│  │  • POST /api/v1/preload/fetch?days=3 │                                  │
│  └──────┬───────────────────────────────┘                                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  PreloadService                      │                                  │
│  │  • Verifica cache incremental        │                                  │
│  │  • Para cada liga × data:            │                                  │
│  └──────┬───────────────────────────────┘                                  │
│         │                                                                   │
│         │ 2. Resolve season da liga                                         │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  CacheManager (SQLite)               │                                  │
│  │  • Busca: season:{league_id}         │                                  │
│  │  • Cache HIT? → usa season cacheada  │                                  │
│  │  • Cache MISS? → API-Football ↓      │                                  │
│  └──────┬───────────────────────────────┘                                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  📡 API-FOOTBALL                     │                                  │
│  │  GET /leagues?id=71&current=true     │ → Resolve season                 │
│  │  GET /fixtures?league=71&date=...    │ → Busca fixtures                 │
│  │    &season=2026                      │                                  │
│  └──────┬───────────────────────────────┘                                  │
│         │                                                                   │
│         │ 3. Parse + Cache                                                  │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  fixture_parser.py                   │                                  │
│  │  • Parse JSON → dict                 │                                  │
│  │  • Converte timezone → local         │                                  │
│  │  • Verifica logo local (escudos/)    │                                  │
│  │  • Salva em SQLite cache (TTL 6h)    │                                  │
│  └──────────────────────────────────────┘                                  │
│                                                                             │
│  ───── ODDS (separado, após preload) ─────                                 │
│                                                                             │
│  ┌──────────────────────────────────────┐                                  │
│  │  Frontend: POST /matches/odds/batch  │                                  │
│  │  (chunks de 10 partidas)             │                                  │
│  └──────┬───────────────────────────────┘                                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  📡 API-FOOTBALL                     │                                  │
│  │  GET /odds?fixture={id}              │                                  │
│  └──────┬───────────────────────────────┘                                  │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────┐                                  │
│  │  odds_parser.py                      │                                  │
│  │  • Parse odds de todas as casas      │                                  │
│  │  • match_application_service filtra  │                                  │
│  │    apenas SUPPORTED_BOOKMAKERS       │                                  │
│  │  • Salva em SQLite cache (TTL 30min) │                                  │
│  └──────────────────────────────────────┘                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📡 Endpoints Usados

| # | Endpoint API-Football | Uso no Sistema | Quando |
|---|---|---|---|
| 1 | `GET /leagues?id={id}&current=true` | Resolver season atual | Primeiro acesso à liga (cache 7 dias) |
| 2 | `GET /fixtures?league={id}&date={date}&season={year}` | Buscar fixtures | Preload sob demanda (cache 6h) |
| 3 | `GET /odds?fixture={id}` | Buscar odds | Batch após preload + refresh individual (cache 30min) |
| 4 | `GET /fixtures?id={id}` | Status/resultado | Refresh individual + atualizar bilhetes |

---

## 🔢 Contagem de Requests

### Preload de 3 dias (7 ligas)

```
Season resolution: até 7 requests (se nenhum cacheado)
Fixtures: 7 ligas × 3 datas = 21 requests
Odds batch: N fixtures × 1 request cada
─────────────────────────
Total máximo: 7 + 21 + N odds
```

### Otimizações

- **Season cache:** 7 dias TTL → 0 requests após primeiro acesso
- **Fixtures cache:** 6h TTL → 0 requests se dados recentes
- **Odds cache:** 30min TTL → 0 requests se odds recentes
- **Cache incremental:** 3→7 dias busca apenas dias 4-7 (não re-busca 1-3)
- **Preload SEM odds:** Fixtures e odds são fluxos separados

---

## 🗄️ Chaves de Cache

| Chave | Conteúdo | TTL |
|-------|----------|-----|
| `season:{league_id}` | Ano da season (ex: 2026) | 7 dias |
| `fixtures:{league_id}:{date}` | Lista de fixtures JSON | 6 horas |
| `odds:{fixture_id}` | Odds de todas as casas | 30 minutos |
| `preload:last_date` | Última data base do preload | 24 horas |
| `preload:last_days` | Último período carregado | 24 horas |

---

## 🏟️ Season Resolution

A API-Football requer `season` para fixtures. O sistema resolve automaticamente:

```python
# APIFootballService._get_current_season(league_id)
1. Verifica cache: season:{league_id}
2. Se cache MISS:
   → GET /leagues?id={league_id}&current=true
   → Extrai seasons[0].year
   → Cacheia por 7 dias
3. Retorna: ex. 2026 (BR) ou 2025 (Europa 2025/2026)
```

---

## 🎰 Filtro de Bookmakers

```
API-Football → odds_parser → TODAS as casas (12+)
                    ↓
match_application_service → filtra SUPPORTED_BOOKMAKERS
                    ↓
Frontend recebe: apenas bet365 e betano
```

Configurável em `.env`:
```
SUPPORTED_BOOKMAKERS=bet365,betano
```

---

## 🔄 Refresh Individual

```
POST /api/v1/matches/{id}/odds/refresh
    ↓
1. Deleta cache: odds:{fixture_id}
2. GET /odds?fixture={id} → API-Football
3. GET /fixtures?id={id} → status atualizado
4. Cacheia novas odds (30min TTL)
5. Retorna: { odds, status, status_short }
```

---

## ⚠️ Limitações

| Item | Detalhe |
|------|---------|
| Limite gratuito | 100 requests/dia |
| Odds disponíveis | Depende da partida e horário |
| Latência | ~500ms por request |
| Partidas sem odds | Retorna vazio (frontend trata) |
| Season errada | Retorna 0 fixtures (sistema loga warning) |
