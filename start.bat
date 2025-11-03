@echo off
REM Quick Start Script for Trading Analytics Platform
REM Windows PowerShell version

echo ========================================
echo   Trading Analytics Platform
echo   Quick Start Script
echo ========================================
echo.

REM Check Python installation
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9 or higher
    pause
    exit /b 1
)

echo [1/4] Checking Python version...
py --version

echo.
echo [2/4] Installing dependencies...
echo This may take a few minutes. Please be patient...
echo.
py -m pip install --default-timeout=100 --retries 5 -r requirements.txt
if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies failed to install.
    echo This might be due to network issues or packages already installed.
    echo.
    echo Attempting to continue with existing packages...
    echo If the application fails to start, please run: py -m pip install -r requirements.txt
    echo.
    timeout /t 3 /nobreak >nul
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

py -m streamlit run frontend.py

pause
