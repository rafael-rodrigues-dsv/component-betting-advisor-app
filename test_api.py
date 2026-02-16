import requests
import json

try:
    response = requests.get("http://localhost:8000/api/v1/matches")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Success: {data.get('success')}")
    print(f"Date: {data.get('date')}")
    print(f"Count: {data.get('count')}")
    print(f"\nPrimeiro jogo:")
    if data.get('matches'):
        print(json.dumps(data['matches'][0], indent=2))
except Exception as e:
    print(f"Erro: {e}")

