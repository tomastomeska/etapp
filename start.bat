@echo off
echo ============================================================
echo    European Transport CZ - Spousteci skript
echo ============================================================
echo.

cd /d "%~dp0"

echo Kontrola Python instalace...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [CHYBA] Python neni nainstalovan nebo neni v PATH!
    pause
    exit /b 1
)

echo.
echo Spoustim aplikaci...
echo.
python complete_app.py

if %errorlevel% neq 0 (
    echo.
    echo [CHYBA] Aplikace skoncila s chybou!
    pause
)
