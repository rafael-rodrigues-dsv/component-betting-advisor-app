"""
Match Controller - Lista de jogos (MOCK)
"""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
import random
import uuid

from web.dtos.responses.match_response import (
    MatchesListResponse,
    LeaguesListResponse,
    BookmakersListResponse
)

router = APIRouter()

# Cache global de matches gerados
MATCHES_CACHE = {}

# Mock data - Times por Liga

# G12 Brasileirão (Times Grandes)
G12_BRASILEIRAO = {
    "Flamengo", "Palmeiras", "São Paulo", "Corinthians", "Atlético Mineiro",
    "Fluminense", "Botafogo", "Grêmio", "Internacional", "Santos",
    "Vasco da Gama", "Cruzeiro"
}

# G6 Premier League (Times Grandes)
G6_PREMIER_LEAGUE = {
    "Manchester City", "Arsenal", "Liverpool", "Manchester United",
    "Newcastle", "Tottenham"
}

# Brasileirão Série A
TEAMS_BRASILEIRAO = [
    {"id": "t1", "name": "Flamengo", "logo": {"url": "/static/escudos/flamengo.png", "type": "LOCAL"}},
    {"id": "t2", "name": "Palmeiras", "logo": {"url": "/static/escudos/palmeiras.png", "type": "LOCAL"}},
    {"id": "t3", "name": "São Paulo", "logo": {"url": "/static/escudos/sao-paulo.png", "type": "LOCAL"}},
    {"id": "t4", "name": "Corinthians", "logo": {"url": "/static/escudos/corinthians.png", "type": "LOCAL"}},
    {"id": "t5", "name": "Atlético Mineiro", "logo": {"url": "/static/escudos/atletico-mineiro.png", "type": "LOCAL"}},
    {"id": "t6", "name": "Fluminense", "logo": {"url": "/static/escudos/fluminense.png", "type": "LOCAL"}},
    {"id": "t7", "name": "Botafogo", "logo": {"url": "/static/escudos/botafogo.png", "type": "LOCAL"}},
    {"id": "t8", "name": "Grêmio", "logo": {"url": "/static/escudos/gremio.png", "type": "LOCAL"}},
    {"id": "t9", "name": "Internacional", "logo": {"url": "/static/escudos/internacional.png", "type": "LOCAL"}},
    {"id": "t10", "name": "Santos", "logo": {"url": "/static/escudos/santos.png", "type": "LOCAL"}},
    {"id": "t11", "name": "Vasco da Gama", "logo": {"url": "/static/escudos/vasco.png", "type": "LOCAL"}},
    {"id": "t12", "name": "Cruzeiro", "logo": {"url": "/static/escudos/cruzeiro.png", "type": "LOCAL"}},
    {"id": "t14", "name": "Bahia", "logo": {"url": "/static/escudos/bahia.png", "type": "LOCAL"}},
    {"id": "t15", "name": "Fortaleza", "logo": {"url": "/static/escudos/fortaleza.png", "type": "LOCAL"}},
    {"id": "t16", "name": "Bragantino", "logo": {"url": "/static/escudos/bragantino.png", "type": "LOCAL"}},
    {"id": "t17", "name": "Cuiabá", "logo": {"url": "/static/escudos/cuiaba.png", "type": "LOCAL"}},
    {"id": "t18", "name": "Goiás", "logo": {"url": "/static/escudos/goias.png", "type": "LOCAL"}},
    {"id": "t19", "name": "Coritiba", "logo": {"url": "/static/escudos/coritiba.png", "type": "LOCAL"}},
    {"id": "t20", "name": "Atlético Goianiense", "logo": {"url": "/static/escudos/atletico-goianiense.png", "type": "LOCAL"}},
]

# Copa do Brasil (usando times brasileiros)
TEAMS_COPA_BRASIL = TEAMS_BRASILEIRAO.copy()

