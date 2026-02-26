# ⚽ Betting Advisor API - Postman Collection

Collection completa da **Betting Advisor API** para testes e desenvolvimento local.

**Versão:** 4.0.0  
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

A collection está organizada em **8 pastas principais**:

### ❤️ **1. Health Check**

| Endpoint | Descrição |
|----------|-----------|
| `GET /health` | Status da API |

**Response:**
```json
{ "status": "ok" }
```

---

### 📦 **2. Preload (Pré-carregamento)**
Carregar fixtures da API-Football sob demanda.

| Endpoint | Descrição |
|----------|-----------|
| `POST /api/v1/preload/fetch?days=3` | Pré-carrega fixtures para 3 dias |
| `POST /api/v1/preload/fetch?days=7` | Pré-carrega fixtures para 7 dias |
| `POST /api/v1/preload/fetch?days=14` | Pré-carrega fixtures para 14 dias |
| `GET /api/v1/preload/status` | Status do cache |

**Response (fetch):**
```json
{
  "success": true,
  "message": "Pré-carregamento concluído",
  "date_from": "2026-02-26",
  "date_to": "2026-02-28",
  "total_fixtures": 39,
  "total_odds": 0
}
```

> **Nota:** O preload carrega apenas fixtures, não odds. Odds são carregadas via batch ou refresh individual.

---

### ⚽ **3. Matches (Jogos)**
Buscar jogos disponíveis por data, liga, etc.

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/matches?date_from=...&date_to=...` | Jogos no período |
| `GET /api/v1/matches?date_from=...&date_to=...&league_id=71` | Jogos do Brasileirão |

**Parâmetros:**
- `date_from`: Data início (YYYY-MM-DD)
- `date_to`: Data fim (YYYY-MM-DD)
- `league_id`: ID da liga (opcional)

**League IDs Importantes:**
- **71** - Brasileirão Série A
- **73** - Copa do Brasil
- **39** - Premier League (Inglaterra)
- **140** - La Liga (Espanha)
- **78** - Bundesliga (Alemanha)
- **61** - Ligue 1 (França)
- **135** - Serie A (Itália)

---

### 📊 **4. Odds**
Buscar odds de partidas.

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `GET /api/v1/matches/{id}/odds` | GET | Odds de uma partida (cache ou API) |
| `POST /api/v1/matches/{id}/odds/refresh` | POST | Força refresh de odds + status |
| `POST /api/v1/matches/odds/batch` | POST | Odds em lote |

**Response (odds):**
```json
{
  "success": true,
  "fixture_id": "1387913",
  "odds": {
    "bet365": {
      "home": 2.10,
      "draw": 3.20,
      "away": 2.80,
      "over_25": 1.85,
      "under_25": 1.95,
      "btts_yes": 1.72,
      "btts_no": 2.05
    },
    "betano": {
      "home": 2.15,
      "draw": 3.25,
      "away": 2.75,
      "over_25": 1.90,
      "under_25": 1.90,
      "btts_yes": 1.75,
      "btts_no": 2.00
    }
  }
}
```

**Refresh Response (inclui status):**
```json
{
  "success": true,
  "odds": { ... },
  "status": "Not Started",
  "status_short": "NS"
}
```

**Batch Request:**
```json
{
  "fixture_ids": ["1387913", "1387914", "1387915"]
}
```

---

### 🏅 **5. Leagues e Bookmakers**

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/v1/leagues` | Ligas disponíveis |
| `GET /api/v1/bookmakers` | Casas de apostas suportadas |

**Response (bookmakers):**
```json
{
  "success": true,
  "count": 2,
  "bookmakers": [
    { "id": "bet365", "name": "Bet365", "logo": "🟢" },
    { "id": "betano", "name": "Betano", "logo": "🟡" }
  ]
}
```

> **Nota:** Apenas Bet365 e Betano são suportadas. Configurável via `SUPPORTED_BOOKMAKERS` no `.env`.

---

