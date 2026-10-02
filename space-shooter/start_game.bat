@echo off
title Cosmic Vanguard - 2D Space Shooter
cd /d "%~dp0"
echo ==============================================
echo   Launching Cosmic Vanguard - Space Shooter
echo ==============================================

py -3.12 main.py
if %ERRORLEVEL% NEQ 0 (
    echo Trying fallback python command...
    python main.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Game closed with an error.
    pause
)
