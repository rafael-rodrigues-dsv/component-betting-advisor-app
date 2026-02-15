# 🔧 Betting Advisor - Backend API

API REST para análise e sugestão de apostas esportivas (Mockada para POC).

## 📋 Tecnologias

- **Python 3.14+**
- **FastAPI** - Framework web assíncrono
- **Uvicorn** - Servidor ASGI
- **Pydantic** - Validação de dados

## 🚀 Como Executar

### Windows

```bash
cd web_api
start.bat
```

### Linux/Mac

```bash
cd web_api
chmod +x start.sh
./start.sh
```

O script irá:
1. ✅ Criar ambiente virtual (`.venv`) se não existir
2. ✅ Instalar dependências do `requirements.txt`
3. ✅ Iniciar o servidor FastAPI na porta 8000

## 📡 Endpoints

### Jogos

- **GET** `/api/v1/matches` - Lista jogos disponíveis
  - Query params: `date`, `league_id`
- **GET** `/api/v1/matches/{id}` - Detalhes de um jogo
- **GET** `/api/v1/leagues` - Lista campeonatos
- **GET** `/api/v1/bookmakers` - Lista casas de apostas

### Previsões

- **POST** `/api/v1/analyze` - Analisa jogos selecionados
  - Body: `{ "match_ids": [...], "strategy": "BALANCED" }`
- **GET** `/api/v1/predictions` - Lista previsões
- **GET** `/api/v1/predictions/{id}` - Detalhes de uma previsão

### Bilhetes

- **POST** `/api/v1/tickets` - Cria um bilhete
- **GET** `/api/v1/tickets` - Lista bilhetes
- **GET** `/api/v1/tickets/{id}` - Detalhes de um bilhete
- **PUT** `/api/v1/tickets/{id}` - Atualiza bilhete
- **DELETE** `/api/v1/tickets/{id}` - Remove bilhete
- **POST** `/api/v1/tickets/{id}/simulate` - Simula resultado

## 📚 Documentação Interativa

Acesse após iniciar o servidor:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 Estrutura

```
web_api/
├── start.bat              # Script de inicialização (Windows)
├── start.sh               # Script de inicialização (Linux/Mac)
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── .venv/                # Ambiente virtual (criado automaticamente)
└── src/
    ├── main.py           # Ponto de entrada da API
    └── web/
        └── controllers/
            ├── match_controller.py       # Endpoints de jogos
            ├── prediction_controller.py  # Endpoints de previsões
            └── ticket_controller.py      # Endpoints de bilhetes
```

## 🎯 Estratégias de Análise

- **BALANCED** ⚖️ - Balanceada (padrão)
- **CONSERVATIVE** 🛡️ - Conservadora (maior confiança)
- **VALUE_BET** 💰 - Value Bet (maior expected value)
- **AGGRESSIVE** 🔥 - Agressiva (odds altas)

## 🏆 Ligas Disponíveis (Mock)

- 🇧🇷 **Brasileirão Série A** - 20 times
- 🏆 **Copa do Brasil** - Mata-mata
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **Premier League** - 20 times

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (opcional):

```env
# API
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 📝 Dependências

```
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
python-dotenv==1.0.0
httpx==0.26.0
```

## 🧪 Desenvolvimento

O backend está **100% mockado** para POC. Os dados retornados são gerados aleatoriamente para demonstração.

Para desenvolvimento futuro, substitua os controllers por:
- Integração com API-Football
- Modelo de IA para análise real
- Banco de dados real (SQLite/PostgreSQL)

## ⚠️ Importante

Este é um **projeto de demonstração**. Os dados são fictícios e não devem ser usados para apostas reais.

## 📞 Suporte

Para dúvidas, consulte a documentação em `/docs/`.