### 🔮 **6. Predictions (Análises)**
Analisar jogos selecionados e obter previsões baseadas em estratégias.

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
- `CONSERVATIVE` — 🛡️ Seguro, favoritos claros (default ao analisar)
- `BALANCED` — ⚖️ Mix equilibrado
- `VALUE_BET` — 💰 Busca discrepâncias de odds entre casas
- `AGGRESSIVE` — 🔥 Alto risco, alto retorno

**Response:**
```json
{
  "success": true,
  "count": 2,
  "strategy": "CONSERVATIVE",
  "predictions": [
    {
      "id": "1387913",
      "match_id": "1387913",
      "home_team": "Flamengo",
      "away_team": "Palmeiras",
      "league": "Brasileirão Série A",
      "date": "2026-02-26T20:00:00-03:00",
      "predictions": [
        {
          "market": "MATCH_WINNER",
          "predicted_outcome": "HOME",
          "confidence": 0.55,
          "odds": 2.10,
          "expected_value": 0.08,
          "recommendation": "RECOMMENDED"
        },
        {
          "market": "OVER_UNDER",
          "predicted_outcome": "OVER_2.5",
          "confidence": 0.52,
          "odds": 1.85,
          "expected_value": 0.05,
          "recommendation": "RECOMMENDED"
        }
      ],
      "odds_by_bookmaker": {
        "bet365": { "home": 2.10, "draw": 3.20, "away": 2.80, "over_25": 1.85, "under_25": 1.95 },
        "betano": { "home": 2.15, "draw": 3.25, "away": 2.75, "over_25": 1.90, "under_25": 1.90 }
      }
    }
  ],
  "pre_ticket": {
    "bets": [...],
    "total_bets": 2,
    "combined_odds": 3.89,
    "message": "Bilhete conservador montado"
  }
}
```

> **Nota:** `odds_by_bookmaker` é usado pelo frontend para a comparação lado a lado entre Bet365 e Betano.

**Markets (Mercados):**
- `MATCH_WINNER` — Resultado final (1X2)
- `OVER_UNDER` — Mais/Menos 2.5 gols
- `BTTS` — Ambos marcam (Sim/Não)

**Recommendations:**
- `STRONG_BET` — 🔥 Aposta Forte
- `RECOMMENDED` — ✅ Recomendada
- `CONSIDER` — 💭 Considerar
- `AVOID` — ⛔ Evitar

---

### 🎫 **7. Tickets (Bilhetes)**
Gerenciar bilhetes de apostas.

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `POST /api/v1/tickets` | POST | Criar bilhete |
| `GET /api/v1/tickets` | GET | Listar bilhetes |
| `GET /api/v1/tickets/{id}` | GET | Detalhes de um bilhete |
| `DELETE /api/v1/tickets/{id}` | DELETE | Deletar bilhete |
| `GET /api/v1/tickets/stats/dashboard` | GET | Estatísticas do dashboard |
| `POST /api/v1/tickets/update-results` | POST | Atualizar resultados reais |

#### **Criar Ticket**

**Request:**
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

**Response:**
```json
{
  "success": true,
  "message": "Bilhete criado com sucesso!",
  "ticket": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Rodada 5 - Conservadora - Betano",
    "stake": 50.00,
    "bookmaker_id": "betano",
    "status": "PENDENTE",
    "combined_odds": 2.15,
    "potential_return": 107.50,
    "bets": [
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
        "status": null,
        "status_short": null
      }
    ],
    "created_at": "2026-02-26T20:00:00"
  }
}
```

**Status:**
- `PENDENTE` — Aguardando resultado
- `GANHOU` — Todas as apostas corretas
- `PERDEU` — Alguma aposta errada

---

### 🖼️ **8. Static Assets**

| Endpoint | Descrição |
|----------|-----------|
| `GET /static/escudos/{team}.png` | Escudo de time |

