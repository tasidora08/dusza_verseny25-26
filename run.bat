@echo off
cd /d "%~dp0"
if "%1"=="--ui" (
    python main.py --ui
) else (
    python main.py
)