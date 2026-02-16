# 🤖 Betting Bot - Modelos de IA (V2)

> Modelos de IA planejados para previsão de apostas - **Status: Planejado**

**Data:** 2026-02-17  
**Versão:** 2.0.0  
**Status:** ⏳ Planejado (não implementado ainda)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Status Atual (POC)](#status-atual-poc)
3. [Modelo Poisson (Planejado)](#modelo-poisson-planejado)
4. [Modelo XGBoost (Planejado)](#modelo-xgboost-planejado)
5. [Ensemble (Combinação)](#ensemble-combinação)
6. [Estratégias de Apostas](#estratégias-de-apostas)
7. [Value Bet Calculator](#value-bet-calculator)
8. [Dados Históricos](#dados-históricos)
9. [Pipeline de Implementação](#pipeline-de-implementação)

---

## 🎯 Visão Geral

O sistema utilizará **dois modelos de IA complementares** para gerar previsões:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🧠 ARQUITETURA DE IA (PLANEJADA)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   📊 DADOS DE ENTRADA (API-Football)                                        │
│   ├─ Estatísticas dos times                                                │
│   ├─ Histórico Head-to-Head                                                │
│   ├─ Forma recente                                                         │
│   ├─ Odds do mercado                                                       │
│   └─ Contexto (mandante/visitante, liga, etc.)                             │
│                                                                             │
│                                 │                                           │
│                                 ▼                                           │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     PROCESSAMENTO PARALELO                          │  │
│   │                                                                     │  │
│   │   ┌─────────────────────┐       ┌─────────────────────┐            │  │
│   │   │                     │       │                     │            │  │
│   │   │   🎲 POISSON        │       │   🤖 XGBOOST        │            │  │
│   │   │   (Estatístico)     │       │   (Machine Learning)│            │  │
│   │   │                     │       │                     │            │  │
│   │   │   Especialista em:  │       │   Especialista em:  │            │  │
│   │   │   • Over/Under      │       │   • Resultado 1X2   │            │  │
│   │   │   • BTTS (Ambas     │       │   • Padrões         │            │  │
│   │   │     Marcam)         │       │     complexos       │            │  │
│   │   │   • Total de Gols   │       │   • Interações      │            │  │
│   │   │                     │       │     não-lineares    │            │  │
│   │   └──────────┬──────────┘       └──────────┬──────────┘            │  │
│   │              │                               │                      │  │
│   │              │    Probabilidades            │                      │  │
│   │              └───────────────┬──────────────┘                      │  │
│   │                              │                                     │  │
│   └──────────────────────────────┼─────────────────────────────────────┘  │
│                                  │                                         │
│                                  ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                     🔄 ENSEMBLE (Combinação)                        │  │
│   │                                                                     │  │
│   │        Combina os dois modelos com pesos ajustáveis:                │  │
│   │        Poisson (40%) + XGBoost (60%) = Probabilidade Final         │  │
│   │                                                                     │  │
│   └─────────────────────────────┬───────────────────────────────────────┘  │
│                                  │                                         │
│                                  ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    💰 VALUE BET CALCULATOR                          │  │
│   │                                                                     │  │
│   │      Value Bet % = (Prob. Modelo - Prob. Odd) / Prob. Odd × 100   │  │
│   │                                                                     │  │
│   │      Se Value Bet > 0 → Aposta tem valor esperado positivo ✅      │  │
│   │                                                                     │  │
│   └─────────────────────────────┬───────────────────────────────────────┘  │
│                                  │                                         │
│                                  ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    🎯 APLICAÇÃO DE ESTRATÉGIA                       │  │
│   │                                                                     │  │
│   │   ⚖️ BALANCED:      confiança >= 65% E value_bet >= 5%             │  │
│   │   🛡️ CONSERVATIVE:  confiança >= 75%                               │  │
│   │   💰 VALUE_BET:     value_bet >= 10%                               │  │
│   │   🔥 AGGRESSIVE:    odd >= 2.5                                     │  │
│   │                                                                     │  │
│   └─────────────────────────────┬───────────────────────────────────────┘  │
│                                  │                                         │
│                                  ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                        📋 SUGESTÃO FINAL                            │  │
│   │                                                                     │  │
│   │   • Mercado: Resultado Final (1X2)                                 │  │
│   │   • Previsão: Vitória Man Utd                                      │  │
│   │   • Confiança: 72%                                                 │  │
│   │   • Value Bet: +12%                                                │  │
│   │   • Recomendação: APOSTAR ✅                                       │  │
│   │                                                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Status Atual (POC)

### ✅ Implementado

```python
# Backend - prediction_controller.py (MOCKADO)

def _calculate_confidence(home_team, away_team, prediction):
    """Calcula confiança baseada em força dos times"""
    base_confidence = random.uniform(60, 80)
    
    # Ajusta baseado em força do time
    if home_team in G12_BRASILEIRAO and prediction == "HOME":
        base_confidence += random.uniform(5, 15)
    
    return min(base_confidence, 95)

def _calculate_value_bet(confidence, odd):
    """Calcula value bet %"""
    implied_prob = (1 / odd) * 100
    value_bet = ((confidence - implied_prob) / implied_prob) * 100
    return round(value_bet, 2)
```

**Status:** Cálculos mockados com valores realistas, mas sem modelos de IA reais.

---

## 🎲 Modelo Poisson (Planejado)

### Objetivo
Prever **quantidade de gols** e mercados relacionados (Over/Under, BTTS).

### Fundamento Matemático

O modelo de Poisson assume que gols em uma partida seguem uma distribuição de Poisson:

```
P(X = k) = (λ^k × e^(-λ)) / k!

Onde:
- X = número de gols
- k = quantidade específica de gols
- λ = taxa média de gols (calculada)
- e = número de Euler (≈ 2.71828)
```

### Cálculo de λ (Lambda)

```python
def calculate_lambda(team_attack, team_defense, opponent_attack, opponent_defense, league_avg_goals):
    """
    Calcula λ (taxa esperada de gols) para um time
    
    Args:
        team_attack: Força ofensiva do time (gols/jogo)
        team_defense: Força defensiva do time (gols sofridos/jogo)
        opponent_attack: Força ofensiva do oponente
        opponent_defense: Força defensiva do oponente
        league_avg_goals: Média de gols da liga
    
    Returns:
        lambda: Taxa esperada de gols
    """
    
    # Força de ataque relativa (normalizada pela média da liga)
    attack_strength = team_attack / league_avg_goals
    
    # Força de defesa relativa
    defense_weakness = opponent_defense / league_avg_goals
    
    # Lambda = ataque × defesa do oponente
    lambda_home = attack_strength * defense_weakness * league_avg_goals
    
    return lambda_home
```

### Exemplo de Cálculo

```python
# Dados da API-Football
flamengo_attack = 2.1  # Gols/jogo em casa
flamengo_defense = 0.8  # Gols sofridos/jogo

palmeiras_attack = 1.9
palmeiras_defense = 0.9

brasileirao_avg_goals = 2.5  # Média da liga

# Calcula lambda para cada time
lambda_flamengo = calculate_lambda(
    team_attack=flamengo_attack,
    team_defense=flamengo_defense,
    opponent_attack=palmeiras_attack,
    opponent_defense=palmeiras_defense,
    league_avg_goals=brasileirao_avg_goals
)
# lambda_flamengo ≈ 1.89

lambda_palmeiras = calculate_lambda(
    team_attack=palmeiras_attack,
    team_defense=palmeiras_defense,
    opponent_attack=flamengo_attack,
    opponent_defense=flamengo_defense,
    league_avg_goals=brasileirao_avg_goals
)
# lambda_palmeiras ≈ 1.52
```

### Previsão de Mercados

#### 1. Over/Under 2.5 Gols

```python
from scipy.stats import poisson

def predict_over_under_25(lambda_home, lambda_away):
    """Calcula probabilidade de Over/Under 2.5 gols"""
    
    prob_under_25 = 0
    
    # Soma probabilidades para 0-0, 1-0, 0-1, 1-1, 2-0, 0-2, 2-1, 1-2
    for home_goals in range(3):
        for away_goals in range(3):
            if home_goals + away_goals <= 2:
                prob_home = poisson.pmf(home_goals, lambda_home)
                prob_away = poisson.pmf(away_goals, lambda_away)
                prob_under_25 += prob_home * prob_away
    
    prob_over_25 = 1 - prob_under_25
    
    return {
        "over_25": prob_over_25,
        "under_25": prob_under_25
    }

# Exemplo
result = predict_over_under_25(lambda_flamengo, lambda_palmeiras)
# {
#   "over_25": 0.68,  # 68% de chance
#   "under_25": 0.32   # 32% de chance
# }
```

#### 2. BTTS (Both Teams To Score)

```python
def predict_btts(lambda_home, lambda_away):
    """Calcula probabilidade de ambos marcarem"""
    
    # P(ambos marcam) = 1 - P(casa 0 gols) - P(fora 0 gols) + P(ambos 0 gols)
    prob_home_zero = poisson.pmf(0, lambda_home)
    prob_away_zero = poisson.pmf(0, lambda_away)
    prob_both_zero = prob_home_zero * prob_away_zero
    
    prob_btts_yes = 1 - prob_home_zero - prob_away_zero + prob_both_zero
    prob_btts_no = 1 - prob_btts_yes
    
    return {
        "btts_yes": prob_btts_yes,
        "btts_no": prob_btts_no
    }

# Exemplo
result = predict_btts(lambda_flamengo, lambda_palmeiras)
# {
#   "btts_yes": 0.71,  # 71% de chance
#   "btts_no": 0.29    # 29% de chance
# }
```

### Features Necessárias

| Feature | Fonte | Descrição |
|---------|-------|-----------|
| `team_goals_scored_home` | API-Football | Gols marcados em casa |
| `team_goals_conceded_home` | API-Football | Gols sofridos em casa |
| `opponent_goals_scored_away` | API-Football | Gols do oponente fora |
| `opponent_goals_conceded_away` | API-Football | Gols sofridos fora |
| `league_avg_goals` | Calculado | Média da liga |
| `h2h_avg_goals` | API-Football | Média histórica H2H |

---

## 🤖 Modelo XGBoost (Planejado)

### Objetivo
Prever **resultado 1X2** (Vitória Casa, Empate, Vitória Fora) usando Machine Learning.

### Por que XGBoost?

| Vantagem | Descrição |
|----------|-----------|
| **Não-Linear** | Captura relações complexas entre features |
| **Ensemble** | Combina múltiplas árvores de decisão |
| **Robustez** | Lida bem com overfitting |
| **Interpretável** | Feature importance clara |
| **Performance** | Rápido para treinar e prever |

### Arquitetura

```python
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

class XGBoostPredictor:
    def __init__(self):
        self.model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softprob',  # 3 classes (HOME/DRAW/AWAY)
            num_class=3,
            eval_metric='mlogloss',
            random_state=42
        )
        self.scaler = StandardScaler()
    
    def train(self, X, y):
        """Treina o modelo"""
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
    
    def predict_proba(self, X):
        """Retorna probabilidades para cada classe"""
        X_scaled = self.scaler.transform(X)
        probas = self.model.predict_proba(X_scaled)
        
        return {
            "HOME": probas[0][0],
            "DRAW": probas[0][1],
            "AWAY": probas[0][2]
        }
```

### Features Engineering

#### Features Básicas (30+)

```python
def engineer_features(match_data, team_stats, opponent_stats, h2h_data):
    """Gera features para o modelo"""
    
    features = {}
    
    # === FEATURES DO TIME MANDANTE ===
    features['home_goals_scored_avg'] = team_stats['goals_scored_home'] / team_stats['games_home']
    features['home_goals_conceded_avg'] = team_stats['goals_conceded_home'] / team_stats['games_home']
    features['home_win_rate'] = team_stats['wins_home'] / team_stats['games_home']
    features['home_draw_rate'] = team_stats['draws_home'] / team_stats['games_home']
    features['home_loss_rate'] = team_stats['losses_home'] / team_stats['games_home']
    
    # Forma recente (últimos 5 jogos)
    features['home_points_last_5'] = calculate_points_last_n(team_stats['last_5_home'], 5)
    features['home_goals_last_5'] = sum(g['goals_scored'] for g in team_stats['last_5_home'])
    
    # === FEATURES DO TIME VISITANTE ===
    features['away_goals_scored_avg'] = opponent_stats['goals_scored_away'] / opponent_stats['games_away']
    features['away_goals_conceded_avg'] = opponent_stats['goals_conceded_away'] / opponent_stats['games_away']
    features['away_win_rate'] = opponent_stats['wins_away'] / opponent_stats['games_away']
    features['away_draw_rate'] = opponent_stats['draws_away'] / opponent_stats['games_away']
    features['away_loss_rate'] = opponent_stats['losses_away'] / opponent_stats['games_away']
    
    # === HISTÓRICO HEAD-TO-HEAD ===
    features['h2h_home_wins'] = h2h_data['home_wins'] / h2h_data['total_games']
    features['h2h_draws'] = h2h_data['draws'] / h2h_data['total_games']
    features['h2h_away_wins'] = h2h_data['away_wins'] / h2h_data['total_games']
    features['h2h_avg_goals'] = h2h_data['total_goals'] / h2h_data['total_games']
    
    # === FEATURES DE LIGA ===
    features['league_avg_goals'] = match_data['league_avg_goals']
    features['league_home_win_rate'] = match_data['league_home_win_rate']
    
    # === FEATURES DE ODDS (Sabedoria da Multidão) ===
    features['odd_home'] = match_data['odds']['home']
    features['odd_draw'] = match_data['odds']['draw']
    features['odd_away'] = match_data['odds']['away']
    features['odd_favorite'] = min(match_data['odds'].values())
    
    # === FEATURES DERIVADAS ===
    features['goal_diff_avg'] = features['home_goals_scored_avg'] - features['away_goals_conceded_avg']
    features['form_diff'] = features['home_points_last_5'] - features['away_points_last_5']
    features['strength_diff'] = (features['home_win_rate'] - features['away_loss_rate'])
    
    return features
```

#### Features Avançadas (Opcional)

```python
# Contexto temporal
features['days_since_last_game_home'] = ...
features['days_since_last_game_away'] = ...

# Rivalidade
features['is_derby'] = 1 if is_derby_match() else 0

# Pressão
features['home_position_table'] = ...
features['away_position_table'] = ...
features['position_diff'] = ...

# Momentum
features['home_streak'] = ...  # Sequência de vitórias/derrotas
features['away_streak'] = ...
```

### Pipeline de Treinamento

```python
def train_xgboost_model():
    """Pipeline completo de treinamento"""
    
    # 1. Carregar dados históricos
    df = load_historical_data('data/processed/training_dataset.parquet')
    
    # 2. Feature engineering
    X = df.drop(['result'], axis=1)  # Features
    y = df['result']  # Target (HOME=0, DRAW=1, AWAY=2)
    
    # 3. Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 4. Treinar modelo
    predictor = XGBoostPredictor()
    predictor.train(X_train, y_train)
    
    # 5. Avaliar
    y_pred = predictor.model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"Acurácia: {accuracy:.2%}")
    
    # 6. Salvar modelo
    predictor.model.save_model('data/models/xgboost_model.json')
    joblib.dump(predictor.scaler, 'data/models/scaler.pkl')
    
    return predictor
```

---

## 🔄 Ensemble (Combinação)

### Estratégia de Combinação

```python
def ensemble_prediction(poisson_probs, xgboost_probs, weights=(0.4, 0.6)):
    """
    Combina previsões dos dois modelos
    
    Args:
        poisson_probs: Probabilidades do Poisson
        xgboost_probs: Probabilidades do XGBoost
        weights: Pesos (poisson, xgboost)
    
    Returns:
        final_probs: Probabilidades finais combinadas
    """
    
    w_poisson, w_xgboost = weights
    
    final_probs = {
        "HOME": (w_poisson * poisson_probs["HOME"]) + (w_xgboost * xgboost_probs["HOME"]),
        "DRAW": (w_poisson * poisson_probs["DRAW"]) + (w_xgboost * xgboost_probs["DRAW"]),
        "AWAY": (w_poisson * poisson_probs["AWAY"]) + (w_xgboost * xgboost_probs["AWAY"])
    }
    
    return final_probs

# Exemplo
poisson_probs = {"HOME": 0.45, "DRAW": 0.30, "AWAY": 0.25}
xgboost_probs = {"HOME": 0.52, "DRAW": 0.28, "AWAY": 0.20}

final = ensemble_prediction(poisson_probs, xgboost_probs)
# {
#   "HOME": 0.492,  # 49.2%
#   "DRAW": 0.288,  # 28.8%
#   "AWAY": 0.220   # 22.0%
# }
```

### Ajuste de Pesos

```python
# Diferentes pesos para diferentes mercados
ENSEMBLE_WEIGHTS = {
    "1X2": (0.4, 0.6),      # XGBoost melhor para resultado
    "OVER_UNDER": (0.7, 0.3),  # Poisson melhor para gols
    "BTTS": (0.7, 0.3)      # Poisson melhor para gols
}
```

---

## 🎯 Estratégias de Apostas

### Implementação

```python
class BettingStrategy:
    """Aplica estratégia de apostas nas previsões"""
    
    @staticmethod
    def apply_strategy(predictions, strategy: str):
        """
        Filtra e ordena previsões baseado na estratégia
        
        Args:
            predictions: Lista de previsões
            strategy: "BALANCED" | "CONSERVATIVE" | "VALUE_BET" | "AGGRESSIVE"
        
        Returns:
            filtered_predictions: Previsões filtradas e ordenadas
        """
        
        if strategy == "BALANCED":
            # Confiança >= 65% E value_bet >= 5%
            filtered = [p for p in predictions 
                       if p['confidence'] >= 65 and p['value_bet_percentage'] >= 5]
            return sorted(filtered, key=lambda x: x['confidence'], reverse=True)
        
        elif strategy == "CONSERVATIVE":
            # Alta confiança (>= 75%)
            filtered = [p for p in predictions if p['confidence'] >= 75]
            return sorted(filtered, key=lambda x: x['confidence'], reverse=True)
        
        elif strategy == "VALUE_BET":
            # Value bet >= 10%
            filtered = [p for p in predictions if p['value_bet_percentage'] >= 10]
            return sorted(filtered, key=lambda x: x['value_bet_percentage'], reverse=True)
        
        elif strategy == "AGGRESSIVE":
            # Odds altas (>= 2.5)
            filtered = [p for p in predictions if p['odd'] >= 2.5]
            return sorted(filtered, key=lambda x: x['odd'], reverse=True)
        
        return predictions
```

---

## 💰 Value Bet Calculator

### Implementação

```python
def calculate_value_bet(model_probability, odd):
    """
    Calcula Value Bet %
    
    Value Bet indica se uma aposta tem valor esperado positivo.
    
    Fórmula:
    Value Bet % = ((Prob. Modelo - Prob. Odd) / Prob. Odd) × 100
    
    Args:
        model_probability: Probabilidade do modelo (0-100)
        odd: Odd da casa de apostas
    
    Returns:
        value_bet_percentage: % de value bet
        expected_value: Valor esperado da aposta
        is_value_bet: True se value_bet > 0
    """
    
    # Probabilidade implícita da odd
    implied_probability = (1 / odd) * 100
    
    # Value Bet %
    value_bet_percentage = ((model_probability - implied_probability) / implied_probability) * 100
    
    # Expected Value (EV)
    # EV = (Prob × Lucro) - (Prob_Perder × Stake)
    # Assumindo stake = 1
    profit = odd - 1  # Lucro se ganhar
    prob_win = model_probability / 100
    prob_lose = 1 - prob_win
    
    expected_value = (prob_win * profit) - (prob_lose * 1)
    
    return {
        "value_bet_percentage": round(value_bet_percentage, 2),
        "expected_value": round(expected_value, 4),
        "is_value_bet": value_bet_percentage > 0
    }

# Exemplo 1: Value Bet Positivo
result = calculate_value_bet(model_probability=72, odd=2.10)
# {
#   "value_bet_percentage": +51.16,  # Excelente value!
#   "expected_value": +0.224,        # EV positivo
#   "is_value_bet": True
# }

# Exemplo 2: Value Bet Negativo
result = calculate_value_bet(model_probability=45, odd=2.10)
# {
#   "value_bet_percentage": -5.32,   # Sem value
#   "expected_value": -0.055,        # EV negativo
#   "is_value_bet": False
# }
```

### Interpretação

| Value Bet % | Interpretação | Ação |
|-------------|---------------|------|
| **> +15%** | 🔥 Excelente value | Apostar com confiança |
| **+10% a +15%** | ✅ Bom value | Apostar |
| **+5% a +10%** | ⚖️ Value moderado | Considerar |
| **0% a +5%** | ⚠️ Value baixo | Evitar |
| **< 0%** | ❌ Sem value | Não apostar |

---

## 📚 Dados Históricos

### Fonte: Football-Data.co.uk

**URL:** https://www.football-data.co.uk/

#### CSVs Disponíveis

| Liga | Temporadas | Arquivo |
|------|------------|---------|
| Premier League | 1993-presente | `england/E0.csv` |
| Championship | 2005-presente | `england/E1.csv` |
| La Liga | 2000-presente | `spain/SP1.csv` |
| Serie A | 2000-presente | `italy/I1.csv` |
| Bundesliga | 2000-presente | `germany/D1.csv` |
| Ligue 1 | 2000-presente | `france/F1.csv` |
| Brasileirão | 2018-presente | `brazil/B1.csv` |

#### Campos Importantes

```csv
Date,HomeTeam,AwayTeam,FTHG,FTAG,FTR,HTHG,HTAG,HTR,HS,AS,HST,AST,HC,AC,HY,AY,HR,AR,B365H,B365D,B365A,...

Onde:
- FTHG/FTAG: Gols full time (casa/fora)
- FTR: Resultado (H=Home, D=Draw, A=Away)
- HS/AS: Chutes (casa/fora)
- HST/AST: Chutes ao gol
- HC/AC: Escanteios
- B365H/D/A: Odds Bet365
```

### Pipeline de Download

```python
import requests
import pandas as pd
from pathlib import Path

def download_historical_data(league='england', division='E0', seasons=5):
    """
    Baixa dados históricos do Football-Data.co.uk
    
    Args:
        league: País (england, spain, etc.)
        division: Divisão (E0=Premier, E1=Championship, etc.)
        seasons: Quantidade de temporadas
    """
    
    base_url = "https://www.football-data.co.uk/mmz4281"
    data_dir = Path("data/raw/football-data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    current_year = datetime.now().year
    
    for i in range(seasons):
        year_start = current_year - i - 1
        year_end = year_start + 1
        season_str = f"{str(year_start)[2:]}{str(year_end)[2:]}"  # Ex: "2223"
        
        url = f"{base_url}/{season_str}/{division}.csv"
        output_file = data_dir / f"{league}_{division}_{season_str}.csv"
        
        print(f"Baixando: {url}")
        
        try:
            df = pd.read_csv(url, encoding='latin1')
            df.to_csv(output_file, index=False)
            print(f"  ✅ Salvo: {output_file}")
        except Exception as e:
            print(f"  ❌ Erro: {e}")
```

---

## 🚀 Pipeline de Implementação

### Fase 1: Preparação de Dados

```bash
# 1. Baixar dados históricos
python scripts/download_historical_data.py

# 2. Limpar e processar
python scripts/prepare_dataset.py

# Output: data/processed/training_dataset.parquet
```

### Fase 2: Treinar Modelos

```bash
# 3. Treinar XGBoost
python scripts/train_xgboost.py

# Output: data/models/xgboost_model.json
#         data/models/scaler.pkl
#         data/models/model_metadata.json
```

### Fase 3: Integrar com Backend

```python
# web_api/infrastructure/external/analyzers/xgboost_analyzer_impl.py

class XGBoostAnalyzerImpl(AnalyzerContract):
    def __init__(self):
        self.model = xgb.Booster()
        self.model.load_model('data/models/xgboost_model.json')
        self.scaler = joblib.load('data/models/scaler.pkl')
    
    def analyze(self, match_data):
        """Analisa jogo e retorna previsões"""
        features = self.engineer_features(match_data)
        X = self.scaler.transform([features])
        probas = self.model.predict(xgb.DMatrix(X))
        
        return {
            "HOME": probas[0][0],
            "DRAW": probas[0][1],
            "AWAY": probas[0][2]
        }
```

### Fase 4: Atualização Contínua

```python
# Scheduler job que treina modelo periodicamente
# web_api/infrastructure/scheduler/jobs/model_retraining_job.py

@scheduler.scheduled_job('cron', day_of_week='mon', hour=2)
def retrain_models():
    """Re-treina modelos semanalmente"""
    
    # 1. Coleta dados novos da API-Football (última semana)
    new_data = collect_new_data()
    
    # 2. Adiciona ao dataset
    append_to_dataset(new_data)
    
    # 3. Re-treina modelo
    train_xgboost_model()
    
    # 4. Valida acurácia
    validate_model()
    
    # 5. Atualiza modelo em produção (se melhor)
    deploy_model()
```

---

## 📊 Métricas de Avaliação

### Modelo XGBoost (1X2)

| Métrica | Descrição | Target |
|---------|-----------|--------|
| **Accuracy** | % de acertos | >= 55% |
| **Log Loss** | Penaliza previsões incorretas | <= 1.0 |
| **Brier Score** | Calibração das probabilidades | <= 0.20 |
| **ROI** | Retorno sobre investimento | > 0% |

### Modelo Poisson (Over/Under, BTTS)

| Métrica | Descrição | Target |
|---------|-----------|--------|
| **Accuracy** | % de acertos | >= 60% |
| **RMSE** | Erro médio de gols | <= 1.2 |
| **Calibration** | Diferença prob. vs frequência | <= 5% |

---

## 🎉 Conclusão

### Status Atual
⏳ **Modelos de IA não implementados ainda**  
✅ **Estrutura de previsões mockada e funcionando**  
✅ **Sistema pronto para integração dos modelos**  

### Próximos Passos
1. ✅ Download de dados históricos
2. ⏳ Feature engineering
3. ⏳ Treinar modelo XGBoost
4. ⏳ Implementar modelo Poisson
5. ⏳ Integrar com backend
6. ⏳ Validar acurácia
7. ⏳ Deploy em produção

**Previsão de implementação:** 2-3 semanas 🚀

