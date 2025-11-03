@echo off
REM Quick Start Script for Trading Analytics Platform
REM Windows PowerShell version

echo ========================================
echo   Trading Analytics Platform
echo   Quick Start Script
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
python --version

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Creating data directories...
if not exist "data" mkdir data
if not exist "data\exports" mkdir data\exports
echo Data directories created.

echo.
echo [4/4] Starting application...
echo.
echo ========================================
echo   Dashboard will open in your browser
echo   Press Ctrl+C to stop the application
echo ========================================
echo.

streamlit run frontend.py

pause
