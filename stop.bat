@echo off
echo Zastavuji aplikaci European Transport CZ...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *complete_app*" >nul 2>&1
if %errorlevel% equ 0 (
    echo Aplikace byla zastavena.
) else (
    echo Aplikace nebezi nebo uz byla zastavena.
)
timeout /t 2 /nobreak >nul
