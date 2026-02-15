# 📮 Postman Collection - API-Football

## 📋 O que contém

Collection completa para testar a API-Football com foco em times brasileiros e escudos.

### 📁 Estrutura Organizada:

```
API-Football - Escudos e Times
│
├── 🇧🇷 Times Brasileiros
│   ├── Buscar Time por Nome
│   ├── Todos os Times do Brasil
│   └── Time por ID
│
├── ⚽ Times Específicos - Brasileirão (20 times)
│   ├── Flamengo (ID: 127)
│   ├── Palmeiras (ID: 128)
│   ├── São Paulo (ID: 126)
│   ├── Corinthians (ID: 131)
│   ├── Atlético Mineiro (ID: 129)
│   ├── ... (mais 15 times)
│   └── Atlético-GO (ID: 155)
│
├── 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Times Premier League (6 principais)
│   ├── Manchester City (ID: 50)
│   ├── Arsenal (ID: 42)
│   ├── Liverpool (ID: 40)
│   └── ... (mais 3 times)
│
└── 🔍 Utilitários
    ├── Listar Países
    └── Listar Ligas do Brasil
```

---

## 🚀 Como Importar no Postman

### 1️⃣ Via Arquivo

1. Abra o Postman
2. Clique em **Import** (canto superior esquerdo)
3. Selecione o arquivo: `API-Football-Collection.postman_collection.json`
4. Clique em **Import**
5. ✅ Pronto! A collection aparecerá na barra lateral

### 2️⃣ Via Drag & Drop

1. Abra o Postman
2. Arraste o arquivo `.json` para a janela do Postman
3. ✅ Importado automaticamente!

---

## 🔑 Configurar API Key

### Se você TEM API Key (cadastro em api-football.com):

1. No Postman, abra a Collection importada
2. Clique na aba **Variables**
3. Altere o valor de `API_KEY`:
   - Current Value: `SUA_API_KEY_REAL`
4. Salve (Ctrl+S)

### Se você NÃO TEM API Key:

**Boa notícia:** Os escudos (CDN) **NÃO precisam de API Key!**

- ✅ Pasta **"⚽ Times Específicos - Brasileirão"** → Funciona sem API Key
- ✅ Pasta **"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Times Premier League"** → Funciona sem API Key
- ❌ Pasta **"🇧🇷 Times Brasileiros"** → Precisa de API Key
- ❌ Pasta **"🔍 Utilitários"** → Precisa de API Key

---

## 🎯 Como Usar

### 1. Baixar Escudos (SEM API Key necessária)

1. Abra pasta: **"⚽ Times Específicos - Brasileirão"**
2. Clique em qualquer time (ex: **"Flamengo (ID: 127)"**)
3. Clique em **Send**
4. ✅ O escudo PNG aparecerá na resposta!
5. Clique em **Save Response** → **Save to a file** para salvar

**Exemplo:**
```
GET https://media.api-sports.io/football/teams/127.png
```
Resposta: Imagem PNG do escudo do Flamengo

### 2. Buscar Time por Nome (COM API Key)

1. Configure sua API Key (veja seção acima)
2. Abra pasta: **"🇧🇷 Times Brasileiros"**
3. Clique em **"Buscar Time por Nome"**
4. Na aba **Params**, altere `team_name`:
   - Value: `Flamengo` (ou outro time)
5. Clique em **Send**
6. ✅ Receberá JSON com ID, nome, logo, estádio, etc.

**Exemplo de Resposta:**
```json
{
  "response": [
    {
      "team": {
        "id": 127,
        "name": "Flamengo",
        "code": "FLA",
        "country": "Brazil",
        "founded": 1895,
        "national": false,
        "logo": "https://media.api-sports.io/football/teams/127.png"
      },
      "venue": {
        "id": 247,
        "name": "Estádio do Maracanã",
        "address": "Rua Professor Eurico Rabelo",
        "city": "Rio de Janeiro",
        "capacity": 78838
      }
    }
  ]
}
```

### 3. Listar Todos os Times do Brasil

1. Configure API Key
2. Abra: **"🇧🇷 Times Brasileiros"** → **"Todos os Times do Brasil"**
3. Clique em **Send**
4. ✅ Receberá lista com TODOS os times brasileiros

---

## 📝 Variáveis Disponíveis

A collection tem 3 variáveis configuráveis:

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `API_KEY` | `SUA_API_KEY_AQUI` | Sua chave da API-Football |
| `team_name` | `Flamengo` | Nome do time para busca |
| `team_id` | `127` | ID do time para busca |

