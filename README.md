# Trading Analytics Platform

A comprehensive real-time trading analytics dashboard for statistical arbitrage and quantitative analysis. Built for high-frequency trading firms to analyze market data, compute hedge ratios, monitor spreads, and backtest mean-reversion strategies.

![Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

### Core Functionality
- **Real-Time Data Ingestion**: WebSocket connection to Binance Futures for live tick data
- **Multi-Timeframe Analysis**: Resample tick data to 1s, 1m, 5m, and custom intervals
- **Advanced Analytics**:
  - OLS and Robust Regression (Huber) for hedge ratio estimation
  - Kalman Filter for dynamic hedge ratio tracking
  - Spread computation and z-score analysis
  - Augmented Dickey-Fuller (ADF) test for stationarity
  - Rolling correlation and half-life calculation
  - VWAP and liquidity metrics
- **Interactive Visualizations**: Real-time charts with zoom, pan, and hover capabilities
- **Alert System**: Configurable rule-based alerts (z-score, price, spread, volume)
- **Backtesting**: Mean-reversion strategy simulator with performance metrics
- **Data Export**: CSV export for tick data and analytics results

### Advanced Features
- **Dynamic Hedge Estimation**: Kalman Filter for time-varying hedge ratios
- **Robust Regression**: Huber and Theil-Sen for outlier-resistant analysis
- **Mini Backtest**: Z-score based entry/exit with PnL tracking
- **Liquidity Filters**: Volume analysis and spike detection
- **Cross-Correlation Heatmaps**: Multi-pair correlation analysis
- **OHLC Upload**: Support for historical data import

## 🏗️ Architecture

### Design Philosophy
The system is built with **modularity**, **scalability**, and **extensibility** as core principles:

1. **Loose Coupling**: Each component (ingestion, storage, analytics, alerts) operates independently through clean interfaces
2. **Pluggable Components**: Easy to swap data sources (Binance → CME, REST APIs, CSV)
3. **Separation of Concerns**: Backend services are decoupled from frontend visualization
4. **Extensible Analytics**: New indicators and strategies can be added without touching core logic

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Streamlit)                    │
│  - Interactive Dashboard                                    │
│  - Real-time Charts (Plotly)                               │
│  - User Controls & Alerts                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Orchestrator (app.py)              │
│  - Coordinates all services                                 │
│  - Provides clean API to frontend                          │
└──┬────────┬──────────┬──────────┬──────────┬───────────────┘
   │        │          │          │          │
   ▼        ▼          ▼          ▼          ▼
┌──────┐ ┌─────┐ ┌─────────┐ ┌────────┐ ┌─────────┐
│Ingest│ │Store│ │Resample │ │Analyze │ │ Alerts  │
│      │ │     │ │         │ │        │ │         │
│WS    │ │SQLite│ │OHLCV    │ │OLS/KF  │ │Rules    │
│Client│ │Redis │ │Engine   │ │Stats   │ │Manager  │
└──────┘ └─────┘ └─────────┘ └────────┘ └─────────┘
```

### Data Flow

1. **Ingestion**: WebSocket client connects to Binance, receives tick data
2. **Storage**: Ticks stored in SQLite (durable) and Redis (fast cache)
3. **Resampling**: Background threads convert ticks to OHLCV bars
4. **Analytics**: Compute regressions, spreads, z-scores on demand
5. **Visualization**: Frontend queries analytics and renders charts
6. **Alerts**: Rule engine monitors analytics and triggers notifications

### Storage Strategy

**Hybrid Approach** for performance and durability:
- **SQLite**: Primary storage for all historical tick data
  - Indexed by symbol and timestamp
  - Supports complex queries and exports
  - Persistent across restarts
  
- **Redis** (Optional): In-memory cache for hot data
  - Recent ticks (last 10,000 per symbol)
  - Resampled OHLCV with 5-minute TTL
  - Falls back to SQLite if unavailable

This design allows:
- Fast real-time queries (Redis)
- Reliable historical analysis (SQLite)
- Easy migration to TimescaleDB/InfluxDB for production scale

## 🚀 Quick Start

### Prerequisites
- **Python 3.9 or higher** (Python 3.11+ recommended)
- **Internet connection** for real-time data
- **Redis server** (optional but recommended for better performance)

### Installation

#### Option 1: Quick Start (Windows - Recommended)

1. **Download/Clone the project**
2. **Double-click `start.bat`** - This will:
   - Check Python installation
   - Install all dependencies automatically
   - Start the dashboard

#### Option 2: Manual Installation (All Platforms)

1. **Navigate to project directory**:
```bash
cd gemscap
```

2. **Install dependencies**:
```bash
# If you encounter timeout errors, use:
python -m pip install --default-timeout=100 --retries 5 -r requirements.txt

