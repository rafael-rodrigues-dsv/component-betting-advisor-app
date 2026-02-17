@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
echo ========================================
echo    Betting Advisor - Backend API
echo ========================================
echo.

cd /d "%~dp0"

REM Define o diretório do projeto
set WEB_API_ROOT=%~dp0


REM Tenta py launcher
py --version >nul 2>&1
if !errorlevel!==0 (
    set PYTHON_CMD=py
    echo [INFO] Python encontrado: py
    py --version
    goto :create_venv
)

echo [ERRO] Python nao encontrado!
echo        Instale de https://python.org
pause
exit /b 1

:create_venv
REM Verifica se a pasta data/ existe
set NEED_RECREATE=0
if not exist "data\" (
    echo [WARN] Pasta data/ nao encontrada!
    set NEED_RECREATE=1
)

REM Verifica se os bancos de dados existem
if not exist "data\cache.db" (
    if exist "data\" (
        echo [WARN] Banco cache.db nao encontrado!
        set NEED_RECREATE=1
    )
)

if not exist "data\tickets.db" (
    if exist "data\" (
        echo [WARN] Banco tickets.db nao encontrado!
        set NEED_RECREATE=1
    )
)

REM Se precisar recriar, remove o venv antigo
if !NEED_RECREATE!==1 (
    echo [INFO] Estrutura de dados inconsistente. Recriando ambiente...
    if exist ".venv\" (
        echo [INFO] Removendo ambiente virtual antigo...
        rmdir /s /q .venv
    )
    if exist "data\" (
        echo [INFO] Limpando pasta data/...
        rmdir /s /q data
    )
)

REM Verifica se o venv existe
if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo [INFO] Criando ambiente virtual...
    %PYTHON_CMD% -m venv .venv
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )

    echo [INFO] Instalando dependencias Python...
    call .venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao instalar dependencias!
        pause
        exit /b 1
    )
) else (
    echo [INFO] Ambiente virtual ja existe.
    call .venv\Scripts\activate.bat
)

echo.
echo ========================================
echo    Iniciando Backend (FastAPI)
echo ========================================
echo.
echo    API:    http://localhost:8000
echo    Docs:   http://localhost:8000/docs
echo.

cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
