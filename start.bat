@echo off
echo ========================================
echo    HERANCA TATICA - Iniciando...
echo ========================================
echo.

cd /d "%~dp0"

echo [1/2] Iniciando Backend (porta 8080)...
start "Backend" cmd /k "cd backend && python run_server.py"

timeout /t 2 /nobreak >nul

echo [2/2] Iniciando Frontend (porta 3000)...
start "Frontend" cmd /k "cd frontend && npm run dev -- --port 3000"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    Servidores iniciados!
echo ========================================
echo.
echo    Frontend: http://localhost:3000
echo    Backend:  http://localhost:8080
echo.
echo    Abrindo navegador...
start http://localhost:3000

echo.
echo    Para parar: feche as janelas do terminal
echo ========================================
