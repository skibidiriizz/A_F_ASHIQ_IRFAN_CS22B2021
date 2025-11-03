@echo off
REM Dependency Installation Script for Trading Analytics Platform
REM Run this separately if start.bat fails to install dependencies

echo ========================================
echo   Dependency Installation
echo   Trading Analytics Platform
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

echo [1/3] Checking Python version...
py --version
echo.

echo [2/3] Upgrading pip...
py -m pip install --upgrade pip
echo.

echo [3/3] Installing dependencies with extended timeout...
echo This may take several minutes depending on your internet connection.
echo Please be patient and do not close this window.
echo.

REM Install with increased timeout and retries
py -m pip install --default-timeout=100 --retries 5 -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Installation encountered errors!
    echo ========================================
    echo.
    echo This is likely due to network timeout issues.
    echo.
    echo SOLUTIONS:
    echo 1. Check your internet connection
    echo 2. Try running this script again
    echo 3. Install packages individually: py -m pip install streamlit pandas plotly
    echo 4. Use a VPN if you're experiencing network restrictions
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo All dependencies have been installed successfully.
echo You can now run the application using: .\start.bat
echo.
pause
