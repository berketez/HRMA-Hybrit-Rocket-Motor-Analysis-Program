@echo off
title HRMA - Hybrid Rocket Motor Analysis
color 0A

echo ========================================
echo   HRMA - Starting Application
echo ========================================
echo.

REM Set UTF-8 encoding
chcp 65001 > nul

REM Set Python environment
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set FLASK_ENV=production
set FLASK_APP=app.py

REM Check Python installation
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Navigate to application directory
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using global Python
)

REM Install/upgrade dependencies if needed
echo Checking dependencies...
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt

REM Clear any temp files
if exist "__pycache__" rd /s /q "__pycache__"
if exist "*.pyc" del /f /q "*.pyc"

REM Start the application
echo.
echo Starting HRMA application...
echo Navigate to http://localhost:5000 in your browser
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
