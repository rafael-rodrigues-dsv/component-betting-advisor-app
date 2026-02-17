# ⚽ Betting Advisor API - Postman Collection

Collection completa da **Betting Advisor API** para testes e desenvolvimento local.

---

## 📦 Como Importar no Postman

### 1. **Importar o Arquivo JSON**

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Arraste o arquivo `Betting-Advisor-API-Local.postman_collection.json` ou clique em **Upload Files**
4. Clique em **Import**

### 2. **Importar Environment (Opcional)**

Para facilitar testes com variáveis pré-configuradas:

1. Clique em **Import**
2. Selecione o arquivo `Betting-Advisor-Local.postman_environment.json`
3. Clique em **Import**
4. No canto superior direito, selecione o environment **"Betting Advisor - Local"**

### 3. **Verificar Variáveis**

A collection já vem com a variável configurada:
- **`base_url`**: `http://localhost:8000`

Se precisar alterar:
1. Clique nos `...` ao lado da collection
2. **Edit** → aba **Variables**
3. Altere o valor de `base_url`

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

A collection está organizada em **7 pastas principais** com ícones para fácil identificação:

### ❤️ **1. Health Check**
Verificar se a API está online e funcionando.

| Endpoint | Descrição |
|----------|-----------|
| `GET /health` | Status da API |

**Response:**
```json
{
  "status": "ok"
}
```

---

### ⚽ **2. Matches (Jogos)**
Buscar jogos disponíveis por data, liga, etc.

| Endpoint | Descrição | Ícone |
|----------|-----------|-------|
| `GET /api/v1/matches` | Todos os jogos de hoje | 📋 |
| `GET /api/v1/matches?date=2026-02-17` | Jogos de uma data específica | 📅 |
| `GET /api/v1/matches?league_id=71` | Jogos do Brasileirão | 🏆 |
| `GET /api/v1/matches?date=2026-02-17&league_id=71` | Brasileirão em uma data | 🏆📅 |

**Parâmetros:**
- `date`: Data no formato `YYYY-MM-DD` (opcional, padrão: hoje)
- `league_id`: ID da liga (opcional)

**League IDs Importantes:**
- **71** - Brasileirão Série A
- **73** - Copa do Brasil
- **39** - Premier League (Inglaterra)
- **140** - La Liga (Espanha)
- **78** - Bundesliga (Alemanha)
- **61** - Ligue 1 (França)
- **135** - Serie A (Itália)

**Response:**
```json
{
  "success": true,
  "date": "2026-02-17",
  "count": 12,
  "matches": [
    {
      "id": "712026021700",
      "date": "2026-02-17T16:30:00Z",
      "timestamp": "2026-02-17",
      "status": "Not Started",
      "league": {
        "id": "71",
        "name": "Brasileirão Série A",
        "country": "Brazil",
        "logo": "http://localhost:8000/static/leagues/71.png",
        "type": "league"
      },
      "home_team": {
        "id": "797",
        "name": "Vasco",
        "logo": {
          "url": "http://localhost:8000/static/escudos/vasco.png",
          "type": "LOCAL"
        }
      },
      "away_team": {
        "id": "3568",
        "name": "Palmeiras",
        "logo": {
          "url": "http://localhost:8000/static/escudos/palmeiras.png",
          "type": "LOCAL"
        }
      },
      "round": {
        "type": "round",
        "name": "Rodada 1"
      },
      "venue": {
        "name": "Stadium Vasco",
        "city": "Brazil"
      },
      "odds": {
        "bet365": {
          "home": 1.93,
          "draw": 3.26,
          "away": 3.59,
          "over_25": 2.16,
          "under_25": 1.8,
          "btts_yes": 2.08,
          "btts_no": 1.58
        },
        "betano": {
          "home": 1.97,
          "draw": 3.19,
          "away": 3.63,
          "over_25": 2.18,
          "under_25": 1.78,
          "btts_yes": 2.12,
          "btts_no": 1.55
        }
      }
    }
  ]
}
```

---

### 🏅 **3. Leagues (Ligas)**
Buscar ligas/campeonatos disponíveis.

| Endpoint | Descrição | Ícone |
|----------|-----------|-------|
| `GET /api/v1/leagues` | Todas as ligas disponíveis | 📜 |