# Premier League
TEAMS_PREMIER_LEAGUE = [
    {"id": "tp1", "name": "Manchester City", "logo": {"url": "/static/escudos/manchester-city.png", "type": "LOCAL"}},
    {"id": "tp2", "name": "Arsenal", "logo": {"url": "/static/escudos/arsenal.png", "type": "LOCAL"}},
    {"id": "tp3", "name": "Liverpool", "logo": {"url": "/static/escudos/liverpool.png", "type": "LOCAL"}},
    {"id": "tp4", "name": "Manchester United", "logo": {"url": "/static/escudos/manchester-united.png", "type": "LOCAL"}},
    {"id": "tp5", "name": "Newcastle", "logo": {"url": "/static/escudos/newcastle.png", "type": "LOCAL"}},
    {"id": "tp6", "name": "Tottenham", "logo": {"url": "/static/escudos/tottenham.png", "type": "LOCAL"}},
    {"id": "tp7", "name": "Chelsea", "logo": {"url": "/static/escudos/chelsea.png", "type": "LOCAL"}},
    {"id": "tp8", "name": "Brighton", "logo": {"url": "/static/escudos/brighton.png", "type": "LOCAL"}},
    {"id": "tp9", "name": "Aston Villa", "logo": {"url": "/static/escudos/aston-villa.png", "type": "LOCAL"}},
    {"id": "tp10", "name": "West Ham", "logo": {"url": "/static/escudos/west-ham.png", "type": "LOCAL"}},
    {"id": "tp11", "name": "Fulham", "logo": {"url": "/static/escudos/fulham.png", "type": "LOCAL"}},
    {"id": "tp12", "name": "Brentford", "logo": {"url": "/static/escudos/brentford.png", "type": "LOCAL"}},
    {"id": "tp13", "name": "Crystal Palace", "logo": {"url": "/static/escudos/crystal-palace.png", "type": "LOCAL"}},
    {"id": "tp14", "name": "Wolverhampton", "logo": {"url": "/static/escudos/wolverhampton.png", "type": "LOCAL"}},
    {"id": "tp15", "name": "Nottingham Forest", "logo": {"url": "/static/escudos/nottingham-forest.png", "type": "LOCAL"}},
    {"id": "tp16", "name": "Everton", "logo": {"url": "/static/escudos/everton.png", "type": "LOCAL"}},
    {"id": "tp17", "name": "Leicester", "logo": {"url": "/static/escudos/leicester.png", "type": "LOCAL"}},
    {"id": "tp18", "name": "Leeds United", "logo": {"url": "/static/escudos/leeds-united.png", "type": "LOCAL"}},
    {"id": "tp19", "name": "Southampton", "logo": {"url": "/static/escudos/southampton.png", "type": "LOCAL"}},
    {"id": "tp20", "name": "Bournemouth", "logo": {"url": "/static/escudos/bournemouth.png", "type": "LOCAL"}},
]

# Mapa de times por liga
TEAMS_BY_LEAGUE = {
    "l1": TEAMS_BRASILEIRAO,
    "l2": TEAMS_COPA_BRASIL,
    "l3": TEAMS_PREMIER_LEAGUE,
}

LEAGUES = [
    {"id": "l1", "name": "Brasileirão Série A", "country": "Brazil", "logo": "🇧🇷", "type": "league"},
    {"id": "l2", "name": "Copa do Brasil", "country": "Brazil", "logo": "🏆", "type": "cup"},
    {"id": "l3", "name": "Premier League", "country": "England", "logo": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "type": "league"},
]

BOOKMAKERS = [
    {"id": "bet365", "name": "Bet365", "logo": "🎰", "is_default": True},
    {"id": "betano", "name": "Betano", "logo": "⚡", "is_default": False},
]

