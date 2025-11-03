#!/bin/bash
# Quick Start Script for Trading Analytics Platform
# Linux/Mac version

echo "========================================"
echo "  Trading Analytics Platform"
echo "  Quick Start Script"
echo "========================================"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "[1/4] Checking Python version..."
python3 --version

echo
echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt || {
    echo "ERROR: Failed to install dependencies"
    exit 1
}

echo
echo "[3/4] Creating data directories..."
mkdir -p data/exports
echo "Data directories created."

echo
echo "[4/4] Starting application..."
echo
echo "========================================"
echo "  Dashboard will open in your browser"
echo "  Press Ctrl+C to stop the application"
echo "========================================"
echo

streamlit run frontend.py