**Para alterar:**
1. Clique na Collection
2. Aba **Variables**
3. Altere **Current Value**
4. Salve

---

## 🎨 Endpoints Organizados

### 🇧🇷 Times Brasileiros (Brasileirão Série A)

| Time | ID | URL Escudo |
|------|----|-----------| 
| Flamengo | 127 | `https://media.api-sports.io/football/teams/127.png` |
| Palmeiras | 128 | `https://media.api-sports.io/football/teams/128.png` |
| São Paulo | 126 | `https://media.api-sports.io/football/teams/126.png` |
| Corinthians | 131 | `https://media.api-sports.io/football/teams/131.png` |
| Atlético-MG | 129 | `https://media.api-sports.io/football/teams/129.png` |
| Fluminense | 124 | `https://media.api-sports.io/football/teams/124.png` |
| Botafogo | 141 | `https://media.api-sports.io/football/teams/141.png` |
| Grêmio | 154 | `https://media.api-sports.io/football/teams/154.png` |
| Internacional | 130 | `https://media.api-sports.io/football/teams/130.png` |
| Santos | 125 | `https://media.api-sports.io/football/teams/125.png` |
| Vasco | 145 | `https://media.api-sports.io/football/teams/145.png` |
| Cruzeiro | 138 | `https://media.api-sports.io/football/teams/138.png` |
| Athletico-PR | 158 | `https://media.api-sports.io/football/teams/158.png` |
| Bahia | 159 | `https://media.api-sports.io/football/teams/159.png` |
| Fortaleza | 150 | `https://media.api-sports.io/football/teams/150.png` |
| Bragantino | 132 | `https://media.api-sports.io/football/teams/132.png` |
| Cuiabá | 2829 | `https://media.api-sports.io/football/teams/2829.png` |
| Goiás | 153 | `https://media.api-sports.io/football/teams/153.png` |
| Coritiba | 146 | `https://media.api-sports.io/football/teams/146.png` |
| Atlético-GO | 155 | `https://media.api-sports.io/football/teams/155.png` |

### 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Times Premier League

| Time | ID | URL Escudo |
|------|----|-----------| 
| Manchester City | 50 | `https://media.api-sports.io/football/teams/50.png` |
| Arsenal | 42 | `https://media.api-sports.io/football/teams/42.png` |
| Liverpool | 40 | `https://media.api-sports.io/football/teams/40.png` |
| Manchester United | 33 | `https://media.api-sports.io/football/teams/33.png` |
| Chelsea | 49 | `https://media.api-sports.io/football/teams/49.png` |
| Tottenham | 47 | `https://media.api-sports.io/football/teams/47.png` |

---

## 💡 Dicas

### 1. Baixar Múltiplos Escudos

Use o **Collection Runner**:
1. Clique com botão direito na pasta **"⚽ Times Específicos - Brasileirão"**
2. Escolha **Run collection**
3. Clique em **Run**
4. ✅ Todos os 20 escudos serão testados automaticamente!

### 2. Exportar Escudo como PNG

No Postman, após fazer o request:
1. Vá em **Response**
2. Clique em **Save Response**
3. Escolha **Save to a file**
4. Salve como `.png`

### 3. Ver Escudo no Postman

Requests de escudos mostram a imagem diretamente no Postman! Não precisa baixar para ver.

---

## ⚠️ Limitações

### API Key Gratuita:
- ✅ 100 requisições por dia
- ✅ Escudos (CDN): **ILIMITADO** (não conta na cota)
- ❌ Busca de times/jogos: conta na cota

### Sem API Key:
- ✅ Escudos (CDN): **FUNCIONA**
- ❌ Busca de times: **NÃO FUNCIONA**
- ❌ Busca de ligas: **NÃO FUNCIONA**

---

## 🔗 Links Úteis

- 🌐 API-Football: https://www.api-football.com/
- 📚 Documentação: https://www.api-football.com/documentation-v3
- 🔑 Obter API Key: https://dashboard.api-football.com/register
- 📮 Postman: https://www.postman.com/downloads/

---

## ✅ Checklist de Uso

- [ ] Importei a collection no Postman
- [ ] (Opcional) Configurei minha API Key
- [ ] Testei baixar escudo do Flamengo
- [ ] (Com API Key) Busquei time por nome
- [ ] Explorei outros times brasileiros
- [ ] Salvei escudos que preciso

---

## 🎉 Pronto!

Agora você tem uma collection completa e organizada para trabalhar com a API-Football!

**Arquivo criado:** `API-Football-Collection.postman_collection.json`

**Para usar:** Importe no Postman e divirta-se! 🚀