# Estádios reais dos times
STADIUMS = {
    # Brasileirão
    "Flamengo": {"name": "Maracanã", "city": "Rio de Janeiro"},
    "Palmeiras": {"name": "Allianz Parque", "city": "São Paulo"},
    "São Paulo": {"name": "Morumbi", "city": "São Paulo"},
    "Corinthians": {"name": "Neo Química Arena", "city": "São Paulo"},
    "Atlético Mineiro": {"name": "Arena MRV", "city": "Belo Horizonte"},
    "Fluminense": {"name": "Maracanã", "city": "Rio de Janeiro"},
    "Botafogo": {"name": "Estádio Nilton Santos", "city": "Rio de Janeiro"},
    "Grêmio": {"name": "Arena do Grêmio", "city": "Porto Alegre"},
    "Internacional": {"name": "Beira-Rio", "city": "Porto Alegre"},
    "Santos": {"name": "Vila Belmiro", "city": "Santos"},
    "Vasco da Gama": {"name": "São Januário", "city": "Rio de Janeiro"},
    "Cruzeiro": {"name": "Mineirão", "city": "Belo Horizonte"},
    "Athletico Paranaense": {"name": "Ligga Arena", "city": "Curitiba"},
    "Bahia": {"name": "Arena Fonte Nova", "city": "Salvador"},
    "Fortaleza": {"name": "Castelão", "city": "Fortaleza"},
    "Bragantino": {"name": "Nabi Abi Chedid", "city": "Bragança Paulista"},
    "Cuiabá": {"name": "Arena Pantanal", "city": "Cuiabá"},
    "Goiás": {"name": "Estádio da Serrinha", "city": "Goiânia"},
    "Coritiba": {"name": "Couto Pereira", "city": "Curitiba"},
    "Atlético Goianiense": {"name": "Antônio Accioly", "city": "Goiânia"},

    # Premier League
    "Manchester City": {"name": "Etihad Stadium", "city": "Manchester"},
    "Arsenal": {"name": "Emirates Stadium", "city": "London"},
    "Liverpool": {"name": "Anfield", "city": "Liverpool"},
    "Manchester United": {"name": "Old Trafford", "city": "Manchester"},
    "Newcastle": {"name": "St James' Park", "city": "Newcastle"},
    "Tottenham": {"name": "Tottenham Hotspur Stadium", "city": "London"},
    "Chelsea": {"name": "Stamford Bridge", "city": "London"},
    "Brighton": {"name": "Amex Stadium", "city": "Brighton"},
    "Aston Villa": {"name": "Villa Park", "city": "Birmingham"},
    "West Ham": {"name": "London Stadium", "city": "London"},
    "Fulham": {"name": "Craven Cottage", "city": "London"},
    "Brentford": {"name": "Gtech Community Stadium", "city": "London"},
    "Crystal Palace": {"name": "Selhurst Park", "city": "London"},
    "Wolverhampton": {"name": "Molineux Stadium", "city": "Wolverhampton"},
    "Nottingham Forest": {"name": "City Ground", "city": "Nottingham"},
    "Everton": {"name": "Goodison Park", "city": "Liverpool"},
    "Leicester": {"name": "King Power Stadium", "city": "Leicester"},
    "Leeds United": {"name": "Elland Road", "city": "Leeds"},
    "Southampton": {"name": "St Mary's Stadium", "city": "Southampton"},
    "Bournemouth": {"name": "Vitality Stadium", "city": "Bournemouth"},
}


def _is_big_team(team_name: str, league_id: str) -> bool:
    """Verifica se o time é um dos grandes da liga"""
    if league_id in ["l1", "l2"]:  # Brasileirão ou Copa do Brasil
        return team_name in G12_BRASILEIRAO
    elif league_id == "l3":  # Premier League
        return team_name in G6_PREMIER_LEAGUE
    return False


