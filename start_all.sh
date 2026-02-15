#!/bin/bash
# Betting Advisor - Start All

clear

echo "========================================"
echo "   Betting Advisor - Iniciando..."
echo "========================================"
echo ""
echo "[INFO] Backend: http://localhost:8000"
echo "[INFO] Frontend: http://localhost:5173"
echo "[INFO] Docs API: http://localhost:8000/docs"
echo ""

# Iniciar backend em background
cd "$(dirname "$0")/web_api"
./start.sh &
BACKEND_PID=$!
echo "[INFO] Backend iniciado (PID: $BACKEND_PID)"
echo ""
echo "[INFO] Aguardando backend inicializar..."

# Aguardar backend estar pronto (verificar porta 8000)
MAX_TRIES=30
TRIES=0
while [ $TRIES -lt $MAX_TRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "[INFO] Backend pronto!"
        break
    fi
    echo "[INFO] Backend ainda nao esta pronto, aguardando..."
    sleep 2
    TRIES=$((TRIES+1))
done

if [ $TRIES -eq $MAX_TRIES ]; then
    echo "[ERRO] Backend nao iniciou em tempo habil"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""

# Iniciar frontend em background
cd "$(dirname "$0")/web_app"
./start.sh &
FRONTEND_PID=$!
echo "[INFO] Frontend iniciado (PID: $FRONTEND_PID)"

echo ""
echo "========================================"
echo "   Sistema rodando!"
echo "========================================"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

# Trap para matar processos ao sair
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Aguardar
wait