# Or install core packages first:
pip install streamlit pandas plotly websockets scipy statsmodels scikit-learn
```

**Troubleshooting Installation Issues**:
- **Network Timeout**: Run `install_dependencies.bat` (Windows) for extended timeout
- **Permission Errors**: Use `python -m pip install --user -r requirements.txt`
- **Proxy Issues**: Configure pip with `pip config set global.proxy http://your-proxy:port`

3. **Start Redis** (optional, recommended):
```bash
# Windows (with Redis installed)
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:latest

# Note: The application works fine without Redis (uses SQLite only)
```

### Running the Application

**Windows**:
```bash
.\start.bat
# Or
py -m streamlit run frontend.py
```

**Linux/Mac**:
```bash
./start.sh
# Or
python -m streamlit run frontend.py
```

The dashboard will automatically open in your browser at `http://localhost:8501`

### First-Time Usage

1. **Start Data Ingestion**:
   - Enter symbols (e.g., `BTCUSDT,ETHUSDT`) in the sidebar
   - Click "▶️ Start" button
   - Wait 30-60 seconds for sufficient data collection

2. **View Analytics**:
   - Navigate to "🔬 Pair Analytics" tab
   - Select trading pair and timeframe
   - Charts will update automatically

3. **Configure Alerts**:
   - Expand "Alert Configuration" in sidebar
   - Choose alert type and parameters
   - System will notify when conditions are met

4. **Run Backtest**:
   - Go to "🎯 Backtest" tab
   - Adjust entry/exit thresholds
   - Click "🚀 Run Backtest"

## 📊 Analytics Methodology

### Hedge Ratio Estimation

**OLS Regression** (Default):
```
Y = α + β·X + ε
```
Where:
- Y = Price of Symbol 1 (e.g., ETH)
- X = Price of Symbol 2 (e.g., BTC)
- β = Hedge ratio (how much of X to hedge Y)

**Kalman Filter** (Advanced):
- Dynamic hedge ratio that adapts to market conditions
- Better for non-stationary relationships
- Uses state-space model for online estimation

### Spread Construction

```
Spread = Price₁ - β × Price₂
```

For pairs trading:
- Enter when |z-score| > 2 (spread deviates from mean)
- Exit when z-score reverts to 0 (spread returns to mean)

### Z-Score Calculation

```
Z = (Spread - μ) / σ
```

Where:
- μ = Rolling mean of spread (default: 20 periods)
- σ = Rolling standard deviation

### Stationarity Test

**ADF (Augmented Dickey-Fuller) Test**:
- H₀: Series has unit root (non-stationary)
- H₁: Series is stationary
- p-value < 0.05 → Reject H₀ → Spread is mean-reverting

### Half-Life

Measures how quickly spread reverts to mean:
```
Half-Life = -log(2) / λ
```

Where λ is the mean-reversion speed from AR(1) model.

## 🎨 Dashboard Overview

### Tab 1: Overview
- Real-time price metrics for all symbols
- Candlestick charts with OHLCV data
- Volume analysis

