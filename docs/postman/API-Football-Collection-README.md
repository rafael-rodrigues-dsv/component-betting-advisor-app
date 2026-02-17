# 🎰 API-Football - Postman Collection

Collection completa da API-Football para o projeto **Betting Advisor**.

---

## 📦 Como Importar no Postman

### 1. **Importar o Arquivo JSON**

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Arraste o arquivo `API-Football-Collection.postman_collection.json` ou clique em **Upload Files**
4. Clique em **Import**

### 2. **Configurar Variável de Ambiente**

A collection já vem com a chave de API configurada, mas você pode criar um ambiente separado:

1. No Postman, vá em **Environments** (barra lateral esquerda)
2. Clique em **+** para criar novo ambiente
3. Nome: `API-Football`
4. Adicione a variável:
   - **Variable:** `API_FOOTBALL_KEY`
   - **Initial Value:** `9b0f0fe6a2e910ccf28f8968a422a7d9`
   - **Current Value:** `9b0f0fe6a2e910ccf28f8968a422a7d9`
5. Salve o ambiente
6. Selecione o ambiente no dropdown (canto superior direito)

---

## 📚 Estrutura da Collection

A collection está organizada em **7 pastas principais**:

### 🏆 **1. Leagues (Ligas)**
Buscar ligas/campeonatos disponíveis.

| Endpoint | Descrição |
|----------|-----------|
| `GET /leagues` | Todas as ligas |
| `GET /leagues?country=Brazil` | Ligas do Brasil |
| `GET /leagues?country=England` | Ligas da Inglaterra |
| `GET /leagues?id=71` | Brasileirão Série A |
| `GET /leagues?id=39` | Premier League |

**IDs Importantes:**
- **71** - Brasileirão Série A
- **73** - Copa do Brasil
- **39** - Premier League

---

### ⚽ **2. Fixtures (Jogos)**
Buscar jogos (fixtures) por data, liga, time, etc.

| Endpoint | Descrição |
|----------|-----------|
| `GET /fixtures?date=2026-02-17` | Jogos de hoje |
| `GET /fixtures?league=71&season=2026` | Jogos do Brasileirão 2026 |
| `GET /fixtures?league=71&date=2026-02-17` | Jogos do Brasileirão hoje |
| `GET /fixtures?league=39&season=2026` | Jogos da Premier League 2026 |
| `GET /fixtures?id=1035148` | Jogo específico por ID |
| `GET /fixtures?live=all` | Jogos ao vivo |

**Formato de Data:** `YYYY-MM-DD`

---

### 💰 **3. Odds (Cotações)**
Buscar odds (cotações) de múltiplas casas de apostas.

| Endpoint | Descrição |
|----------|-----------|
| `GET /odds?fixture=1035148` | Odds de um jogo (todas as casas) |
| `GET /odds?league=71&date=2026-02-17` | Odds do Brasileirão hoje |
| `GET /odds?fixture=1035148&bookmaker=6` | Odds apenas da Bet365 |
| `GET /odds?fixture=1035148&bet=1` | Odds apenas de Match Winner (1X2) |

**Bookmaker IDs:**
- **6** - Bet365
- **8** - Betano

**Bet Type IDs:**
- **1** - Match Winner (1X2)
- **5** - Goals Over/Under
- **8** - Both Teams Score (BTTS)

---

### 🏠 **4. Bookmakers (Casas de Apostas)**
Buscar casas de apostas disponíveis.

| Endpoint | Descrição |
|----------|-----------|
| `GET /odds/bookmakers` | Todas as casas |
| `GET /odds/bookmakers?id=6` | Bet365 |

---

### ⚙️ **5. Bets (Tipos de Aposta)**
Buscar tipos de apostas disponíveis.

| Endpoint | Descrição |
|----------|-----------|
| `GET /odds/bets` | Todos os tipos |
| `GET /odds/bets?id=1` | Match Winner (1X2) |

---

### 🏅 **6. Teams (Times)**
Buscar times (incluindo logos).

| Endpoint | Descrição |
|----------|-----------|
| `GET /teams?country=Brazil` | Todos os times do Brasil |
| `GET /teams?league=71&season=2026` | Times do Brasileirão 2026 |
| `GET /teams?id=127` | Flamengo (ID: 127) |
| `GET /teams?search=Flamengo` | Busca por nome |

**IDs Importantes:**
- **127** - Flamengo
- **128** - Palmeiras
- **129** - São Paulo
- **33** - Manchester United
- **50** - Manchester City

---

### 📊 **7. Status**
Verificar status da API e limites.

| Endpoint | Descrição |
|----------|-----------|
| `GET /status` | Status da conta (requests, limite, etc) |

---

## 🔑 Autenticação

Todos os requests usam **RapidAPI Headers**:

```
x-rapidapi-key: {{API_FOOTBALL_KEY}}
x-rapidapi-host: v3.football.api-sports.io
```

A variável `{{API_FOOTBALL_KEY}}` é substituída automaticamente pelo Postman.

---

## 📊 Limites da API

**Plano Gratuito:**
- ✅ **100 requests/dia**
- ✅ Dados ao vivo
- ✅ Odds de múltiplas casas
- ✅ Histórico de 3 anos

**⚠️ Dicas para Economizar Requests:**
1. **Cache local** dos dados (TTL: 6h para fixtures, 30min para odds)
2. Buscar múltiplos jogos de uma vez (`league` + `date`)
3. Filtrar por bookmaker específico quando possível
4. Usar `/status` para monitorar uso

---

## 🎯 Endpoints Mais Usados no Projeto

### Para o Betting Advisor, você vai precisar principalmente:

#### **1. Buscar Jogos do Dia**
```
GET /fixtures?league=71&date=2026-02-17
```

#### **2. Buscar Odds de um Jogo**
```
GET /odds?fixture={fixture_id}&bookmaker=6
```

#### **3. Buscar Times de uma Liga**
```
GET /teams?league=71&season=2026
```

#### **4. Verificar Limite Diário**
```
GET /status
```

---

## 📝 Exemplo de Response

### Fixture (Jogo)
```json
{
  "fixture": {
    "id": 1035148,
    "date": "2026-02-17T15:00:00+00:00",
    "status": {
      "short": "NS"
    },
    "venue": {
      "name": "Maracanã",
      "city": "Rio de Janeiro"
    }
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
```

### Odds (Cotações)
```json
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
            {
              "value": "Home",
              "odd": "2.10"
            },
            {
              "value": "Draw",
              "odd": "3.20"
            },
            {
              "value": "Away",
              "odd": "2.80"
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🔗 Links Úteis

- 📚 **Documentação Oficial:** https://www.api-football.com/documentation-v3
- 🏠 **Dashboard:** https://dashboard.api-football.com/
- 💬 **Suporte:** https://www.api-football.com/support

---

## ✅ Checklist de Uso

- [ ] Importar collection no Postman
- [ ] Configurar variável `API_FOOTBALL_KEY`
- [ ] Testar endpoint `/status` para verificar conexão
- [ ] Buscar ligas do Brasil (`/leagues?country=Brazil`)
- [ ] Buscar jogos de hoje (`/fixtures?date=2026-02-17`)
- [ ] Buscar odds de um jogo (`/odds?fixture={id}`)
- [ ] Verificar limite diário antes de desenvolver

---

**Collection pronta para uso! 🚀**

