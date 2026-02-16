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

# Mock data - Times por Liga

# Brasileirão Série A
TEAMS_BRASILEIRAO = [
    {"id": "t1", "name": "Flamengo", "logo": "/escudos/flamengo.png"},
    {"id": "t2", "name": "Palmeiras", "logo": "/escudos/palmeiras.png"},
    {"id": "t3", "name": "São Paulo", "logo": "/escudos/sao-paulo.png"},
    {"id": "t4", "name": "Corinthians", "logo": "/escudos/corinthians.png"},
    {"id": "t5", "name": "Atlético Mineiro", "logo": "/escudos/atletico-mineiro.png"},
    {"id": "t6", "name": "Fluminense", "logo": "/escudos/fluminense.png"},
    {"id": "t7", "name": "Botafogo", "logo": "/escudos/botafogo.png"},
    {"id": "t8", "name": "Grêmio", "logo": "/escudos/gremio.png"},
    {"id": "t9", "name": "Internacional", "logo": "/escudos/internacional.png"},
    {"id": "t10", "name": "Santos", "logo": "/escudos/santos.png"},
    {"id": "t11", "name": "Vasco da Gama", "logo": "/escudos/vasco.png"},
    {"id": "t12", "name": "Cruzeiro", "logo": "/escudos/cruzeiro.png"},
    {"id": "t13", "name": "Athletico Paranaense", "logo": "/escudos/athletico-paranaense.png"},
    {"id": "t14", "name": "Bahia", "logo": "/escudos/bahia.png"},
    {"id": "t15", "name": "Fortaleza", "logo": "/escudos/fortaleza.png"},
    {"id": "t16", "name": "Bragantino", "logo": "/escudos/bragantino.png"},
    {"id": "t17", "name": "Cuiabá", "logo": "/escudos/cuiaba.png"},
    {"id": "t18", "name": "Goiás", "logo": "/escudos/goias.png"},
    {"id": "t19", "name": "Coritiba", "logo": "/escudos/coritiba.png"},
    {"id": "t20", "name": "Atlético Goianiense", "logo": "/escudos/atletico-goianiense.png"},
]

# Copa do Brasil (usando times brasileiros)
TEAMS_COPA_BRASIL = TEAMS_BRASILEIRAO.copy()

# Premier League
TEAMS_PREMIER_LEAGUE = [
    {"id": "tp1", "name": "Manchester City", "logo": "/escudos/manchester-city.png"},
    {"id": "tp2", "name": "Arsenal", "logo": "/escudos/arsenal.png"},
    {"id": "tp3", "name": "Liverpool", "logo": "/escudos/liverpool.png"},
    {"id": "tp4", "name": "Manchester United", "logo": "/escudos/manchester-united.png"},
    {"id": "tp5", "name": "Newcastle", "logo": "/escudos/newcastle.png"},
    {"id": "tp6", "name": "Tottenham", "logo": "/escudos/tottenham.png"},
    {"id": "tp7", "name": "Chelsea", "logo": "/escudos/chelsea.png"},
    {"id": "tp8", "name": "Brighton", "logo": "/escudos/brighton.png"},
    {"id": "tp9", "name": "Aston Villa", "logo": "/escudos/aston-villa.png"},
    {"id": "tp10", "name": "West Ham", "logo": "/escudos/west-ham.png"},
    {"id": "tp11", "name": "Fulham", "logo": "/escudos/fulham.png"},
    {"id": "tp12", "name": "Brentford", "logo": "/escudos/brentford.png"},
    {"id": "tp13", "name": "Crystal Palace", "logo": "/escudos/crystal-palace.png"},
    {"id": "tp14", "name": "Wolverhampton", "logo": "/escudos/wolverhampton.png"},
    {"id": "tp15", "name": "Nottingham Forest", "logo": "/escudos/nottingham-forest.png"},
    {"id": "tp16", "name": "Everton", "logo": "/escudos/everton.png"},
    {"id": "tp17", "name": "Leicester", "logo": "/escudos/leicester.png"},
    {"id": "tp18", "name": "Leeds United", "logo": "/escudos/leeds-united.png"},
    {"id": "tp19", "name": "Southampton", "logo": "/escudos/southampton.png"},
    {"id": "tp20", "name": "Bournemouth", "logo": "/escudos/bournemouth.png"},
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
    {"id": "b1", "name": "Bet365", "logo": "🎰"},
    {"id": "b2", "name": "Betano", "logo": "⚡"},
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
                    "home": round(random.uniform(1.5, 3.5), 2),
                    "draw": round(random.uniform(2.8, 4.2), 2),
                    "away": round(random.uniform(1.5, 3.5), 2),
                    "over_25": round(random.uniform(1.6, 2.3), 2),
                    "under_25": round(random.uniform(1.6, 2.3), 2),
                    "btts_yes": round(random.uniform(1.6, 2.1), 2),
                    "btts_no": round(random.uniform(1.6, 2.1), 2),
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

