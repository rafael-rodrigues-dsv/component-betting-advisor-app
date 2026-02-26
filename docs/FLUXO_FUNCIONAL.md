# 🔄 Betting Advisor - Fluxo Funcional

> Fluxo funcional real implementado — API-Football integrada, sem mocks

**Data:** 2026-02-26  
**Versão:** 4.0.0  
**Status:** ✅ Produção (API-Football Real)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Fluxo do Usuário](#fluxo-do-usuário)
3. [Fluxo 1: Dashboard](#fluxo-1-dashboard)
4. [Fluxo 2: Carregar Jogos por Período](#fluxo-2-carregar-jogos-por-período)
5. [Fluxo 3: Visualizar Jogos e Odds](#fluxo-3-visualizar-jogos-e-odds)
6. [Fluxo 4: Analisar Jogos](#fluxo-4-analisar-jogos)
7. [Fluxo 5: Previsões e Comparação de Casas](#fluxo-5-previsões-e-comparação-de-casas)
8. [Fluxo 6: Criar Bilhete](#fluxo-6-criar-bilhete)
9. [Fluxo 7: Acompanhar Bilhetes](#fluxo-7-acompanhar-bilhetes)
10. [Detalhes Técnicos](#detalhes-técnicos)

---

## 🎯 Visão Geral

O sistema segue um fluxo sob demanda com carregamento incremental:

```
Selecionar Período → Preload Fixtures → Batch Odds → Seleção → Análise → Estratégia → Comparar Casas → Bilhete
       ↓                   ↓                ↓           ↓         ↓          ↓               ↓              ↓
  3/7/14 dias       API-Football      Cache + API    Filtros   CONSERVATIVE  Re-analisa    Bet365 vs      Confirmar
                   (só fixtures)     (por partida)             como default  ao trocar     Betano
```

### ⚡ Carregamento Sob Demanda (Sem auto-load no startup)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              🚀 CARREGAMENTO SOB DEMANDA (POST /api/v1/preload/fetch)       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  QUANDO: Usuário clica em 3, 7 ou 14 dias na tela de Jogos                │
│                                                                             │
│  ETAPA 1 — PRELOAD (fixtures, SEM odds):                                   │
│  • Busca fixtures das 7 ligas na API-Football                              │
│  • Cache incremental: 3→7 reaproveita, 7→14 reaproveita                   │
│  • Fixtures cacheados em SQLite (TTL 6h)                                   │
│  • Filtra apenas partidas ativas (NS, 1H, 2H, HT, etc.)                   │
│                                                                             │
│  ETAPA 2 — ODDS (batch automático após preload):                           │
│  • Dispara carregamento de odds para TODAS as partidas                     │
│  • Chunks de 10 partidas por vez (não bloqueia UI)                         │
│  • Odds cacheadas em SQLite (TTL 30min)                                    │
│  • Filtro: apenas Bet365 e Betano (SUPPORTED_BOOKMAKERS)                   │
│                                                                             │
│  ETAPA 3 — REFRESH (sob demanda por partida):                              │
│  • Botão 🔄 em cada partida atualiza odds + status                        │
│  • Deleta cache da partida e busca da API novamente                        │
│                                                                             │
│  🇧🇷 Ligas:                                                                 │
│  • Brasileirão Série A (71) • Copa do Brasil (73)                          │
│                                                                             │
│  🇪🇺 Europa — Top 5:                                                        │
│  • Premier League (39) • La Liga (140) • Bundesliga (78)                   │
│  • Ligue 1 (61) • Serie A Itália (135)                                     │
│                                                                             │
│  🏠 Casas de Apostas: Bet365, Betano                                       │
│                                                                             │
│  ⏰ Timezone: America/Sao_Paulo (configurável via .env)                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cache Incremental

```
Clicou 3 dias  → Busca fixtures dias 1-3 na API → Salva cache "3 dias"
Clicou 7 dias  → Já tem 3 dias no cache → Busca apenas dias 4-7
Clicou 14 dias → Já tem 7 dias no cache → Busca apenas dias 8-14
Clicou 3 dias  → Cache de 7 já cobre → Não faz nenhum request
```

---

## 👤 Fluxo do Usuário

### Jornada Completa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     🎰 BETTING ADVISOR — FLUXO COMPLETO                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌──────────────���──┐
│  📊 DASHBOARD │         │  ⚽ JOGOS        │         │  🎫 BILHETES    │
│  Estatísticas │         │  Período → Odds │         │  Histórico      │
│  dos bilhetes │         │  Filtro Liga    │         │  Status partida │
└───────────────┘         │  Select All/Day │         └─────────────────┘
                          └────────┬────────┘
                                   │ Analisar (default: Conservadora)
                          ┌────────▼────────┐
                          │  🎯 PREVISÕES    │
                          │  Trocar estratég.│
                          │  Resumo compacto │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │  🔄 COMPARAÇÃO   │
                          │  Bet365 vs Betano│
                          │  Recomendação    │
                          └────────┬────────┘
                                   │ "Usar X"
                          ┌────────▼────────┐
                          │  ✅ BILHETE      │
                          │  Editar, excluir │
                          │  Stake → Criar   │
                          └─────────────────┘
```

---

## 📊 Fluxo 1: Dashboard

### Objetivo
Visão geral das estatísticas dos bilhetes do usuário.

### Sequência

```
1. Usuário acessa http://localhost:5173
2. Frontend carrega → GET /api/v1/tickets/stats/dashboard
3. Backend retorna estatísticas reais dos bilhetes salvos no SQLite
4. Dashboard.tsx renderiza:
   ├─ 4 cards: Total, Ganhos, Perdas, Pendentes
   ├─ 3 cards: Taxa de Acerto, Total Apostado, Lucro
   └─ QuickGuide (guia rápido)
```

### Componentes Envolvidos

```typescript
// Dashboard.tsx
const Dashboard = () => {
  const [stats, setStats] = useState(null);
  
  useEffect(() => {
    loadStats(); // GET /api/v1/tickets/stats/dashboard
  }, []);
  
  return (
    <>
      <StatsCard title="Total de Bilhetes" value={stats.total_tickets} />
      <StatsCard title="Bilhetes Ganhos" value={stats.won_tickets} />
      // ... mais stats
      <QuickGuide />
    </>
  );
};
```

---

## ⚽ Fluxo 2: Carregar Jogos por Período

### Objetivo
Usuário escolhe período (3, 7 ou 14 dias) para carregar fixtures da API-Football.

### Sequência

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Usuário clica na aba "Jogos"                                             │
│    └─ Vê o seletor de período: [⚡ 3 Dias] [📅 7 Dias] [📆 14 Dias]        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Usuário clica em "3 Dias" (exemplo)                                      │
│    └─ useMatches.fetchByPeriod(3)                                           │
│       ├─ Cancela batch de odds anterior (se existir)                        │
│       ├─ POST /api/v1/preload/fetch?days=3                                  │
│       │   → Backend: PreloadService.preload_main_leagues(3)                 │
│       │   → Verifica cache incremental                                      │
│       │   → Busca fixtures das 7 ligas × 3 datas na API-Football            │
│       │   → Resolve season correta de cada liga via GET /leagues             │
│       │   → Salva no SQLite cache (TTL 6h)                                  │
│       │   → NÃO carrega odds (apenas fixtures)                              │
│       │   → Retorna { date_from, date_to }                                  │
│       │                                                                      │
│       ├─ GET /api/v1/matches?date_from=...&date_to=...                      │
│       │   → Backend lê fixtures do cache                                    │
│       │   → Filtra apenas partidas ativas (ACTIVE_STATUSES)                 │
│       │   → Retorna matches SEM odds                                        │
│       │                                                                      │
│       ├─ GET /api/v1/leagues                                                │
│       ├─ GET /api/v1/bookmakers                                             │
│       │                                                                      │
│       └─ Dispara loadAllOdds(matches) em background                         │
│          → POST /api/v1/matches/odds/batch (chunks de 10)                   │
│          → Cada fixture: busca odds na API ou cache                         │
│          → Filtra apenas Bet365 e Betano                                    │
│          → Atualiza state dos matches com odds                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Tela exibe jogos agrupados por data                                      │
│    ├─ Header por data: "Hoje — quarta-feira, 26 de fevereiro" (expandível) │
│    ├─ Checkbox por data: selecionar todos do dia                            │
│    ├─ MatchCard por jogo                                                    │
│    └─ Barra de progresso: "📊 Carregando odds: 15/39"                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Timezone

O sistema usa `settings.today()` com timezone `America/Sao_Paulo` (configurável via `TIMEZONE` no `.env`). Garante que o período sempre inclua a data atual do usuário.

---

## 🔎 Fluxo 3: Visualizar Jogos e Odds

### Filtros na Tela de Jogos

| Filtro | Tipo | Descrição |
|--------|------|-----------|
| 🏆 Campeonato | Dropdown | Todos ou liga específica (client-side) |

> **Nota:** O filtro de estratégia foi movido para a tela de Previsões (v4.0).

### Seleção de Jogos

| Ação | Descrição |
|------|-----------|
| Checkbox no jogo | Seleciona/deseleciona individualmente |
| Checkbox no header de data | Seleciona/deseleciona todos do dia |
| Botão "Selecionar Todos" | Seleciona todos os jogos carregados |
| Botão "Deselecionar Todos" | Limpa seleção |

### MatchCard — Tabela Comparativa de Odds

Cada partida exibe tabela com odds de todas as casas suportadas, com melhor odd destacada em verde:

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🇧🇷 Brasileirão Série A • Rodada 5          [Não iniciado]         │
│ 📅 qua, 26 fev   🕐 20:00                                         │
│                                                                     │
│    🔴 Flamengo          vs          Palmeiras 🟢                   │
│                                                                     │
│ 🏟️ Maracanã                                                        │
│                                                                     │
│ 📊 Comparativo de Odds                               [🔄]          │
│ ┌──────────┬────────┬────────┬────────┐                             │
│ │ Casa     │   1    │   X    │   2    │                             │
│ ├──────────┼────────┼────────┼────────┤                             │
│ │ 🟢 Bet365│  2.10  │  3.20  │  2.80  │                             │
│ │ 🟡 Betano│ *2.15* │ *3.25* │  2.75  │  ← verde = melhor odd      │
│ └──────────┴────────┴────────┴────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

### Refresh de Odds (Botão 🔄)

```
1. Clica 🔄 → POST /api/v1/matches/{id}/odds/refresh
2. Backend deleta cache de odds → busca API → busca status
3. Retorna { odds, status, status_short }
4. Frontend atualiza MatchCard (odds + badge de status)
```

---

## 🧠 Fluxo 4: Analisar Jogos

### Sequência

```
1. Seleciona jogos (checkbox em jogo, por dia, ou todos)
2. Clica "Analisar Selecionados"
   └─ POST /api/v1/analyze { match_ids, strategy: "CONSERVATIVE" }
   └─ Estratégia default: CONSERVATIVE (o seletor está na tela de Previsões)

3. Backend — PredictionApplicationService + OddsAnalyzer:
   ├─ Busca fixtures e odds do cache
   ├─ Analisa por estratégia (CONSERVATIVE/BALANCED/VALUE_BET/AGGRESSIVE)
   ├─ Gera previsões com múltiplos mercados (1X2, Over/Under, BTTS)
   ├─ Diversifica recomendações (evita repetir mesmo mercado)
   ├─ Retorna odds_by_bookmaker por partida (para comparação)
   └─ Cria pré-bilhete automaticamente

4. Frontend navega automaticamente para aba "Previsões"
```

---

## 🎯 Fluxo 5: Previsões e Comparação de Casas

### Tela de Previsões (3 seções)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 1: SELETOR DE ESTRATÉGIA                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ 🛡️ Conserv.  │ │ ⚖️ Balancead.│ │ 💰 Value Bet │ │ 🔥 Agressiva │       │
│  │  [ATIVA]     │ │              │ │              │ │              │       │
│  │ Menos risco  │ │ Equilíbrio   │ │ Foco em EV   │ │ Mais risco   │       │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                                             │
│  Trocar estratégia → re-analisa os MESMOS jogos com nova estratégia         │
│  (POST /api/v1/analyze { match_ids, strategy: "VALUE_BET" })               │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 2: RESUMO COMPACTO DAS PREVISÕES                                     │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Flamengo vs Palmeiras                            Brasileirão Série A │  │
│  │ ⚽ Resultado   🏠 Vitória Mandante   @ 2.10   55%   🔥 Forte        │  │
│  │ 🎯 Total Gols  ⬆️ Mais de 2.5       @ 1.85   52%   ✅ Recomendada  │  │
│  │ ⚡ Ambos Marc. ✅ Sim                @ 1.72   48%   💭 Considerar   │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Vasco vs Corinthians                             Brasileirão Série A │  │
│  │ ...                                                                  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 3: COMPARAÇÃO DE BILHETES — QUAL CASA PAGA MELHOR?                   │
│                                                                             │
│  ┌───────────────────────┐    ┌───────────────────────┐                     │
│  │ 🟢 Bet365             │    │ 🟡 Betano     ⭐ MELHOR│                    │
│  │                       │    │                       │                     │
│  │ Flamengo vs Palmeiras │    │ Flamengo vs Palmeiras │                     │
│  │ Resultado: Casa @2.10 │    │ Resultado: Casa @2.15 │                     │
│  │                       │    │                       │                     │
│  │ Vasco vs Corinthians  │    │ Vasco vs Corinthians  │                     │
│  │ Over 2.5 gols  @1.85  │    │ Over 2.5 gols  @1.90  │                    │
│  │                       │    │                       │                     │
│  │ Odd Combinada: 3.89   │    │ Odd Combinada: 4.09   │                     │
│  │ Retorno: R$ 194.25    │    │ Retorno: R$ 204.25    │                     │
│  │                       │    │                       │                     │
│  │ [✅ Usar Bet365]      │    │ [✅ Usar Betano]      │                     │
│  └───────────────────────┘    └───────────────────────┘                     │
│                                                                             │
│  💡 Recomendação: Betano paga +5.1% melhor (R$ 10.00 a mais com R$ 50)     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ "Usar Betano"
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 4: BILHETE MONTADO (após escolher casa)                               │
│                                                                             │
│  🎫 Novo Bilhete                                    🎰 BETANO              │
│  ├─ Flamengo vs Palmeiras — Resultado: Casa @ 2.15  [×]                    │
│  ├─ Vasco vs Corinthians — Over 2.5 gols @ 1.90     [×]                    │
│  │                                                                          │
│  │ Apostas: 2 | Odd Combinada: 4.09 | Retorno: R$ 204.25                  │
│  │ Valor (R$): [50.00]                                                     │
│  │                                                                          │
│  │ [Limpar] [Criar Bilhete]                                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Estratégias

| Estratégia | Critério | Risco |
|-----------|----------|-------|
| 🛡️ CONSERVATIVE | Favoritos seguros (odd 1.50–2.00) | Baixo |
| ⚖️ BALANCED | Favorito + value ≥3% | Médio |
| 💰 VALUE_BET | Diferença entre casas ≥5% | Médio-Alto |
| 🔥 AGGRESSIVE | Odds altas / zebras (≥2.50) | Alto |

---

## 🎫 Fluxo 6: Criar Bilhete

```
1. Na tela de Previsões, escolhe a casa na comparação ("Usar Betano")
2. Bilhete é montado automaticamente com odds da casa escolhida
3. Pode remover apostas individualmente (botão ×)
4. Define valor da aposta (stake)
5. Clica "Criar Bilhete"
   └─ POST /api/v1/tickets { name, stake, bookmaker_id, bets }
6. Backend: gera UUID, calcula odds combinadas, salva no SQLite
7. Frontend: notificação de sucesso → navega para "Bilhetes"
```

---

## 🎫 Fluxo 7: Acompanhar Bilhetes

```
1. Aba "Bilhetes" → GET /api/v1/tickets
2. TicketHistory renderiza por status (PENDENTE / GANHOU / PERDEU)
3. Cada aposta exibe badge de status da partida:
   ├─ ⚪ Não iniciado (NS)
   ├─ 🔴 Ao vivo (1H, 2H, HT, etc.)
   ├─ ⚫ Encerrado (FT)
   ├─ 🟡 Suspenso (SUSP)
   └─ ⚪ A definir (TBD)
4. "Atualizar Resultados" → POST /api/v1/tickets/update-results
   ├─ Busca resultado real na API-Football (GET /fixtures?id=X)
   ├─ Compara com aposta → atualiza status/status_short
   └─ Calcula lucro/prejuízo
```

---

## 🔧 Detalhes Técnicos

### Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/preload/fetch?days=N` | POST | Pré-carrega fixtures (3, 7, 14 dias) |
| `/api/v1/preload/status` | GET | Status do cache |
| `/api/v1/matches` | GET | Lista jogos (do cache, com filtros de data) |
| `/api/v1/matches/{id}/odds` | GET | Odds de uma partida |
| `/api/v1/matches/{id}/odds/refresh` | POST | Refresh odds + status |
| `/api/v1/matches/odds/batch` | POST | Odds em lote (chunks) |
| `/api/v1/leagues` | GET | Lista campeonatos |
| `/api/v1/bookmakers` | GET | Lista casas de apostas |
| `/api/v1/analyze` | POST | Analisa jogos (retorna odds_by_bookmaker) |
| `/api/v1/tickets` | GET | Lista bilhetes (com status partidas) |
| `/api/v1/tickets` | POST | Cria bilhete |
| `/api/v1/tickets/{id}` | GET | Detalhes de um bilhete |
| `/api/v1/tickets/{id}` | DELETE | Deleta bilhete |
| `/api/v1/tickets/stats/dashboard` | GET | Estatísticas |
| `/api/v1/tickets/update-results` | POST | Atualiza resultados + status reais |

### Sistema de Cache (SQLite)

| Tipo | TTL | Chave |
|------|-----|-------|
| Fixtures | 6 horas | `fixtures:{league_id}:{date}` |
| Odds | 30 minutos | `odds:{fixture_id}` |
| Season | 7 dias | `season:{league_id}` |
| Preload meta | 24 horas | `preload:last_date`, `preload:last_days` |

### Configurações (.env)

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `API_FOOTBALL_KEY` | — | Chave da API-Football (obrigatória) |
| `TIMEZONE` | `America/Sao_Paulo` | Timezone para cálculo de datas |
| `SUPPORTED_BOOKMAKERS` | `bet365,betano` | Casas de apostas filtradas |
| `MAIN_LEAGUES` | `71,73,39,140,78,61,135` | IDs das ligas |
| `CACHE_TTL_FIXTURES` | `21600` | TTL fixtures (6h) |
| `CACHE_TTL_ODDS` | `1800` | TTL odds (30min) |

### Status de Partidas

| Ativos (exibidos) | Encerrados (filtrados) |
|---|---|
| NS, 1H, 2H, HT, ET, BT, P, SUSP, INT, LIVE, TBD | FT, AET, PEN, WO, AWD, CANC, ABD, PST |
