# 🔄 Betting Advisor - Fluxo Funcional

> Fluxo funcional real implementado — API-Football integrada, sem mocks

**Data:** 2026-02-27  
**Versão:** 5.0.0  
**Status:** ✅ Produção (API-Football Real)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Fluxo do Usuário](#fluxo-do-usuário)
3. [Fluxo 1: Dashboard](#fluxo-1-dashboard)
4. [Fluxo 2: Carregar Jogos por Período](#fluxo-2-carregar-jogos-por-período)
5. [Fluxo 3: Carrossel de Ligas e Odds](#fluxo-3-carrossel-de-ligas-e-odds)
6. [Fluxo 4: Filtros Avançados](#fluxo-4-filtros-avançados)
7. [Fluxo 5: Analisar Jogos](#fluxo-5-analisar-jogos)
8. [Fluxo 6: Previsões e Comparação de Casas](#fluxo-6-previsões-e-comparação-de-casas)
9. [Fluxo 7: Criar Bilhete (Modal)](#fluxo-7-criar-bilhete-modal)
10. [Fluxo 8: Acompanhar Bilhetes ao Vivo](#fluxo-8-acompanhar-bilhetes-ao-vivo)
11. [Detalhes Técnicos](#detalhes-técnicos)

---

## 🎯 Visão Geral

O sistema segue um fluxo sob demanda com carregamento incremental:

```
Período → Preload Fixtures → Carrossel Ligas → Odds por Liga → Filtros → Seleção → Análise → Modal → Bilhete
   ↓            ↓                 ↓                 ↓             ↓         ↓         ↓         ↓        ↓
Hoje/3/7   API-Football      Multi-select       Por liga/data   Status   Checkbox   3 Estrat.  Editar  Ao vivo
           (só fixtures)     + busca + filtro    (bulk API)     Odds/etc            Trocar mkt  placar
```

### ⚡ Carregamento Sob Demanda

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              🚀 CARREGAMENTO SOB DEMANDA                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  QUANDO: Usuário clica em Hoje, 3 ou 7 dias na tela de Jogos              │
│                                                                             │
│  ETAPA 1 — PRELOAD (fixtures, SEM odds):                                   │
│  • Busca fixtures de TODAS as ligas na API-Football                        │
│  • Cache incremental: Hoje→3 reaproveita, 3→7 reaproveita                 │
│  • Fixtures cacheados em SQLite (TTL 6h)                                   │
│  • Filtra apenas partidas ativas (NS, 1H, 2H, HT, etc.)                   │
│  • Carrega ligas disponíveis no carrossel                                   │
│                                                                             │
│  ETAPA 2 — ODDS POR LIGA (sob demanda ao selecionar no carrossel):         │
│  • Usuário seleciona liga(s) no carrossel                                  │
│  • POST /api/v1/preload/odds/league { league_id }                          │
│  • Busca GET /odds?league={id}&date={date} na API-Football (bulk)          │
│  • Muito mais eficiente que 1 request por fixture                          │
│  • Odds cacheadas em SQLite (TTL 30min)                                    │
│                                                                             │
│  ETAPA 3 — REFRESH (sob demanda por partida):                              │
│  • Botão 🔄 em cada partida atualiza odds + status                        │
│  • Deleta cache da partida e busca da API novamente                        │
│                                                                             │
│  🏠 Casas de Apostas: Bet365, Betano                                       │
│  ⏰ Timezone: America/Sao_Paulo (configurável via .env)                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Cache Incremental

```
Clicou Hoje   → Busca fixtures do dia na API → Salva cache "1 dia"
Clicou 3 dias → Já tem Hoje no cache → Busca apenas dias 2-3
Clicou 7 dias → Já tem 3 dias no cache → Busca apenas dias 4-7
Clicou Hoje   → Cache de 3 já cobre → Não faz nenhum request
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
┌───────────────┐         ┌─────────────────────┐       ┌─────────────────┐
│  📊 DASHBOARD │         │  ⚽ JOGOS            │       │  🎫 BILHETES    │
│  Estatísticas │         │  Período Hoje/3/7   │       │  Histórico      │
│  dos bilhetes │         │  Carrossel de ligas │       │  Placar ao vivo │
└───────────────┘         │  Filtros avançados  │       │  Minuto/Barra   │
                          │  Odds por liga      │       │  Ganho/Perdendo │
                          └─────────┬───────────┘       └─────────────────┘
                                    │ Analisar (default: Conservadora)
                          ┌─────────▼───────────┐
                          │  🎯 PREVISÕES        │
                          │  3 Estratégias       │
                          │  Todas as odds/mkt   │
                          │  Resumo compacto     │
                          └─────────┬───────────┘
                                    │
                          ┌─────────▼───────────┐
                          │  🔄 COMPARAÇÃO       │
                          │  Bet365 vs Betano    │
                          │  Recomendação        │
                          └─────────┬───────────┘
                                    │ "Usar X" → Modal
                          ┌─────────▼───────────┐
                          │  🎫 MODAL BILHETE    │
                          │  Editar apostas      │
                          │  Trocar mercados     │
                          │  Stake → Criar       │
                          └─────────────────────┘
```

---

## 📊 Fluxo 1: Dashboard

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

---

## ⚽ Fluxo 2: Carregar Jogos por Período

### Sequência

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. Usuário clica na aba "Jogos"                                             │
│    └─ Vê o seletor de período: [📅 Hoje] [⚡ 3 Dias] [📆 7 Dias]           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Usuário clica em "3 Dias" (exemplo)                                      │
│    └─ useMatches.fetchByPeriod(3)                                           │
│       ├─ POST /api/v1/preload/fetch?days=3                                  │
│       │   → Backend: PreloadService.preload_fixtures(3)                     │
│       │   → Verifica cache incremental                                      │
│       │   → Busca fixtures de TODAS as ligas × 3 datas na API-Football      │
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
│       └─ GET /api/v1/matches/live (polling a cada 5s)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Tela exibe carrossel de ligas (sem jogos visíveis até selecionar)        │
│    ├─ Seção "Ao Vivo" com ligas que têm jogos em andamento                 │
│    ├─ Seção principal com TODAS as ligas (filtráveis por país/tipo)         │
│    ├─ Busca por nome de liga                                               │
│    └─ Multi-select (pode selecionar várias ligas)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎠 Fluxo 3: Carrossel de Ligas e Odds

### Carrossel Multi-Select

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🏆 Ligas Disponíveis (534)            🔍 [Buscar liga...]                  │
│                                                                             │
│ 🔴 AO VIVO ─────────────────────────────────────                           │
│ ┌─────────┐ ┌─────────┐                                                   │
│ │ 🏆 AFC  │ │ 🏆 Copa │ ← Ligas com jogos ao vivo                       │
│ │ Cup     │ │ do Rei  │                                                   │
│ │ 2 jogos │ │ 1 jogo  │                                                   │
│ └─────────┘ └─────────┘                                                   │
│                                                                             │
│ Filtros: [Todas] [Ligas] [Copas]     País: [Todas] [Brazil] [England]...  │
│                                                                             │
│ ◄ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ... ►     │
│   │ 🇧🇷 Bras.│ │ 🇬🇧 Prem.│ │ 🇪🇸 La  │ │ 🇩🇪 Bund.│ │ 🇫🇷 Ligu.│          │
│   │ Série A │ │ League  │ │ Liga   │ │ esliga │ │ e 1    │          │
│   │ [SEL]   │ │ 12 jogos│ │ 10 jgs │ │  9 jgs │ │  9 jgs │          │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│                                                                             │
│ ✅ 1 liga selecionada: Brasileirão Série A (12 jogos)    [Limpar]          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Carregamento de Odds ao Selecionar Liga

```
1. Usuário seleciona "Brasileirão Série A" no carrossel
2. Frontend dispara: POST /api/v1/preload/odds/league { league_id: 71 }
3. Backend:
   ├─ Identifica datas do período atual (ex: 2026-02-27 a 2026-03-01)
   ├─ Para cada data: GET /odds?league=71&date=YYYY-MM-DD (paginado)
   ├─ Parseia odds, cacheia por fixture
   └─ Retorna total de fixtures com odds
4. Frontend recarrega matches → jogos agora têm odds
5. Ligas sem odds: jogos ficam desabilitados (não selecionáveis)
```

---

## 🔎 Fluxo 4: Filtros Avançados

### Painel de Filtros

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔍 Filtros                                                    [Limpar]     │
│                                                                             │
│ 📊 Status:    [Ao Vivo] [Não Iniciado] [Encerrado] [Suspenso]             │
│ 💰 Odds:      [Todas] [Com Odds] [Sem Odds]                               │
│ 🔄 Rodada:    [Todas] [Rodada 5] [Rodada 6] [...]                         │
│ 📅 Data:      [Todas] [27/02] [28/02] [01/03]                             │
│ 🕐 Horário:   [Todos] [Manhã] [Tarde] [Noite] [Madrugada]                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Regras

- Jogos sem odds disponíveis **não podem** ser selecionados para análise
- Filtros são client-side (não fazem requests)
- Ligas com 0 jogos não aparecem no carrossel
- Carrossel ordenado alfabeticamente

---

## 🧠 Fluxo 5: Analisar Jogos

### Sequência

```
1. Seleciona jogos (apenas jogos COM odds disponíveis)
   ├─ Checkbox em jogo individual
   ├─ Checkbox no header de data (seleciona todos do dia)
   └─ Botão "Selecionar Todos"

2. Clica "Analisar Selecionados"
   └─ POST /api/v1/analyze { match_ids, strategy: "CONSERVATIVE" }

3. Backend — PredictionApplicationService + OddsAnalyzer:
   ├─ Busca fixtures e odds do cache
   ├─ Analisa por estratégia (CONSERVATIVE/BALANCED/AGGRESSIVE)
   ├─ Gera previsões com múltiplos mercados (1X2, Over/Under, BTTS)
   ├─ Diversifica recomendações
   ├─ Retorna odds_by_bookmaker por partida
   └─ Cria pré-bilhete automaticamente

4. Frontend navega para aba "Previsões"
```

---

## 🎯 Fluxo 6: Previsões e Comparação de Casas

### Tela de Previsões (4 seções)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 1: SELETOR DE ESTRATÉGIA                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                        │
│  │ 🛡️ Conserv.  │ │ ⚖️ Balancead.│ │ 🔥 Agressiva │                        │
│  │  [ATIVA]     │ │              │ │              │                        │
│  │ Menos risco  │ │ Equilíbrio   │ │ Mais risco   │                        │
│  └──────────────┘ └──────────────┘ └──────────────┘                        │
│                                                                             │
│  Trocar estratégia → re-analisa os MESMOS jogos com nova estratégia         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 2: RESUMO — TODAS AS ODDS DE CADA MERCADO                           │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Flamengo vs Palmeiras                            Brasileirão Série A │  │
│  │                                                                       │  │
│  │ ⚽ Resultado Final                                                    │  │
│  │   🏠 Mandante @ 2.10  55% +8% EV ✅ Recomendada                     │  │
│  │   🤝 Empate   @ 3.40  —                                              │  │
│  │   ✈️ Visitante @ 3.00  —                                              │  │
│  │                                                                       │  │
│  │ 🎯 Total de Gols                                                     │  │
│  │   ⬆️ Mais 2.5  @ 1.85  52% +5% EV ✅ Recomendada                    │  │
│  │   ⬇️ Menos 2.5 @ 1.95  —                                             │  │
│  │                                                                       │  │
│  │ ⚡ Ambos Marcam                                                       │  │
│  │   ✅ Sim       @ 1.72  48% +3% EV 💭 Considerar                     │  │
│  │   ❌ Não       @ 2.05  —                                              │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│  (Exibe TODAS as opções — recomendadas e não recomendadas)                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SEÇÃO 3: COMPARAÇÃO DE BILHETES — QUAL CASA PAGA MELHOR?                   │
│                                                                             │
│  ┌───────────────────────┐    ┌───────────────────────┐                     │
│  │ 🟢 Bet365             │    │ 🟡 Betano     ⭐ MELHOR│                    │
│  │ Odd Combinada: 3.89   │    │ Odd Combinada: 4.09   │                     │
│  │ Retorno: R$ 194.25    │    │ Retorno: R$ 204.25    │                     │
│  │ [✅ Usar Bet365]      │    │ [✅ Usar Betano]      │                     │
│  └───────────────────────┘    └───────────────────────┘                     │
│                                                                             │
│  💡 Recomendação: Betano paga +5.1% melhor                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ "Usar Betano" → abre Modal
                                    ▼
```

### Estratégias

| Estratégia | Ordenação | Risco |
|-----------|-----------|-------|
| 🛡️ CONSERVATIVE | Por confiança (maior → menor) | Baixo |
| ⚖️ BALANCED | `EV × 0.5 + Confiança × 0.5` | Médio |
| 🔥 AGRESSIVE | `Odds × Confiança` | Alto |

---

## 🎫 Fluxo 7: Criar Bilhete (Modal)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  MODAL: 🎫 Novo Bilhete                                    🎰 BETANO  [×] │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ Flamengo vs Palmeiras                              @ 2.15  [✏️] [×] │  │
│  │ Resultado Final: Vitória Mandante                                    │  │
│  │                                                                       │  │
│  │ ┌── ✏️ Alterar aposta ────────────────────────────────────────────┐  │  │
│  │ │ ⚽ Resultado Final                                               │  │  │
│  │ │   🏠 Mandante  @ 2.15  ← atual                                  │  │  │
│  │ │   🤝 Empate    @ 3.25                                            │  │  │
│  │ │   ✈️ Visitante @ 2.75                                            │  │  │
│  │ │ 🎯 Total de Gols                                                 │  │  │
│  │ │   ⬆️ Mais 2.5  @ 1.90                                            │  │  │
│  │ │   ⬇️ Menos 2.5 @ 1.90                                            │  │  │
│  │ │ ⚡ Ambos Marcam                                                   │  │  │
│  │ │   ✅ Sim       @ 1.75                                             │  │  │
│  │ │   ❌ Não       @ 2.00                                             │  │  │
│  │ └─────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  Apostas: 2 | Odd: 4.09 | Retorno: R$ 204.25                              │
│  Valor (R$): [50.00]  [10] [25] [50] [100]                                │
│                                                                             │
│  [Limpar]                                              [✅ Criar Bilhete]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Sequência

```
1. Usuário clica "Usar Bet365" ou "Usar Betano" na comparação
2. Modal abre com bilhete pré-montado
3. Pode editar cada aposta:
   ├─ Clica ✏️ → expande painel com TODAS as opções (7 total)
   ├─ Agrupa por mercado (Resultado, Total Gols, Ambos Marcam)
   └─ Clica numa alternativa → substitui a aposta
4. Define stake (valor)
5. Clica "Criar Bilhete"
   └─ POST /api/v1/tickets { name, stake, bookmaker_id, bets }
6. Modal fecha → navega para "Bilhetes"
```

---

## 🎫 Fluxo 8: Acompanhar Bilhetes ao Vivo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📋 Histórico de Bilhetes                    🟢 Próxima verificação: 3s     │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Rodada 5 - Betano                                       [PENDENTE]     │ │
│ │ 💰 Stake: R$ 50.00 │ 📊 Odd: 4.09 │ 🎯 Retorno: R$ 204.25           │ │
│ │                                                                         │ │
│ │ 🟢 Flamengo vs Palmeiras        1 × 0    67'   [2º Tempo]             │ │
│ │ ██████████████████████░░░░░░░░░  (74%)                                 │ │
│ │ 🏆 Brasileirão  ⚽ Resultado: Mandante  @ 2.15                        │ │
│ │ ✓ Ganhando                                                             │ │
│ │                                                                         │ │
│ │ ⏳ Vasco vs Corinthians                         [Não iniciado]         │ │
│ │ 🏆 Brasileirão  🎯 Over 2.5 gols  @ 1.90                             │ │
│ │                                                                         │ │
│ │ ⏳ Aguardando resultados...                              [🗑️ Excluir] │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dados ao Vivo por Aposta

| Dado | Quando Exibe | Descrição |
|------|-------------|-----------|
| ⚽ Placar | Ao vivo + Encerrado | `1 × 0` (vermelho pulsante se ao vivo) |
| ⏱️ Minuto | Ao vivo | `67'` (pisca) |
| 📊 Barra progresso | Ao vivo + Encerrado | 0-90min visual |
| 🟢/🔴 Ganhando/Perdendo | Ao vivo | Baseado no placar parcial vs aposta |
| 🏆 Liga | Sempre | Badge com nome da liga |
| 📋 Status | Sempre | NS, 1º Tempo, Intervalo, 2º Tempo, Encerrado |

### Sequência de Atualização

```
1. Aba "Bilhetes" → GET /api/v1/tickets
2. Se há bilhetes PENDENTES → inicia polling automático (5s)
3. A cada 5s:
   ├─ POST /api/v1/tickets/update-results
   │   → Backend busca GET /fixtures?id=X para cada partida
   │   → Extrai: status, elapsed, goals_home, goals_away
   │   → SEMPRE persiste dados parciais (mesmo não finalizados)
   │   → Se finalizado: compara resultado com aposta → WON/LOST
   │
   ├─ GET /api/v1/tickets (recarrega dados atualizados)
   │   → Frontend renderiza com placar, minuto, barra progresso
   │
   └─ Bilhetes com jogos ao vivo: borda vermelha pulsante

4. Quando TODOS os jogos finalizam:
   ├─ Ticket → GANHOU (todas certas) ou PERDEU (alguma errada)
   └─ Exibe lucro/prejuízo
```

---

## 🔧 Detalhes Técnicos

### Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/preload/fetch?days=N` | POST | Pré-carrega fixtures (1, 3, 7 dias) |
| `/api/v1/preload/status` | GET | Status do cache |
| `/api/v1/preload/odds` | POST | Odds em lote (body: fixture_ids) |
| `/api/v1/preload/odds/league` | POST | Odds por liga (body: league_id) |
| `/api/v1/matches` | GET | Lista jogos (query: date_from, date_to, league_id) |
| `/api/v1/matches/live` | GET | Jogos ao vivo (real-time) |
| `/api/v1/matches/{id}/odds` | GET | Odds de uma partida |
| `/api/v1/matches/{id}/odds/refresh` | POST | Refresh odds + status |
| `/api/v1/leagues` | GET | Campeonatos disponíveis |
| `/api/v1/bookmakers` | GET | Casas de apostas |
| `/api/v1/analyze` | POST | Analisa jogos (body: match_ids, strategy) |
| `/api/v1/tickets` | GET | Lista bilhetes (com dados ao vivo) |
| `/api/v1/tickets` | POST | Cria bilhete |
| `/api/v1/tickets/{id}` | GET | Detalhes de um bilhete |
| `/api/v1/tickets/{id}` | DELETE | Deleta bilhete |
| `/api/v1/tickets/{id}/update-result` | POST | Atualiza resultado de um bilhete |
| `/api/v1/tickets/stats/dashboard` | GET | Estatísticas |
| `/api/v1/tickets/update-results` | POST | Atualiza todos os pendentes (+ dados ao vivo) |
| `/health` | GET | Health check |

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
| `CACHE_TTL_FIXTURES` | `21600` | TTL fixtures (6h) |
| `CACHE_TTL_ODDS` | `1800` | TTL odds (30min) |

### Status de Partidas

| Ativos (exibidos) | Encerrados (filtrados) |
|---|---|
| NS, 1H, 2H, HT, ET, BT, P, SUSP, INT, LIVE, TBD | FT, AET, PEN, WO, AWD, CANC, ABD, PST |
