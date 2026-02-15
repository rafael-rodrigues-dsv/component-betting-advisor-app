@echo off
chcp 65001 > nul
cls

echo ========================================
echo    Betting Advisor - Iniciando...
echo ========================================
echo.
echo [INFO] Backend: http://localhost:8000
echo [INFO] Frontend: http://localhost:5173
echo [INFO] Docs API: http://localhost:8000/docs
echo.

REM Iniciar backend
cd /d "%~dp0web_api"
start "Backend - API" cmd /k "start.bat"

echo.
echo [INFO] Aguardando backend inicializar...

REM Aguardar backend estar pronto (verificar porta 8000)
:wait_backend
timeout /t 2 /nobreak > nul
curl -s http://localhost:8000/health > nul 2>&1
if errorlevel 1 (
    echo [INFO] Backend ainda nao esta pronto, aguardando...
    goto wait_backend
)

echo [INFO] Backend pronto!
echo.

REM Iniciar frontend
cd /d "%~dp0web_app"
start "Frontend - React" cmd /k "start.bat"

timeout /t 5 /nobreak > nul
start http://localhost:5173

echo.
echo Sistema iniciado!
echo Pressione qualquer tecla para sair...
pause > nul