**Exemplos:**
- `/static/escudos/flamengo.png`
- `/static/escudos/palmeiras.png`
- `/static/escudos/manchester-city.png`

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
GET /api/v1/matches?date_from=2026-02-26&date_to=2026-02-28
```

### **4. Carregar Odds em Batch**
```
POST /api/v1/matches/odds/batch
Body: { "fixture_ids": ["1387913", "1387914"] }
```

### **5. Analisar Jogos (Conservadora)**
```
POST /api/v1/analyze
Body: { "match_ids": ["1387913", "1387914"], "strategy": "CONSERVATIVE" }
```

### **6. Re-analisar com outra estratégia**
```
POST /api/v1/analyze
Body: { "match_ids": ["1387913", "1387914"], "strategy": "VALUE_BET" }
```

### **7. Criar Bilhete**
```
POST /api/v1/tickets
Body: { "name": "Meu Bilhete", "stake": 50.00, "bookmaker_id": "betano", "bets": [...] }
```

### **8. Acompanhar Bilhetes**
```
GET /api/v1/tickets
```

### **9. Atualizar Resultados Reais**
```
POST /api/v1/tickets/update-results
```

---

## 🔧 Configuração do Backend

O backend opera em **modo real** (API-Football):

```env
API_FOOTBALL_KEY=sua_chave_aqui
API_FOOTBALL_BASE_URL=https://v3.football.api-sports.io
TIMEZONE=America/Sao_Paulo
SUPPORTED_BOOKMAKERS=bet365,betano
MAIN_LEAGUES=71,73,39,140,78,61,135
```

**Cache:**
- SQLite (`web_api/data/cache.db`)
- TTL: 6 horas (fixtures) / 30 minutos (odds)
- Incremental: 3→7→14 dias reaproveita cache anterior

---

## 🧪 Testando Endpoints

```bash
# Health
curl http://localhost:8000/health

# Preload 3 dias
curl -X POST "http://localhost:8000/api/v1/preload/fetch?days=3"

# Matches
curl "http://localhost:8000/api/v1/matches?date_from=2026-02-26&date_to=2026-02-28"

# Analyze (Conservative)
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"match_ids": ["1387913"], "strategy": "CONSERVATIVE"}'

# Criar bilhete
curl -X POST http://localhost:8000/api/v1/tickets \
  -H "Content-Type: application/json" \
  -d '{"name": "Teste", "stake": 10.00, "bookmaker_id": "betano", "bets": [...]}'
```

---

## 🔍 Troubleshooting

### **Erro: Connection Refused**
- ✅ Verifique se o backend está rodando
- ✅ Confirme que está na porta 8000
- ✅ Teste: `http://localhost:8000/health`

### **Erro 404: Not Found**
- ✅ Verifique se a rota inclui `/api/v1/`
- ✅ Confira a documentação Swagger: `http://localhost:8000/docs`

### **Erro 500: Internal Server Error**
- ✅ Veja os logs no terminal do backend
- ✅ Limpe o cache: `rmdir /s /q web_api\data` (Windows)
- ✅ Reinicie o backend

### **Dados Vazios (count: 0)**
- ✅ Execute o preload primeiro: `POST /api/v1/preload/fetch?days=3`
- ✅ Aguarde (logs mostram progresso)
- ✅ Verifique se a data está correta

---

## 📚 Recursos Adicionais

- 📖 **Swagger UI:** http://localhost:8000/docs
- 📖 **ReDoc:** http://localhost:8000/redoc
- 📁 `docs/ARQUITETURA.md` — Arquitetura completa
- 📁 `docs/FLUXO_FUNCIONAL.md` — Fluxo funcional

---

## ✅ Checklist de Uso

- [ ] Backend rodando (`/health` retorna OK)
- [ ] Collection importada no Postman
- [ ] Preload executado (`POST /preload/fetch?days=3`)
- [ ] Matches carregados (`GET /matches`)
- [ ] Odds carregadas (batch ou refresh individual)
- [ ] Análise testada (`POST /analyze`)
- [ ] Bilhete criado (`POST /tickets`)
- [ ] Fluxo completo entendido (preload → matches → odds → analyze → ticket)