def _calculate_realistic_odds(home_team: dict, away_team: dict, league_id: str) -> dict:
    """
    Calcula odds realistas baseadas na força dos times.
    Times grandes (G12/G6) têm odds favoráveis contra times menores.
    """
    home_is_big = _is_big_team(home_team["name"], league_id)
    away_is_big = _is_big_team(away_team["name"], league_id)

    # Caso 1: Grande x Pequeno (mandante grande favorito)
    if home_is_big and not away_is_big:
        home_odd = round(random.uniform(1.35, 1.75), 2)  # Grande favorito
        draw_odd = round(random.uniform(3.5, 4.5), 2)
        away_odd = round(random.uniform(5.0, 9.0), 2)  # Pequeno azarão
        over_25 = round(random.uniform(1.50, 1.80), 2)  # Provável muitos gols
        under_25 = round(random.uniform(2.0, 2.5), 2)
        btts_yes = round(random.uniform(1.95, 2.20), 2)
        btts_no = round(random.uniform(1.70, 1.90), 2)

    # Caso 2: Pequeno x Grande (visitante grande é favorito, mas não tanto)
    elif not home_is_big and away_is_big:
        home_odd = round(random.uniform(4.5, 8.0), 2)  # Pequeno azarão em casa
        draw_odd = round(random.uniform(3.2, 4.0), 2)
        away_odd = round(random.uniform(1.50, 1.90), 2)  # Grande favorito como visitante
        over_25 = round(random.uniform(1.60, 1.90), 2)
        under_25 = round(random.uniform(1.90, 2.30), 2)
        btts_yes = round(random.uniform(1.85, 2.10), 2)
        btts_no = round(random.uniform(1.75, 2.00), 2)

    # Caso 3: Grande x Grande (jogo equilibrado com leve vantagem mandante)
    elif home_is_big and away_is_big:
        home_odd = round(random.uniform(2.00, 2.50), 2)  # Vantagem do mandante
        draw_odd = round(random.uniform(3.0, 3.6), 2)
        away_odd = round(random.uniform(2.80, 3.80), 2)
        over_25 = round(random.uniform(1.70, 2.00), 2)  # Jogos abertos
        under_25 = round(random.uniform(1.80, 2.10), 2)
        btts_yes = round(random.uniform(1.70, 1.95), 2)
        btts_no = round(random.uniform(1.90, 2.20), 2)

    # Caso 4: Pequeno x Pequeno (jogo mais equilibrado)
    else:
        home_odd = round(random.uniform(2.20, 2.80), 2)  # Leve vantagem mandante
        draw_odd = round(random.uniform(2.90, 3.50), 2)
        away_odd = round(random.uniform(2.50, 3.50), 2)
        over_25 = round(random.uniform(1.80, 2.20), 2)
        under_25 = round(random.uniform(1.70, 2.10), 2)
        btts_yes = round(random.uniform(1.80, 2.10), 2)
        btts_no = round(random.uniform(1.75, 2.00), 2)

    return {
        "home": home_odd,
        "draw": draw_odd,
        "away": away_odd,
        "over_25": over_25,
        "under_25": under_25,
        "btts_yes": btts_yes,
        "btts_no": btts_no,
    }