**Response:**
```json
{
  "success": true,
  "count": 7,
  "leagues": [
    {
      "id": "71",
      "name": "Brasileirão Série A",
      "country": "Brazil",
      "logo": "🇧🇷",
      "type": "league"
    },
    {
      "id": "39",
      "name": "Premier League",
      "country": "England",
      "logo": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
      "type": "league"
    }
  ]
}
```

---

### 💰 **4. Bookmakers (Casas de Apostas)**
Buscar casas de apostas disponíveis.

| Endpoint | Descrição | Ícone |
|----------|-----------|-------|
| `GET /api/v1/bookmakers` | Todas as casas disponíveis | 🎰 |

**Response:**
```json
{
  "success": true,
  "count": 5,
  "bookmakers": [
    {
      "id": "bet365",
      "name": "Bet365",
      "logo": "💰"
    },
    {
      "id": "betano",
      "name": "Betano",
      "logo": "💰"
    }
  ]
}
```

**Bookmaker IDs:**
- `bet365` - Bet365
- `betano` - Betano
- `betfair` - Betfair
- `1xbet` - 1xBet
- `pinnacle` - Pinnacle

---

### 🔮 **5. Predictions (Análises)**
Analisar jogos selecionados e obter previsões baseadas em estratégias.

| Endpoint | Estratégia | Descrição | Ícone |
|----------|------------|-----------|-------|
| `POST /api/v1/predictions/analyze` | Conservative | Favoritos seguros (>70% confiança) | 🛡️ |
| `POST /api/v1/predictions/analyze` | Balanced | Equilibrado (>60% confiança) | ⚖️ |
| `POST /api/v1/predictions/analyze` | Value Bet | Apostas de valor (>55% confiança, >5% EV) | 💎 |
| `POST /api/v1/predictions/analyze` | Aggressive | Alto risco/retorno (>25% confiança) | 🔥 |

**Request Body:**
```json
{
  "match_ids": [
    "712026021700",
    "712026021701"
  ],
  "strategy": "CONSERVATIVE",
  "bookmaker": "bet365"
}
```

**Estratégias Disponíveis:**
- `CONSERVATIVE` - Seguro, favoritos claros
- `BALANCED` - Mix equilibrado
- `VALUE_BET` - Busca discrepâncias de odds
- `AGGRESSIVE` - Alto risco, alto retorno

**Bookmakers:**
- `bet365`
- `betano`

**Response:**
```json
{
  "success": true,
  "count": 2,
  "strategy": "CONSERVATIVE",
  "bookmaker": "bet365",
  "predictions": [
    {
      "match_id": "712026021700",
      "home_team": "Vasco",
      "away_team": "Palmeiras",
      "league": "Brasileirão Série A",
      "date": "2026-02-17T16:30:00Z",
      "predictions": [
        {
          "market": "MATCH_WINNER",
          "predicted_outcome": "away",
          "confidence": 75.5,
          "odds": 1.85,
          "expected_value": 0.08,
          "recommendation": "RECOMMENDED"
        },
        {
          "market": "OVER_UNDER",
          "predicted_outcome": "over_25",
          "confidence": 68.2,
          "odds": 1.90,
          "expected_value": 0.05,
          "recommendation": "RECOMMENDED"
        }
      ],
      "strategy_used": "CONSERVATIVE"
    }
  ]
}
```

**Markets (Mercados):**
- `MATCH_WINNER` - Resultado final (1X2)
- `OVER_UNDER` - Mais/Menos gols
- `BTTS` - Ambos marcam
- `DOUBLE_CHANCE` - Dupla chance

**Recommendations:**
- `HIGHLY_RECOMMENDED` - Altamente recomendado
- `RECOMMENDED` - Recomendado
- `NEUTRAL` - Neutro
- `NOT_RECOMMENDED` - Não recomendado
- `AVOID` - Evitar

---

### 🎫 **6. Tickets (Bilhetes)**
Gerenciar bilhetes de apostas (múltiplas).

