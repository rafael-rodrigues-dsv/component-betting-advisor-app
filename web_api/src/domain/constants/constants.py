"""
Constants - Constantes do sistema
"""

# ============================================
# LIGAS (League IDs)
# ============================================
LEAGUE_BRASILEIRAO = 71
LEAGUE_COPA_BRASIL = 73
LEAGUE_PREMIER_LEAGUE = 39
LEAGUE_LA_LIGA = 140
LEAGUE_BUNDESLIGA = 78
LEAGUE_LIGUE_1 = 61
LEAGUE_SERIE_A = 135

# Mapeamento ID → Nome
LEAGUE_NAMES = {
    LEAGUE_BRASILEIRAO: "Brasileirão Série A",
    LEAGUE_COPA_BRASIL: "Copa do Brasil",
    LEAGUE_PREMIER_LEAGUE: "Premier League",
    LEAGUE_LA_LIGA: "La Liga",
    LEAGUE_BUNDESLIGA: "Bundesliga",
    LEAGUE_LIGUE_1: "Ligue 1",
    LEAGUE_SERIE_A: "Serie A"
}

# Mapeamento ID → País
LEAGUE_COUNTRIES = {
    LEAGUE_BRASILEIRAO: "Brazil",
    LEAGUE_COPA_BRASIL: "Brazil",
    LEAGUE_PREMIER_LEAGUE: "England",
    LEAGUE_LA_LIGA: "Spain",
    LEAGUE_BUNDESLIGA: "Germany",
    LEAGUE_LIGUE_1: "France",
    LEAGUE_SERIE_A: "Italy"
}


# Lista de ligas principais
MAIN_LEAGUES = [
    LEAGUE_BRASILEIRAO,
    LEAGUE_COPA_BRASIL,
    LEAGUE_PREMIER_LEAGUE,
    LEAGUE_LA_LIGA,
    LEAGUE_BUNDESLIGA,
    LEAGUE_LIGUE_1,
    LEAGUE_SERIE_A
]

# ============================================
# BOOKMAKERS (Bookmaker IDs)
# ============================================
BOOKMAKER_BET365_ID = 6
BOOKMAKER_BET365_NAME = "Bet365"

BOOKMAKER_BETANO_ID = 8
BOOKMAKER_BETANO_NAME = "Betano"

BOOKMAKER_BETFAIR_ID = 3
BOOKMAKER_BETFAIR_NAME = "Betfair"

BOOKMAKER_1XBET_ID = 1
BOOKMAKER_1XBET_NAME = "1xBet"

BOOKMAKER_PINNACLE_ID = 12
BOOKMAKER_PINNACLE_NAME = "Pinnacle"

# Mapeamento ID → Nome
BOOKMAKER_NAMES = {
    BOOKMAKER_BET365_ID: BOOKMAKER_BET365_NAME,
    BOOKMAKER_BETANO_ID: BOOKMAKER_BETANO_NAME,
    BOOKMAKER_BETFAIR_ID: BOOKMAKER_BETFAIR_NAME,
    BOOKMAKER_1XBET_ID: BOOKMAKER_1XBET_NAME,
    BOOKMAKER_PINNACLE_ID: BOOKMAKER_PINNACLE_NAME
}

# Lista de bookmakers principais
MAIN_BOOKMAKERS = [
    BOOKMAKER_BET365_ID,
    BOOKMAKER_BETANO_ID
]

# ============================================
# STATUS HTTP
# ============================================
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500

# Bookmakers suportadas
SUPPORTED_BOOKMAKERS = [
    "bet365",
    "betano",
    "betfair",
    "1xbet",
    "pinnacle"
]

# Estratégias de análise
STRATEGY_DESCRIPTIONS = {
    "CONSERVATIVE": "Favoritos seguros com alta confiança (>70%)",
    "BALANCED": "Mix equilibrado de risco e retorno",
    "VALUE_BET": "Busca discrepâncias entre casas (>5%)",
    "AGGRESSIVE": "Azarões com alto potencial de retorno"
}

# Thresholds
MIN_CONFIDENCE_CONSERVATIVE = 0.70  # 70%
MIN_CONFIDENCE_BALANCED = 0.60       # 60%
MIN_CONFIDENCE_VALUE_BET = 0.55      # 55%
MIN_CONFIDENCE_AGGRESSIVE = 0.25     # 25%

MIN_EV_CONSERVATIVE = 0.02           # 2%
MIN_EV_BALANCED = 0.02               # 2%
MIN_EV_VALUE_BET = 0.05              # 5%
MIN_EV_AGGRESSIVE = -0.05            # -5% (aceita negativo)

# Odds ranges
ODDS_RANGE_CONSERVATIVE = (1.50, 2.00)
ODDS_RANGE_BALANCED = (1.70, 3.50)
ODDS_RANGE_AGGRESSIVE = (3.00, 10.00)

# Cache keys patterns
CACHE_KEY_FIXTURES = "fixtures:{league_id}:{date}"
CACHE_KEY_ODDS = "odds:{fixture_id}"
CACHE_KEY_LEAGUES = "leagues"
CACHE_KEY_PRELOAD = "preload:last_date"

