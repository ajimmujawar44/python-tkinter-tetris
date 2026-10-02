@echo off
title Cosmic Vanguard - Pygame Edition
cd /d "%~dp0"
echo Launching Pygame Space Shooter...
py -3.12 main_pygame.py
if %ERRORLEVEL% NEQ 0 (
    python main_pygame.py
)
pause