| Endpoint | Método | Descrição | Ícone |
|----------|--------|-----------|-------|
| `POST /api/v1/tickets` | POST | Criar novo bilhete | ➕ |
| `GET /api/v1/tickets` | GET | Listar todos os bilhetes | 📋 |
| `GET /api/v1/tickets/:ticket_id` | GET | Buscar bilhete específico | 🔍 |
| `PATCH /api/v1/tickets/:ticket_id/status` | PATCH | Atualizar status | 🔄 |
| `DELETE /api/v1/tickets/:ticket_id` | DELETE | Deletar bilhete | 🗑️ |

#### **Criar Ticket**

**Request:**
```json
{
  "name": "Múltipla Brasileirão - Rodada 1",
  "stake": 50.00,
  "bookmaker_id": "bet365",
  "bets": [
    {
      "match_id": "712026021700",
      "home_team": "Vasco",
      "away_team": "Palmeiras",
      "market": "MATCH_WINNER",
      "predicted_outcome": "away",
      "odds": 1.85,
      "confidence": 75.5
    },
    {
      "match_id": "712026021701",
      "home_team": "Fluminense",
      "away_team": "Atlético-MG",
      "market": "OVER_UNDER",
      "predicted_outcome": "over_25",
      "odds": 1.90,
      "confidence": 68.2
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "ticket": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Múltipla Brasileirão - Rodada 1",
    "stake": 50.00,
    "bookmaker_id": "bet365",
    "status": "PENDING",
    "total_odds": 3.52,
    "potential_return": 176.00,
    "bets_count": 2,
    "created_at": "2026-02-17T15:00:00Z"
  }
}
```

**Status:**
- `PENDING` - Pendente (aguardando resultado)
- `WON` - Ganho
- `LOST` - Perdido
- `CANCELLED` - Cancelado

#### **Listar Tickets**

**Response:**
```json
{
  "success": true,
  "count": 5,
  "tickets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Múltipla Brasileirão - Rodada 1",
      "stake": 50.00,
      "status": "PENDING",
      "total_odds": 3.52,
      "potential_return": 176.00,
      "created_at": "2026-02-17T15:00:00Z"
    }
  ]
}
```

#### **Atualizar Status**

**Request:**
```json
{
  "status": "WON"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Status atualizado com sucesso",
  "ticket": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "WON"
  }
}
```

---

### 🖼️ **7. Static Assets**
Acessar recursos estáticos (logos, escudos).

| Endpoint | Descrição | Ícone |
|----------|-----------|-------|
| `GET /static/escudos/{team}.png` | Escudo de time | 🛡️ |

**Exemplos:**
- `/static/escudos/flamengo.png`
- `/static/escudos/palmeiras.png`
- `/static/escudos/manchester-city.png`

**Escudos Disponíveis:**
- Brasileirão: flamengo, palmeiras, corinthians, sao-paulo, santos, vasco, etc.
- Premier League: manchester-city, liverpool, arsenal, chelsea, etc.

---

## 🎯 Fluxo de Uso Típico

### **1. Verificar API Online**
```
GET /health
```

### **2. Buscar Jogos de Hoje**
```
GET /api/v1/matches
```

### **3. Filtrar por Liga**
```
GET /api/v1/matches?league_id=71
```

### **4. Analisar Jogos Selecionados**
```
POST /api/v1/predictions/analyze
Body: {
  "match_ids": ["712026021700", "712026021701"],
  "strategy": "CONSERVATIVE",
  "bookmaker": "bet365"
}
```

### **5. Criar Bilhete com Previsões**
```
POST /api/v1/tickets
Body: {
  "name": "Múltipla",
  "stake": 50.00,
  "bookmaker_id": "bet365",
  "bets": [...]
}
```

### **6. Acompanhar Bilhetes**
```
GET /api/v1/tickets
```

### **7. Atualizar Resultado**
```
PATCH /api/v1/tickets/{id}/status
Body: { "status": "WON" }
```

---

## 🔧 Configuração do Backend

### **Modo de Operação**

O backend opera em **modo MOCK** (virtualizado, sem chamadas à API-Football):

```env
# .env.development
API_FOOTBALL_MODE=mock
```

**Vantagens:**
- ✅ Sem limite de requests
- ✅ Dados instantâneos
- ✅ Sem necessidade de API key
- ✅ Dados realistas e consistentes

