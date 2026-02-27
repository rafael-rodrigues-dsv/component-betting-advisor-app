# ⚽ Betting Advisor API - Postman Collection

Collection completa da **Betting Advisor API** para testes e desenvolvimento local.

**Versão:** 5.0.0  
**Status:** ✅ API-Football Real (sem mocks)

---

## 📦 Como Importar no Postman

### 1. **Importar o Arquivo JSON**

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Arraste o arquivo `Betting-Advisor-API-Local.postman_collection.json` ou clique em **Upload Files**
4. Clique em **Import**

### 2. **Verificar Variáveis**

A collection já vem com a variável configurada:
- **`base_url`**: `http://localhost:8000`

---

## 🚀 Pré-requisitos

### **Backend deve estar rodando:**

```bash
cd web_api
start.bat  # Windows
# ou
./start.sh  # Linux/Mac
```

**Verifique se está online:**
```
GET http://localhost:8000/health
```

**Esperado:** `{ "status": "ok" }`

---

## 📚 Estrutura da Collection

A collection está organizada em **9 pastas principais**:

### ❤️ **1. Health Check**

| Endpoint | Descrição |
|----------|-----------|
| `GET /health` | Status da API |

---

### 📦 **2. Preload (Pré-carregamento)**

| Endpoint | Descrição |
|----------|-----------|
| `POST /api/v1/preload/fetch?days=1` | Pré-carrega fixtures para Hoje |
| `POST /api/v1/preload/fetch?days=3` | Pré-carrega fixtures para 3 dias |
| `POST /api/v1/preload/fetch?days=7` | Pré-carrega fixtures para 7 dias |
| `GET /api/v1/preload/status` | Status do cache |

> **Nota:** O preload carrega apenas fixtures, não odds. Odds são carregadas por liga.

---

### ⚽ **3. Matches (Jogos)**

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/matches?date_from=...&date_to=...` | Jogos no período |
| `GET /api/v1/matches?date_from=...&date_to=...&league_id=71` | Jogos por liga |
| `GET /api/v1/matches/live` | **Novo** — Jogos ao vivo (real-time) |

---

### 📊 **4. Odds**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `GET /api/v1/matches/{id}/odds` | GET | Odds de uma partida |
| `POST /api/v1/matches/{id}/odds/refresh` | POST | Refresh odds + status |
| `POST /api/v1/preload/odds` | POST | Odds em lote (body: fixture_ids) |
| `POST /api/v1/preload/odds/league` | POST | **Novo** — Odds por liga (bulk) |

**Odds por Liga (recomendado):**
```json
{
  "league_id": 71
}
```
> Busca odds de TODOS os jogos da liga nas datas do período. Muito mais eficiente que individual.

---

### 🏅 **5. Leagues e Bookmakers**

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/leagues` | Ligas disponíveis (todas as do período carregado) |
| `GET /api/v1/bookmakers` | Casas de apostas suportadas (Bet365, Betano) |

---

### 🔮 **6. Predictions (Análises)**

| Endpoint | Descrição |
|----------|-----------|
| `POST /api/v1/analyze` | Analisa jogos com estratégia |

**Request Body:**
```json
{
  "match_ids": ["1387913", "1387914"],
  "strategy": "CONSERVATIVE"
}
```

**Estratégias Disponíveis:**
- `CONSERVATIVE` — 🛡️ Seguro, favoritos claros (default)
- `BALANCED` — ⚖️ Mix equilibrado
- `AGGRESSIVE` — 🔥 Alto risco, alto retorno

**Response inclui:**
- `predictions`: previsões por jogo com todos os mercados
- `odds_by_bookmaker`: odds reais de cada casa (para comparação)
- `pre_ticket`: pré-bilhete montado automaticamente

---

### 🎫 **7. Tickets (Bilhetes)**

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `POST /api/v1/tickets` | POST | Criar bilhete |
| `GET /api/v1/tickets` | GET | Listar bilhetes (com dados ao vivo) |
| `GET /api/v1/tickets/{id}` | GET | Detalhes de um bilhete |
| `DELETE /api/v1/tickets/{id}` | DELETE | Deletar bilhete |
| `GET /api/v1/tickets/stats/dashboard` | GET | Estatísticas do dashboard |
| `POST /api/v1/tickets/update-results` | POST | Atualizar resultados + dados ao vivo |
| `POST /api/v1/tickets/{id}/update-result` | POST | **Novo** — Atualizar um bilhete específico |

