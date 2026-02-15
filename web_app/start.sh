#!/bin/bash
echo "========================================"
echo "   Betting Advisor - Frontend React"
echo "========================================"
echo ""

cd "$(dirname "$0")"

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "[ERRO] Node.js nao encontrado!"
    echo "       Instale de https://nodejs.org"
    exit 1
fi

echo "[INFO] Node.js encontrado:"
node --version

# Verifica se node_modules existe
if [ ! -d "node_modules" ]; then
    echo ""
    echo "[INFO] Instalando dependencias..."
    npm install
fi

echo ""
echo "========================================"
echo "   Iniciando Frontend (React + Vite)"
echo "========================================"
echo ""
echo "   App:    http://localhost:5173"
echo ""

npm run dev

