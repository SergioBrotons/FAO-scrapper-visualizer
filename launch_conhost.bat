@echo off
:: Forces classic Windows console host to avoid Windows Terminal ConPTY error 0x800700e8
if "%1"=="CONHOST" goto :RUN
start conhost.exe "%~f0" CONHOST
exit /b

:RUN
title Cytria FAO Scraper Launcher (Chrome)
cd /d "%~dp0"
echo ========================================================
echo     CYTRIA - GENEVA FAO SCRAPER & PIPELINE (CHROME)
echo ========================================================
echo.
set PYTHONPATH=
set PYTHONNOUSERSITE=1

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found.
    pause
    exit /b 1
)

echo Starting FAO transaction scraper with Google Chrome...
".venv\Scripts\python.exe" -m fao_transactions collect-transactions --headed

echo.
echo Process finished.
pause
