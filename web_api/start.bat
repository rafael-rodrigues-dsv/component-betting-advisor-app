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
python main.py
