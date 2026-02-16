#!/bin/bash

echo "========================================"
echo "   Betting Advisor - Backend API"
echo "========================================"
echo ""

cd "$(dirname "$0")"


# Procura Python
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "[ERRO] Python nao encontrado!"
    exit 1
fi

echo "[INFO] Python encontrado: $PYTHON_CMD"
$PYTHON_CMD --version

# Verifica se o venv existe
if [ ! -f ".venv/bin/activate" ]; then
    echo ""
    echo "[INFO] Criando ambiente virtual..."
    $PYTHON_CMD -m venv .venv

    echo "[INFO] Instalando dependencias Python..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "[INFO] Ambiente virtual ja existe."
    source .venv/bin/activate
fi

echo ""
echo "========================================"
echo "   Iniciando Backend (FastAPI)"
echo "========================================"
echo ""
echo "   API:    http://localhost:8000"
echo "   Docs:   http://localhost:8000/docs"
echo ""

cd src
python main.py
