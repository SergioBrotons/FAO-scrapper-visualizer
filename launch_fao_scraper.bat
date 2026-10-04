@echo off
title Cytria FAO Scraper Launcher
cd /d "%~dp0"
echo ========================================================
echo        CYTRIA - GENEVA FAO SCRAPER ^& PIPELINE
echo ========================================================
echo.
set PYTHONPATH=
set PYTHONNOUSERSITE=1

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment .venv not found.
    pause
    exit /b 1
)

echo Starting FAO transaction scraper (Google Chrome session)...
".venv\Scripts\python.exe" -m fao_transactions collect-transactions --headed %*

echo.
echo Process finished.
pause