### Tab 2: Pair Analytics
- Price comparison (dual-axis)
- Spread visualization
- Z-score with entry/exit thresholds
- Rolling correlation
- Statistical tests (ADF, half-life)
- Kalman filter hedge ratio evolution

### Tab 3: Backtest
- Mean-reversion strategy simulator
- Performance metrics (Win rate, Sharpe, PnL)
- Trade history table
- Equity curve

### Tab 4: Alerts
- Recent triggered alerts
- Active rule management
- Custom alert creation

### Tab 5: Data Export
- Tick data export to CSV
- Analytics snapshot export
- Historical data range selection

## 🔧 Configuration

### Adding New Symbols

In sidebar:
```
BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT
```

Or programmatically:
```python
app.start_ingestion(['BTCUSDT', 'ETHUSDT', 'ADAUSDT'])
```

### Custom Alert Rules

```python
# Z-Score Alert
app.add_alert_rule('zscore', 
    symbol1='BTCUSDT', 
    symbol2='ETHUSDT', 
    threshold=2.5,
    severity='warning'
)

# Price Alert
app.add_alert_rule('price',
    symbol='BTCUSDT',
    threshold=50000,
    direction='above',
    severity='info'
)
```

### Upload Historical Data

CSV format:
```csv
timestamp,open,high,low,close,volume
2024-01-01 00:00:00,50000,50100,49900,50050,100.5
2024-01-01 00:01:00,50050,50200,50040,50150,120.3
```

Upload via sidebar or:
```python
app.upload_ohlc_data('data/historical.csv', 'BTCUSDT', '1m')
```

## 📈 Use Cases

### Statistical Arbitrage
- Monitor BTC/ETH spread for mean-reversion opportunities
- Dynamic hedge ratio adjusts to changing correlations
- ADF test confirms stationarity before trading

### Market Making
- Real-time spread monitoring
- Liquidity metrics and volume spikes
- VWAP for fair price discovery

### Risk Management
- Correlation breakdown alerts
- Volume spike detection
- Price threshold notifications

### Research & Backtesting
- Historical spread analysis
- Strategy parameter optimization
- Performance attribution

## 🔄 Scaling Considerations

### Current Limitations
- Single-machine deployment
- SQLite for storage (not distributed)
- In-memory analytics (RAM constrained)

### Production Scaling Path

1. **Data Ingestion**:
   - Current: Single WebSocket per symbol
   - Scale: Kafka/RabbitMQ message queue
   - Scale: Multiple ingestion workers

2. **Storage**:
   - Current: SQLite + Redis
   - Scale: TimescaleDB (PostgreSQL extension for time-series)
   - Scale: ClickHouse for OLAP analytics

3. **Analytics**:
   - Current: On-demand computation
   - Scale: Pre-computed analytics with caching
   - Scale: Distributed computation with Dask/Ray

4. **Frontend**:
   - Current: Streamlit (single user)
   - Scale: FastAPI + React for multi-user
   - Scale: WebSocket push for real-time updates

5. **Alerts**:
   - Current: In-memory rules
   - Scale: Centralized alert service
   - Scale: Integration with PagerDuty/Slack

### Extensibility Examples

**Add New Data Source**:
```python
class AlpacaWebSocketClient(DataIngestionClient):
    def connect(self):
        # Implement Alpaca-specific logic
        pass
```

**Add Custom Indicator**:
```python
@staticmethod
def compute_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    # Implement RSI logic
    return rsi_series
```

**Add New Visualization**:
```python
with tab_custom:
    st.markdown("## Custom Analysis")
    # Your custom charts and logic
```

## 📁 Project Structure