### **Modo HTTP (Futuro)**

Para usar a API-Football real:

```env
# .env.production
API_FOOTBALL_MODE=http
API_FOOTBALL_KEY=sua_chave_aqui
```

---

## 📊 Dados Mockados

### **Ligas Pré-carregadas:**
- 🇧🇷 Brasileirão Série A (ID: 71)
- 🏆 Copa do Brasil (ID: 73)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (ID: 39)
- 🇪🇸 La Liga (ID: 140)
- 🇩🇪 Bundesliga (ID: 78)
- 🇫🇷 Ligue 1 (ID: 61)
- 🇮🇹 Serie A (ID: 135)

### **Período:**
- Data atual até próximo domingo
- Fixtures gerados automaticamente
- Odds de 2 casas (Bet365 e Betano)

### **Cache:**
- SQLite (`web_api/data/cache.db`)
- TTL: 6 horas (fixtures) / 30 minutos (odds)
- Renovado automaticamente no startup

---

## 🧪 Testando Endpoints

### **Teste 1: Verificar Saúde da API**
```bash
curl http://localhost:8000/health
```
**Esperado:** `{"status":"ok"}`

### **Teste 2: Buscar Jogos**
```bash
curl http://localhost:8000/api/v1/matches
```
**Esperado:** JSON com lista de jogos

### **Teste 3: Analisar Jogos (Conservative)**
```bash
curl -X POST http://localhost:8000/api/v1/predictions/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "match_ids": ["712026021700"],
    "strategy": "CONSERVATIVE",
    "bookmaker": "bet365"
  }'
```
**Esperado:** JSON com análises e recomendações

### **Teste 4: Criar Bilhete**
```bash
curl -X POST http://localhost:8000/api/v1/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Teste",
    "stake": 10.00,
    "bookmaker_id": "bet365",
    "bets": [...]
  }'
```
**Esperado:** JSON com ID do ticket criado

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
- ✅ Verifique se o cache está corrompido
- ✅ Limpe o cache: `rmdir /s /q web_api\data` (Windows) ou `rm -rf web_api/data` (Linux/Mac)
- ✅ Reinicie o backend

### **Dados Vazios (count: 0)**
- ✅ Limpe o cache e reinicie o backend
- ✅ Aguarde o pré-carregamento (logs mostram progresso)
- ✅ Verifique se a data está correta (hoje ou futuro)

---

## 📚 Recursos Adicionais

### **Documentação Interativa**
- 📖 **Swagger UI:** http://localhost:8000/docs
- 📖 **ReDoc:** http://localhost:8000/redoc
- 📖 **OpenAPI JSON:** http://localhost:8000/openapi.json

### **Arquivos de Suporte**
- 📁 `docs/` - Documentação completa
- 📁 `static/escudos/` - Logos dos times
- 📁 `web_api/data/` - Cache SQLite

---

## 🎨 Ícones da Collection

A collection usa ícones para facilitar a navegação:

- ❤️ Health Check
- ⚽ Matches (Jogos)
- 🏅 Leagues (Ligas)
- 💰 Bookmakers (Casas de Apostas)
- 🔮 Predictions (Análises)
  - 🛡️ Conservative
  - ⚖️ Balanced
  - 💎 Value Bet
  - 🔥 Aggressive
- 🎫 Tickets (Bilhetes)
  - ➕ Create
  - 📋 List
  - 🔍 Get by ID
  - 🔄 Update
  - 🗑️ Delete
- 🖼️ Static Assets

---

## ✅ Checklist de Uso

- [ ] Backend rodando (`http://localhost:8000/health` retorna OK)
- [ ] Collection importada no Postman
- [ ] Environment configurado (opcional)
- [ ] Testado endpoint `/health`
- [ ] Testado endpoint `/api/v1/matches`
- [ ] Testado endpoint `/api/v1/predictions/analyze`
- [ ] Testado endpoint `/api/v1/tickets` (POST)
- [ ] Entendido o fluxo completo (matches → analyze → create ticket)

---

## 🚀 Pronto para Usar!

A collection está completa com **17 endpoints organizados** em 7 categorias com ícones bonitinhos! 🎨

**Happy Testing!** ⚽💰🎯

