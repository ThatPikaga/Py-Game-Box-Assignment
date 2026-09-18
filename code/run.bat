@echo off
REM PyCade Arcade - Windows Launcher
REM Run this batch file to start the PyCade arcade system

cd /d "%~dp0"
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Error: Failed to launch PyCade. Make sure Python and pygame are installed.
    echo Run: pip install -r requirements.txt
    pause
)