```
gemscap/
├── app.py                          # Main orchestrator
├── frontend.py                     # Streamlit dashboard
├── requirements.txt                # Dependencies
├── README.md                       # This file
│
├── backend/
│   ├── data_ingestion.py          # WebSocket client
│   ├── storage.py                 # SQLite + Redis layer
│   ├── resampling.py              # Tick-to-OHLCV conversion
│   ├── analytics.py               # Quant analytics engine
│   ├── alerts.py                  # Alert rule manager
│   └── backtest.py                # Backtesting engine
│
├── data/                           # Generated data files
│   ├── ticks.db                   # SQLite database
│   └── exports/                   # CSV exports
│
└── docs/
    └── architecture.drawio         # Architecture diagram
```

## 🤖 ChatGPT Usage

### How AI Was Used

I extensively used ChatGPT-4 and Copilot throughout this project for:

1. **Architecture Design**:
   - Prompt: "Design a modular real-time analytics system for trading with clean separation between ingestion, storage, analytics, and visualization"
   - Used for validating design patterns and identifying bottlenecks

2. **Code Implementation**:
   - Prompt: "Implement Kalman filter for dynamic hedge ratio estimation in Python"
   - Generated boilerplate for WebSocket connections, database schemas
   - Debugged asyncio concurrency issues

3. **Statistical Methods**:
   - Prompt: "Explain half-life calculation for mean-reverting time series"
   - Verified correctness of ADF test implementation
   - Optimized z-score computation for rolling windows

4. **Frontend Development**:
   - Prompt: "Create Streamlit dashboard with multiple tabs, real-time charts using Plotly"
   - Generated CSS for custom styling
   - Implemented auto-refresh logic

5. **Documentation**:
   - Prompt: "Write comprehensive README for trading analytics platform"
   - Generated docstrings and code comments
   - Created usage examples

### Transparency Note

Approximately **60-70%** of the code was AI-assisted, with human oversight for:
- Architecture decisions
- Algorithm selection (OLS vs Kalman)
- Error handling and edge cases
- Performance optimization
- Integration testing

All AI-generated code was **reviewed, tested, and modified** to ensure correctness and alignment with requirements.

## 🎓 Key Learning & Design Decisions

### Why This Architecture?

1. **Modular Backend**: Each service (ingestion, storage, analytics) can be developed, tested, and scaled independently

2. **Hybrid Storage**: SQLite for simplicity and Redis for performance—easy to migrate to production databases

3. **Kalman Filter**: More sophisticated than static OLS; adapts to regime changes

4. **Event-Driven Alerts**: Decoupled from analytics—new rules don't require code changes

5. **Streamlit Frontend**: Rapid development, built-in reactivity, perfect for internal tools

### Trade-offs Made

| Decision | Pros | Cons | Rationale |
|----------|------|------|-----------|
| SQLite | Simple, no setup | Not distributed | Sufficient for 1-day data requirement |
| Streamlit | Fast development | Limited scalability | Focus on analytics, not user scale |
| Synchronous analytics | Easier debugging | Blocks on computation | On-demand is acceptable for demo |
| In-memory alerts | Low latency | Lost on restart | Can persist to DB if needed |

## 🐛 Troubleshooting

### WebSocket Connection Issues
- **Error**: `Connection refused`
- **Solution**: Check internet connection, verify Binance API is accessible

### Redis Not Available
- **Warning**: `Redis not available`
- **Solution**: System will work with SQLite only (slightly slower). Install Redis for best performance.

### Insufficient Data
- **Error**: `Need at least 20 data points`
- **Solution**: Wait longer after starting ingestion (30-60 seconds)

### No Charts Displaying
- **Issue**: Empty charts in dashboard
- **Solution**: Click "▶️ Start" button, wait for data collection

## 📜 License

MIT License - feel free to use this for educational or commercial purposes.

## 🙏 Acknowledgments

- **Binance**: Real-time market data API
- **Streamlit**: Excellent framework for data apps
- **Plotly**: Interactive charting library
- **ChatGPT**: Development assistance and code generation

---

**Built with ❤️ for quantitative trading research**

For questions or issues, please refer to the inline documentation or submit an issue.
