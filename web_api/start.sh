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

# Verifica se a pasta data/ e os bancos existem
NEED_RECREATE=0

if [ ! -d "data" ]; then
    echo "[WARN] Pasta data/ nao encontrada!"
    NEED_RECREATE=1
fi

if [ -d "data" ]; then
    if [ ! -f "data/cache.db" ]; then
        echo "[WARN] Banco cache.db nao encontrado!"
        NEED_RECREATE=1
    fi

    if [ ! -f "data/tickets.db" ]; then
        echo "[WARN] Banco tickets.db nao encontrado!"
        NEED_RECREATE=1
    fi
fi

# Se precisar recriar, remove o venv antigo
if [ $NEED_RECREATE -eq 1 ]; then
    echo "[INFO] Estrutura de dados inconsistente. Recriando ambiente..."

    if [ -d ".venv" ]; then
        echo "[INFO] Removendo ambiente virtual antigo..."
        rm -rf .venv
    fi

    if [ -d "data" ]; then
        echo "[INFO] Limpando pasta data/..."
        rm -rf data
    fi
fi

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
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
