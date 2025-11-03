# Trading Analytics Platform - Setup Guide

## 📋 Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Methods](#installation-methods)
3. [Troubleshooting](#troubleshooting)
4. [Running the Application](#running-the-application)
5. [Verification](#verification)

## 🖥️ System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: Version 3.9 or higher (3.11+ recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB for installation + data storage
- **Internet**: Stable connection for real-time data streaming

### Optional Components
- **Redis Server**: For enhanced performance (can run without it)
- **Docker**: If you prefer containerized Redis

## 📦 Installation Methods

### Method 1: Automated Installation (Windows - Recommended)

This is the **easiest and fastest** method for Windows users:

1. **Open the project folder**
2. **Double-click `start.bat`**
3. **Wait for installation** (may take 3-10 minutes depending on internet speed)
4. **Dashboard opens automatically** in your browser

**What it does**:
- ✅ Checks Python installation
- ✅ Installs all dependencies with retry logic
- ✅ Creates necessary directories
- ✅ Launches the application

### Method 2: Manual Installation (All Platforms)

#### Step 1: Open Terminal/Command Prompt
```bash
# Windows
Win + R, type "cmd", press Enter

# Linux/Mac
Open Terminal application
```

#### Step 2: Navigate to Project Directory
```bash
cd path/to/gemscap
# Example: cd C:\Users\YourName\Desktop\gemscap
```

#### Step 3: Verify Python Installation
```bash
# Windows
py --version

# Linux/Mac
python3 --version

# Expected output: Python 3.9.x or higher
```

#### Step 4: Install Dependencies

**Standard Installation**:
```bash
# Windows
py -m pip install -r requirements.txt

# Linux/Mac
python3 -m pip install -r requirements.txt
```

**If you encounter network timeouts** (recommended):
```bash
# Windows
py -m pip install --default-timeout=100 --retries 5 -r requirements.txt

# Linux/Mac
python3 -m pip install --default-timeout=100 --retries 5 -r requirements.txt
```

**Alternative: Install Core Packages First**:
```bash
# Install essential packages one by one
pip install streamlit==1.29.0
pip install pandas==2.1.3
pip install plotly==5.18.0
pip install websockets==12.0
pip install scipy==1.11.4
pip install statsmodels==0.14.0
pip install scikit-learn==1.3.2

# Then install remaining dependencies
pip install -r requirements.txt
```

### Method 3: Separate Dependency Installation (Windows)

If `start.bat` fails due to network issues:

1. **Run `install_dependencies.bat`**
   - This script has extended timeout and retry logic
   - It will attempt installation multiple times
   - Shows helpful error messages

2. **After successful installation, run `start.bat`**

## 🔧 Troubleshooting

### Problem 1: "pip: command not found" or "Python not in PATH"

**Solution**:
```bash
# Option A: Use full Python path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt

# Option B: Add Python to PATH
1. Search "Environment Variables" in Windows
2. Edit "Path" variable
3. Add Python installation directory
4. Restart command prompt
```

### Problem 2: Network Timeout During Installation

**Error Message**: `ReadTimeoutError: HTTPSConnectionPool... Read timed out`

**Solutions**:
1. **Increase timeout and retries**:
   ```bash
   py -m pip install --default-timeout=200 --retries 10 -r requirements.txt
   ```

2. **Use a different PyPI mirror**:
   ```bash
   py -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```

3. **Install packages individually**:
   ```bash
   # Install only the essential packages
   py -m pip install streamlit pandas plotly websockets
   ```

4. **Check internet connection**:
   - Ensure stable network
   - Try using VPN if restricted
   - Disable firewall/antivirus temporarily

### Problem 3: Permission Errors

**Error Message**: `PermissionError: [WinError 5] Access is denied`

**Solutions**:
```bash
# Install for current user only
py -m pip install --user -r requirements.txt

# Or run Command Prompt as Administrator
Right-click Command Prompt → "Run as Administrator"
```

### Problem 4: SSL Certificate Errors

**Error Message**: `SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Solutions**:
```bash
# Disable SSL verification (not recommended for production)
py -m pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Or update certificates
py -m pip install --upgrade certifi
```

### Problem 5: Redis Connection Warning

**Warning Message**: `Redis not available... Using SQLite only`

**This is NOT an error!** The application works perfectly without Redis.

**Optional: Install Redis for better performance**:
- **Windows**: Download from https://github.com/tporadowski/redis/releases
- **Linux**: `sudo apt-get install redis-server`
- **macOS**: `brew install redis`
- **Docker**: `docker run -d -p 6379:6379 redis:latest`

### Problem 6: Module Not Found Errors

**Error Message**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Verify pip is installing to correct Python environment
py -m pip list

# If packages are installed but not found, check Python path
py -c "import sys; print(sys.executable)"

# Reinstall specific missing package
py -m pip install --force-reinstall streamlit
```

## 🚀 Running the Application

### After Successful Installation

**Windows**:
```bash
# Method 1: Use start script
.\start.bat

# Method 2: Direct Streamlit command
py -m streamlit run frontend.py

# Method 3: Python module
py frontend.py  # If streamlit is in PATH
```

**Linux/Mac**:
```bash
# Method 1: Use start script
./start.sh

# Method 2: Direct Streamlit command
python3 -m streamlit run frontend.py

# Method 3: If streamlit is in PATH
streamlit run frontend.py
```

### Expected Output

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://172.x.x.x:8501

INFO:backend.storage:SQLite database initialized at data/ticks.db
INFO:app:Trading Analytics App initialized with symbols: ['BTCUSDT', 'ETHUSDT']
INFO:backend.data_ingestion:Connected to btcusdt stream
INFO:backend.data_ingestion:Connected to ethusdt stream
```

**Note**: If you see `WARNING:backend.storage:Redis not available`, this is fine! The app works without Redis.

## ✅ Verification

### Step 1: Check Dashboard Opens
- Browser should automatically open to `http://localhost:8501`
- You should see the "Trading Analytics Platform" interface

### Step 2: Verify Data Ingestion
1. In the sidebar, enter symbols: `BTCUSDT,ETHUSDT`
2. Click "▶️ Start Ingestion"
3. Wait 30-60 seconds
4. Look for messages in terminal: "Connected to btcusdt stream"

### Step 3: Verify Charts Display
1. Go to "📈 Market Overview" tab
2. Select a symbol from dropdown
3. Select timeframe (1m or 5m recommended)
4. Candlestick chart should display after data collection

### Step 4: Test Analytics
1. Navigate to "🔬 Pair Analytics" tab
2. Select pair (e.g., "BTCUSDT vs ETHUSDT")
3. Click "🔄 Compute Analytics"
4. Regression results and charts should appear

### Step 5: Verify Demo Mode
```bash
# Run demo test to verify all components
py demo.py --test

# Expected output: "All demo tests passed! ✓"
```

## 📞 Support Information

### If Everything Fails

**Create a minimal environment**:
```bash
# Create virtual environment
py -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install fresh
pip install streamlit pandas plotly websockets scipy statsmodels scikit-learn pykalman

# Run application
streamlit run frontend.py
```

### Logs and Diagnostics

**Check Python environment**:
```bash
py --version
py -m pip --version
py -m pip list
```

**Test network connectivity**:
```bash
# Test PyPI connection
py -m pip install --dry-run streamlit
```

**Generate diagnostic report**:
```bash
# Save full error log
py -m pip install -r requirements.txt > install_log.txt 2>&1
```

## 🎯 Production Deployment Notes

For company deployment:

1. **Pre-installed Packages**: Consider creating a virtual environment with all packages pre-installed
2. **Offline Installation**: Download all `.whl` files and install offline
3. **Docker Container**: Build Docker image with all dependencies
4. **Requirements Freeze**: Use `pip freeze > requirements_locked.txt` for exact versions
5. **Network Configuration**: Configure corporate proxy in pip settings

### Creating Offline Installation Package

```bash
# Download all packages
py -m pip download -r requirements.txt -d packages/

# On target machine, install from local packages
py -m pip install --no-index --find-links=packages/ -r requirements.txt
```

## 📄 License and Contact

This is a demonstration project for quantitative trading analytics.

**Author**: Developed as part of Quant Developer Evaluation Assignment  
**Python Version**: 3.9+  
**Last Updated**: November 2025