def _generate_matches(date: str, league_id: Optional[str] = None) -> list:
    """Gera jogos mockados de todas as ligas ou de uma liga específica"""
    from datetime import datetime, timedelta

    matches = []

    # Converte data string para datetime para cálculos
    base_date = datetime.strptime(date, "%Y-%m-%d")
    weekday = base_date.weekday()  # 0=Segunda, 5=Sábado, 6=Domingo

    # Se league_id foi especificado, gera apenas para essa liga
    leagues_to_generate = [l for l in LEAGUES if l["id"] == league_id] if league_id else LEAGUES

    for league in leagues_to_generate:
        # Pega os times da liga
        teams = TEAMS_BY_LEAGUE.get(league["id"], [])
        if not teams:
            continue

        # Copia lista de times para não modificar original
        available_teams = teams.copy()
        random.shuffle(available_teams)

        # Define horários e datas baseado na liga
        match_dates = []

        if league["id"] == "l1":  # Brasileirão Série A
            # Brasileirão: Sábado e Domingo
            # Se hoje é sábado ou domingo, usa hoje
            # Senão, calcula próximo sábado
            if weekday == 5:  # Sábado
                saturday = base_date
                sunday = base_date + timedelta(days=1)
            elif weekday == 6:  # Domingo
                saturday = base_date - timedelta(days=1)
                sunday = base_date
            else:
                # Calcula próximo sábado
                days_until_saturday = (5 - weekday) % 7
                saturday = base_date + timedelta(days=days_until_saturday)
                sunday = saturday + timedelta(days=1)

            # Horários brasileirão: 16h, 18h30, 19h, 20h, 21h
            hours_saturday = [16, 18, 19, 21]
            hours_sunday = [16, 18, 19, 20]

            # Distribui jogos entre sábado e domingo
            num_matches = min(random.randint(8, 10), len(available_teams) // 2)
            matches_per_day = num_matches // 2

            for i in range(matches_per_day):
                match_dates.append((saturday.strftime("%Y-%m-%d"), random.choice(hours_saturday)))
            for i in range(num_matches - matches_per_day):
                match_dates.append((sunday.strftime("%Y-%m-%d"), random.choice(hours_sunday)))

        elif league["id"] == "l2":  # Copa do Brasil
            # Copa do Brasil: Quarta e Quinta APÓS rodada do Brasileirão
            # Próxima quarta após domingo do brasileirão
            if weekday == 5:  # Sábado
                sunday = base_date + timedelta(days=1)
            elif weekday == 6:  # Domingo
                sunday = base_date
            else:
                days_until_saturday = (5 - weekday) % 7
                sunday = base_date + timedelta(days=days_until_saturday + 1)

            wednesday = sunday + timedelta(days=3)  # Domingo + 3 = Quarta
            thursday = wednesday + timedelta(days=1)

            # Horários Copa do Brasil: 19h, 21h30
            hours_copa = [19, 21]

            num_matches = min(random.randint(4, 6), len(available_teams) // 2)
            matches_per_day = num_matches // 2

            for i in range(matches_per_day):
                match_dates.append((wednesday.strftime("%Y-%m-%d"), random.choice(hours_copa)))
            for i in range(num_matches - matches_per_day):
                match_dates.append((thursday.strftime("%Y-%m-%d"), random.choice(hours_copa)))

        elif league["country"] == "England":
            # Premier League: Sábado, Domingo e Segunda (poucos jogos na segunda)
            if weekday == 5:  # Sábado
                saturday = base_date
                sunday = base_date + timedelta(days=1)
                monday = base_date + timedelta(days=2)
            elif weekday == 6:  # Domingo
                saturday = base_date - timedelta(days=1)
                sunday = base_date
                monday = base_date + timedelta(days=1)
            elif weekday == 0:  # Segunda
                saturday = base_date - timedelta(days=2)
                sunday = base_date - timedelta(days=1)
                monday = base_date
            else:
                days_until_saturday = (5 - weekday) % 7
                saturday = base_date + timedelta(days=days_until_saturday)
                sunday = saturday + timedelta(days=1)
                monday = saturday + timedelta(days=2)

            # Horários Premier League
            hours_saturday = [12, 15, 17]  # Hora de Londres (UTC)
            hours_sunday = [14, 16]
            hours_monday = [20]  # Monday Night Football

            num_matches = min(random.randint(8, 10), len(available_teams) // 2)

            # Distribui: 50% sábado, 40% domingo, 10% segunda
            num_saturday = int(num_matches * 0.5)
            num_sunday = int(num_matches * 0.4)
            num_monday = num_matches - num_saturday - num_sunday

            for i in range(num_saturday):
                match_dates.append((saturday.strftime("%Y-%m-%d"), random.choice(hours_saturday)))
            for i in range(num_sunday):
                match_dates.append((sunday.strftime("%Y-%m-%d"), random.choice(hours_sunday)))
            for i in range(num_monday):
                match_dates.append((monday.strftime("%Y-%m-%d"), random.choice(hours_monday)))
        else:
            # Outras ligas: mantém comportamento padrão
            hours = [15, 18, 20]
            num_matches = min(random.randint(4, 6), len(available_teams) // 2)
            for i in range(num_matches):
                match_dates.append((date, random.choice(hours)))

        # Define rodada/fase baseado no tipo de competição
        if league["type"] == "league":
            # Pontos corridos: rodada aleatória
            round_number = random.randint(1, 38)
            round_info = {"type": "round", "number": round_number, "name": f"Rodada {round_number}"}
        else:
            # Copa: fase aleatória
            phases = ["Oitavas de Final", "Quartas de Final", "Semifinal", "Final"]
            phase = random.choice(phases)
            round_info = {"type": "phase", "name": phase}

        # Gera as partidas
        for i, (match_date, hour) in enumerate(match_dates):
            if i * 2 + 1 >= len(available_teams):
                break

            home = available_teams[i * 2]
            away = available_teams[i * 2 + 1]

            # Pegar estádio real do time da casa
            stadium = STADIUMS.get(home['name'], {"name": "Estádio Municipal", "city": "Cidade"})

            # Calcula odds realistas baseadas na força dos times
            odds_bet365 = _calculate_realistic_odds(home, away, league["id"])

            # Betano tem variação de -3% a +3% nas odds (menor para manter realismo)
            odds_betano = {
                "home": round(odds_bet365["home"] * random.uniform(0.97, 1.03), 2),
                "draw": round(odds_bet365["draw"] * random.uniform(0.97, 1.03), 2),
                "away": round(odds_bet365["away"] * random.uniform(0.97, 1.03), 2),
                "over_25": round(odds_bet365["over_25"] * random.uniform(0.97, 1.03), 2),
                "under_25": round(odds_bet365["under_25"] * random.uniform(0.97, 1.03), 2),
                "btts_yes": round(odds_bet365["btts_yes"] * random.uniform(0.97, 1.03), 2),
                "btts_no": round(odds_bet365["btts_no"] * random.uniform(0.97, 1.03), 2),
            }

            matches.append({
                "id": str(uuid.uuid4()),
                "league": league,
                "home_team": home,
                "away_team": away,
                "date": f"{match_date}T{hour:02d}:00:00Z",
                "status": "NS",
                "round": round_info,
                "venue": stadium,
                "odds": {
                    "bet365": odds_bet365,
                    "betano": odds_betano
                }
            })


    return matches


@router.get("/matches")
async def get_matches(
    date: Optional[str] = Query(None, description="Data no formato YYYY-MM-D"),
    league_id: Optional[str] = Query(None, description="Filtrar por ID da liga")
):
    """Lista jogos disponíveis para análise"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    matches = _generate_matches(date, league_id)

    # Ordena jogos por data e hora
    matches.sort(key=lambda m: m["date"])

    # Adiciona matches ao cache global para uso nos predictions
    for match in matches:
        MATCHES_CACHE[match["id"]] = match

    print(f"[DEBUG] Data: {date}, League: {league_id}, Total jogos: {len(matches)}")

    return {
        "success": True,
        "date": date,
        "count": len(matches),
        "matches": matches
    }


@router.get("/leagues", response_model=LeaguesListResponse)
async def get_leagues() -> LeaguesListResponse:
    """Lista campeonatos disponíveis"""
    return LeaguesListResponse(
        success=True,
        count=len(LEAGUES),
        leagues=LEAGUES
    )


@router.get("/bookmakers", response_model=BookmakersListResponse)
async def get_bookmakers() -> BookmakersListResponse:
    """Lista casas de apostas disponíveis"""
    return BookmakersListResponse(
        success=True,
        count=len(BOOKMAKERS),
        bookmakers=BOOKMAKERS
    )


@router.get("/matches/{match_id}")
async def get_match(match_id: str):
    """Detalhes de um jogo"""
    # Seleciona uma liga aleatória
    league = random.choice(LEAGUES)
    teams = TEAMS_BY_LEAGUE.get(league["id"], TEAMS_BRASILEIRAO)

    home = random.choice(teams)
    away = random.choice([t for t in teams if t["id"] != home["id"]])

    return {
        "success": True,
        "match": {
            "id": match_id,
            "league": league,
            "home_team": home,
            "away_team": away,
            "date": datetime.now().isoformat(),
            "status": "NS",
            "odds": {
                "home": round(random.uniform(1.5, 3.5), 2),
                "draw": round(random.uniform(2.8, 4.2), 2),
                "away": round(random.uniform(1.5, 3.5), 2),
            },
            "stats": {
                "home": {"form": "WWDLW", "goals_scored": 18, "goals_conceded": 8},
                "away": {"form": "WDWLD", "goals_scored": 14, "goals_conceded": 11}
            }
        }
    }

