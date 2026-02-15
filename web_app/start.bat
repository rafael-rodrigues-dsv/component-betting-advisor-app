@echo off
chcp 65001 >nul
echo ========================================
echo    Betting Advisor - Frontend React
echo ========================================
echo.

cd /d "%~dp0"

REM Verifica se Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Node.js nao encontrado!
    echo        Instale de https://nodejs.org
    pause
    exit /b 1
)

echo [INFO] Node.js encontrado:
node --version

REM Verifica se node_modules existe
if not exist "node_modules" (
    echo.
    echo [INFO] Instalando dependencias...
    call npm install
    if errorlevel 1 (
        echo [ERRO] Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo    Iniciando Frontend (React + Vite)
echo ========================================
echo.
echo    App:    http://localhost:5173
echo.

npm run dev