**Criar Ticket:**
```json
{
  "name": "Rodada 5 - Conservadora - Betano",
  "stake": 50.00,
  "bookmaker_id": "betano",
  "bets": [
    {
      "match_id": "1387913",
      "home_team": "Flamengo",
      "away_team": "Palmeiras",
      "league": "Brasileirão Série A",
      "market": "MATCH_WINNER",
      "predicted_outcome": "HOME",
      "odds": 2.15,
      "confidence": 0.55
    }
  ]
}
```

**Bet Response (com dados ao vivo):**
```json
{
  "match_id": "1387913",
  "home_team": "Flamengo",
  "away_team": "Palmeiras",
  "league": "Brasileirão Série A",
  "market": "MATCH_WINNER",
  "predicted_outcome": "HOME",
  "odds": 2.15,
  "confidence": 0.55,
  "result": null,
  "final_score": null,
  "status": "Second Half",
  "status_short": "2H",
  "elapsed": 67,
  "goals_home": 1,
  "goals_away": 0
}
```

**Status do bilhete:** `PENDENTE`, `GANHOU`, `PERDEU`

---

### 🖼️ **8. Static Assets**

| Endpoint | Descrição |
|----------|-----------|
| `GET /static/escudos/{team}.png` | Escudo de time |

---

## 🎯 Fluxo de Uso Típico

### **1. Verificar API Online**
```
GET /health
```

### **2. Pré-carregar fixtures (3 dias)**
```
POST /api/v1/preload/fetch?days=3
```

### **3. Buscar Jogos**
```
GET /api/v1/matches?date_from=2026-02-27&date_to=2026-03-01
```

### **4. Carregar Odds por Liga (Brasileirão)**
```
POST /api/v1/preload/odds/league
Body: { "league_id": 71 }
```

### **5. Buscar Jogos ao Vivo**
```
GET /api/v1/matches/live
```

### **6. Analisar Jogos (Conservadora)**
```
POST /api/v1/analyze
Body: { "match_ids": ["1387913", "1387914"], "strategy": "CONSERVATIVE" }
```

### **7. Re-analisar com outra estratégia**
```
POST /api/v1/analyze
Body: { "match_ids": ["1387913", "1387914"], "strategy": "AGRESSIVE" }
```

### **8. Criar Bilhete**
```
POST /api/v1/tickets
Body: { "name": "Meu Bilhete", "stake": 50.00, "bookmaker_id": "betano", "bets": [...] }
```

### **9. Acompanhar Bilhetes (com dados ao vivo)**
```
GET /api/v1/tickets
```

### **10. Atualizar Resultados Reais**
```
POST /api/v1/tickets/update-results
```

---

## 🔧 Configuração do Backend

```env
API_FOOTBALL_KEY=sua_chave_aqui
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
TIMEZONE=America/Sao_Paulo
SUPPORTED_BOOKMAKERS=bet365,betano
```

**Cache:**
- SQLite (`web_api/data/cache.db`)
- TTL: 6 horas (fixtures) / 30 minutos (odds)
- Incremental: Hoje→3→7 dias reaproveita cache anterior

---

## 🔍 Troubleshooting

### **Erro: Connection Refused**
- ✅ Verifique se o backend está rodando
- ✅ Teste: `http://localhost:8000/health`

### **Erro 404: Not Found**
- ✅ Verifique se a rota inclui `/api/v1/`
- ✅ Swagger: `http://localhost:8000/docs`

### **Dados Vazios (count: 0)**
- ✅ Execute o preload primeiro: `POST /api/v1/preload/fetch?days=3`
- ✅ Carregue odds da liga: `POST /api/v1/preload/odds/league { "league_id": 71 }`

### **Odds não aparecem**
- ✅ Odds são carregadas POR LIGA, não automaticamente
- ✅ Selecione uma liga no carrossel ou use `POST /preload/odds/league`

---

## ✅ Checklist de Uso

- [ ] Backend rodando (`/health` retorna OK)
- [ ] Collection importada no Postman
- [ ] Preload executado (`POST /preload/fetch?days=3`)
- [ ] Matches carregados (`GET /matches`)
- [ ] Odds carregadas por liga (`POST /preload/odds/league`)
- [ ] Jogos ao vivo testados (`GET /matches/live`)
- [ ] Análise testada (`POST /analyze`)
- [ ] Bilhete criado (`POST /tickets`)
- [ ] Resultados atualizados (`POST /tickets/update-results`)
