@echo off
REM Rychly restart aplikace - ukončí běžící instanci a spustí novou

echo Zastavuji bezici aplikaci...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *complete_app*" >nul 2>&1

timeout /t 2 /nobreak >nul

echo Spoustim aplikaci...
start "European Transport CZ" cmd /k "cd /d %~dp0 && python complete_app.py"

echo.
echo Aplikace spustena v novem okne!
echo URL: http://127.0.0.1:5004
echo.
