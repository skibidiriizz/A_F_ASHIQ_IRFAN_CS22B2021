"""
Streamlit Frontend for Trading Analytics Dashboard
Professional UI/UX with advanced visualizations and interactive controls.
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

from app import TradingAnalyticsApp

# Page config
st.set_page_config(
    page_title="Quant Analytics Platform",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced Custom CSS for professional look
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container */
    .main {
        padding: 2rem 3rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] .element-container {
        padding: 0.5rem 1rem;
    }
    
    /* Header styles */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Card styles */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.5);
        border-color: rgba(59, 130, 246, 0.5);
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: scale(1.05);
        border-color: rgba(59, 130, 246, 0.6);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    .metric-change {
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        color: #10b981;
    }
    
    .metric-change.negative {
        color: #ef4444;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
    
    .status-running {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    .status-stopped {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
    }
    
    /* Alert boxes */
    .alert-box {
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border-left: 4px solid;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-10px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .alert-critical {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
        border-left-color: #ef4444;
        color: #fca5a5;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        border-left-color: #f59e0b;
        color: #fcd34d;
    }
    
    .alert-info {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
        border-left-color: #3b82f6;
        color: #93c5fd;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(30, 41, 59, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #94a3b8;
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 8px;
        color: #e2e8f0;
        padding: 0.6rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: rgba(59, 130, 246, 0.3);
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.6);
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.2);
    }
    
    /* Section divider */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent 0%, #3b82f6 50%, transparent 100%);
        margin: 2rem 0;
    }
    
    /* Loading animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        border-radius: 50%;
        border-top-color: #3b82f6;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    /* Trade signal badge */
    .signal-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .signal-long {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    }
    
    .signal-short {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        color: white;
    }
    
    /* Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        color: #94a3b8;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(30, 41, 59, 0.5);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(59, 130, 246, 0.5);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(59, 130, 246, 0.7);
    }
</style>
""", unsafe_allow_html=True)

# Initialize app
@st.cache_resource
def get_app():
    """Initialize and cache the main application"""
    return TradingAnalyticsApp()

app = get_app()

# Sidebar - Enhanced Design
st.sidebar.markdown("""
<div style='text-align: center; padding: 1.5rem 0;'>
    <h1 style='font-size: 2rem; margin: 0; background: linear-gradient(135deg, #06b6d4 0%, #8b5cf6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        📊 Quant Platform
    </h1>
    <p style='color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;'>Real-Time Analytics Engine</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Data ingestion controls
st.sidebar.markdown("### 🌐 Data Ingestion")
default_symbols = st.sidebar.text_input("Symbols (comma-separated)", "BTCUSDT,ETHUSDT", 
                                        help="Enter trading symbols separated by commas")
symbols_list = [s.strip().upper() for s in default_symbols.split(',')]

col1, col2 = st.sidebar.columns(2)
start_btn = col1.button("▶️ Start", use_container_width=True, type="primary")
stop_btn = col2.button("⏹️ Stop", use_container_width=True)

if start_btn:
    if not app.running:
        app.start_ingestion(symbols_list)
        st.sidebar.success("✓ Started successfully!")
        time.sleep(0.5)
        st.rerun()
    else:
        st.sidebar.warning("⚠️ Already running")

if stop_btn:
    if app.running:
        app.stop_ingestion()
        st.sidebar.info("✓ Stopped")
        time.sleep(0.5)
        st.rerun()

# Status indicator with enhanced styling
status_html = f"""
<div style='text-align: center; padding: 1rem; margin: 1rem 0;'>
    <span class='status-badge {"status-running" if app.running else "status-stopped"}'>
        {'🟢 LIVE' if app.running else '🔴 OFFLINE'}
    </span>
</div>
"""
st.sidebar.markdown(status_html, unsafe_allow_html=True)

if app.running:
    st.sidebar.markdown(f"""
    <div style='background: rgba(16, 185, 129, 0.1); padding: 0.8rem; border-radius: 8px; border-left: 3px solid #10b981; margin: 1rem 0;'>
        <div style='font-size: 0.75rem; color: #6ee7b7; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem;'>Active Streams</div>
        <div style='color: #d1fae5; font-weight: 600;'>{', '.join(symbols_list)}</div>
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Analytics parameters
st.sidebar.markdown("### ⚙️ Analytics Configuration")
timeframe = st.sidebar.selectbox("📊 Timeframe", ['1s', '1m', '5m', '15m'], index=1,
                                 help="Data aggregation interval")
window_size = st.sidebar.slider("📏 Rolling Window", 10, 100, 20,
                                help="Number of periods for rolling calculations")
use_kalman = st.sidebar.checkbox("🔄 Kalman Filter", value=False,
                                 help="Use dynamic hedge ratio (vs static OLS)")

regression_type = "Kalman Filter" if use_kalman else "OLS Regression"
st.sidebar.markdown(f"""
<div style='background: rgba(59, 130, 246, 0.1); padding: 0.6rem; border-radius: 6px; font-size: 0.8rem; color: #93c5fd;'>
    <strong>Method:</strong> {regression_type}
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Pair selection
st.sidebar.markdown("### 📈 Trading Pair")
if len(symbols_list) >= 2:
    symbol1 = st.sidebar.selectbox("Primary Symbol", symbols_list, index=0,
                                   help="First symbol in the pair")
    symbol2 = st.sidebar.selectbox("Secondary Symbol", symbols_list, index=1,
                                   help="Second symbol in the pair")
else:
    symbol1 = "BTCUSDT"
    symbol2 = "ETHUSDT"

st.sidebar.markdown(f"""
<div style='background: rgba(139, 92, 246, 0.1); padding: 0.8rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;'>
    <div style='color: #c4b5fd; font-weight: 600; font-size: 1.1rem;'>{symbol1} / {symbol2}</div>
    <div style='color: #a78bfa; font-size: 0.75rem; margin-top: 0.3rem;'>Pairs Trading Analysis</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Alert configuration
st.sidebar.markdown("### 🔔 Alert Management")
with st.sidebar.expander("➕ Create New Alert", expanded=False):
    alert_type = st.selectbox("Alert Type", ['zscore', 'price', 'spread', 'volume'],
                             help="Choose the type of alert to create")
    
    if alert_type == 'zscore':
        zscore_threshold = st.number_input("Z-Score Threshold", 1.0, 5.0, 2.0, 0.1,
                                          help="Alert when |z-score| exceeds this value")
        if st.button("✓ Add Z-Score Alert", use_container_width=True):
            app.add_alert_rule('zscore', symbol1=symbol1, symbol2=symbol2, 
                             threshold=zscore_threshold, severity='warning')
            st.success("✓ Alert created!")
            time.sleep(0.5)
            st.rerun()
    
    elif alert_type == 'price':
        price_symbol = st.selectbox("Symbol", symbols_list, key="price_alert_symbol")
        price_threshold = st.number_input("Price Threshold", 0.0, 1000000.0, 50000.0, 100.0,
                                         help="Alert when price crosses this level")
        direction = st.radio("Direction", ['above', 'below'], horizontal=True)
        if st.button("✓ Add Price Alert", use_container_width=True):
            app.add_alert_rule('price', symbol=price_symbol, threshold=price_threshold,
                             direction=direction, severity='info')
            st.success("✓ Alert created!")
            time.sleep(0.5)
            st.rerun()
    
    elif alert_type == 'spread':
        spread_threshold = st.number_input("Spread Threshold", 0.0, 10000.0, 100.0, 10.0)
        if st.button("✓ Add Spread Alert", use_container_width=True):
            app.add_alert_rule('spread', symbol1=symbol1, symbol2=symbol2,
                             threshold=spread_threshold, severity='warning')
            st.success("✓ Alert created!")
            time.sleep(0.5)
            st.rerun()
    
    elif alert_type == 'volume':
        vol_symbol = st.selectbox("Symbol", symbols_list, key="vol_alert_symbol")
        spike_threshold = st.slider("Spike Multiplier", 1.5, 10.0, 3.0, 0.5,
                                   help="Alert when volume is X times the average")
        if st.button("✓ Add Volume Alert", use_container_width=True):
            app.add_alert_rule('volume', symbol=vol_symbol, spike_threshold=spike_threshold,
                             severity='info')
            st.success("✓ Alert created!")
            time.sleep(0.5)
            st.rerun()

# Show active alert count
active_rules = len(app.alert_manager.rules)
st.sidebar.markdown(f"""
<div style='background: rgba(251, 191, 36, 0.1); padding: 0.6rem; border-radius: 6px; text-align: center;'>
    <span style='color: #fcd34d; font-weight: 600;'>{active_rules} Active Rule{"s" if active_rules != 1 else ""}</span>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)

# Upload data
st.sidebar.markdown("### 📤 Data Upload")
with st.sidebar.expander("Upload Historical Data"):
    uploaded_file = st.file_uploader("Upload CSV (OHLCV)", type=['csv'],
                                     help="CSV with: timestamp, open, high, low, close, volume")
    if uploaded_file:
        upload_symbol = st.text_input("Symbol", "BTCUSDT", key="upload_symbol")
        upload_timeframe = st.selectbox("Timeframe", ['1m', '5m', '1h'], key="upload_tf")
        if st.button("📥 Process Upload", use_container_width=True):
            with st.spinner("Processing..."):
                if app.upload_ohlc_data(uploaded_file, upload_symbol, upload_timeframe):
                    st.success("✓ Data uploaded!")
                else:
                    st.error("✗ Upload failed")

# Footer with version info
st.sidebar.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='text-align: center; color: #64748b; font-size: 0.75rem; padding: 1rem;'>
    <div style='margin-bottom: 0.5rem;'>
        <strong style='color: #94a3b8;'>Quant Analytics Platform</strong>
    </div>
    <div>Version 1.0.0</div>
    <div style='margin-top: 0.5rem;'>Built for Statistical Arbitrage</div>
</div>
""", unsafe_allow_html=True)

# Main content - Enhanced Header
st.markdown("""
<div style='text-align: center; padding: 2rem 0 3rem 0;'>
    <div class='main-header'>Real-Time Quantitative Analytics</div>
    <div class='sub-header'>
        Professional trading analytics for statistical arbitrage and market microstructure analysis
    </div>
</div>
""", unsafe_allow_html=True)

# Create tabs with better naming
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview", 
    "🔬 Pairs Analytics", 
    "🎯 Strategy Backtest", 
    "🔔 Alert Monitor",
    "📥 Data Management"
])

# Tab 1: Enhanced Overview
with tab1:
    st.markdown("## 🌐 Live Market Dashboard")
    
    if not app.running:
        st.info("⚠️ Data ingestion is not running. Click **▶️ Start** in the sidebar to begin collecting live data.")
    
    # Enhanced metrics row with better styling
    metric_cols = st.columns(len(symbols_list) if len(symbols_list) <= 4 else 4)
    
    for idx, symbol in enumerate(symbols_list[:4]):  # Show max 4 symbols
        with metric_cols[idx]:
            df = app.get_ohlcv_data(symbol, timeframe, minutes=60)
            
            if not df.empty and len(df) > 1:
                last_price = df['close'].iloc[-1]
                prev_price = df['close'].iloc[-2] if len(df) > 1 else last_price
                change = ((last_price - prev_price) / prev_price) * 100 if prev_price > 0 else 0
                volume = df['volume'].iloc[-1]
                avg_volume = df['volume'].mean()
                
                # Calculate additional metrics
                high_24h = df['high'].max()
                low_24h = df['low'].min()
                
                change_class = "positive" if change >= 0 else "negative"
                arrow = "↑" if change >= 0 else "↓"
                
                st.markdown(f"""
                <div class='glass-card'>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.1rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.5rem;'>
                            {symbol.replace('USDT', '/USDT')}
                        </div>
                        <div class='metric-value' style='color: {"#10b981" if change >= 0 else "#ef4444"};'>
                            ${last_price:,.2f}
                        </div>
                        <div class='metric-change {change_class}'>
                            {arrow} {abs(change):.2f}%
                        </div>
                        <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(148, 163, 184, 0.2);'>
                            <div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.3rem;'>
                                <span>24h High:</span>
                                <span style='color: #10b981; font-weight: 600;'>${high_24h:,.2f}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.3rem;'>
                                <span>24h Low:</span>
                                <span style='color: #ef4444; font-weight: 600;'>${low_24h:,.2f}</span>
                            </div>
                            <div style='display: flex; justify-content: space-between; font-size: 0.8rem; color: #94a3b8;'>
                                <span>Volume:</span>
                                <span style='color: #e2e8f0; font-weight: 600;'>{volume:,.0f}</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='glass-card'>
                    <div style='text-align: center;'>
                        <div style='font-size: 1.1rem; font-weight: 600; color: #94a3b8; margin-bottom: 0.5rem;'>
                            {symbol.replace('USDT', '/USDT')}
                        </div>
                        <div style='color: #64748b; padding: 2rem 0;'>
                            <div class='loading-spinner'></div>
                            <div style='margin-top: 1rem; font-size: 0.9rem;'>Waiting for data...</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Price charts with enhanced visualization
    st.markdown("### 📈 Price Charts & Volume Analysis")
    
    chart_cols = st.columns(2)
    
    for idx, symbol in enumerate(symbols_list[:2]):  # Show first 2 symbols
        with chart_cols[idx]:
            df = app.get_ohlcv_data(symbol, timeframe, minutes=120)
            
            if not df.empty:
                # Create subplot with price and volume
                fig = make_subplots(
                    rows=2, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.03,
                    row_heights=[0.7, 0.3],
                    subplot_titles=(f'{symbol} Price', 'Volume')
                )
                
                # Candlestick chart
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='OHLC',
                    increasing_line_color='#10b981',
                    decreasing_line_color='#ef4444'
                ), row=1, col=1)
                
                # Add moving average
                if len(df) >= 20:
                    ma20 = df['close'].rolling(20).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=ma20,
                        name='MA(20)',
                        line=dict(color='#f59e0b', width=2, dash='dash')
                    ), row=1, col=1)
                
                # Volume bars
                colors = ['#10b981' if row['close'] >= row['open'] else '#ef4444' 
                         for _, row in df.iterrows()]
                
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ), row=2, col=1)
                
                fig.update_layout(
                    title=dict(
                        text=f"<b>{symbol}</b> · {timeframe} Timeframe",
                        font=dict(size=16, color='#e2e8f0')
                    ),
                    height=500,
                    template="plotly_dark",
                    xaxis_rangeslider_visible=False,
                    hovermode='x unified',
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    paper_bgcolor='rgba(15, 23, 42, 0.8)',
                    plot_bgcolor='rgba(30, 41, 59, 0.5)',
                )
                
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"⏳ Collecting data for {symbol}... Please wait.")
    
    # Additional market stats
    if len(symbols_list) >= 2:
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        st.markdown("### 📊 Market Statistics")
        
        stat_cols = st.columns(4)
        
        for idx, symbol in enumerate(symbols_list[:4]):
            df = app.get_ohlcv_data(symbol, timeframe, minutes=60)
            
            if not df.empty and len(df) > 1:
                with stat_cols[idx]:
                    returns = df['close'].pct_change().dropna()
                    volatility = returns.std() * np.sqrt(len(df))  # Annualized approximation
                    
                    st.markdown(f"""
                    <div style='background: rgba(30, 41, 59, 0.5); padding: 1rem; border-radius: 8px; border: 1px solid rgba(148, 163, 184, 0.2);'>
                        <div style='color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.5rem;'>{symbol}</div>
                        <div style='color: #e2e8f0; font-size: 0.85rem;'>
                            <div style='margin-bottom: 0.3rem;'>Volatility: <strong>{volatility*100:.2f}%</strong></div>
                            <div>Avg Volume: <strong>{df['volume'].mean():,.0f}</strong></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# Tab 2: Enhanced Pair Analytics
with tab2:
    st.markdown(f"## 🔬 {symbol1} / {symbol2} Quantitative Analysis")
    
    # Control row
    control_col1, control_col2, control_col3 = st.columns([2, 2, 1])
    
    with control_col1:
        auto_refresh = st.checkbox("🔄 Auto-refresh (2s)", value=False, 
                                   help="Automatically update analytics every 2 seconds")
    
    with control_col2:
        if st.button("🔍 Compute Analytics", use_container_width=True, type="primary"):
            st.rerun()
    
    with control_col3:
        refresh_time = datetime.now().strftime("%H:%M:%S")
        st.markdown(f"<div style='text-align: right; color: #64748b; font-size: 0.8rem; padding-top: 0.5rem;'>⏰ {refresh_time}</div>", unsafe_allow_html=True)
    
    # Compute analytics
    with st.spinner("🔄 Computing quantitative analytics..."):
        analytics = app.compute_pair_analytics(symbol1, symbol2, timeframe, window_size, use_kalman)
    
    if 'error' in analytics:
        st.error(f"⚠️ Error: {analytics['error']}")
        st.info("""
        💡 **Troubleshooting Tips:**
        - Ensure data ingestion is running (click ▶️ Start in sidebar)
        - Wait 60-90 seconds for sufficient data collection
        - Check that symbols are correctly specified
        - Verify WebSocket connection to Binance
        """)
    else:
        # Key metrics row with enhanced cards
        st.markdown("### 📊 Key Performance Indicators")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            beta = analytics['regression']['beta']
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Hedge Ratio (β)</div>
                <div class='metric-value'>{beta:.4f}</div>
                <div style='color: #64748b; font-size: 0.75rem; margin-top: 0.5rem;'>
                    {regression_type}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            r_squared = analytics['regression'].get('r_squared', 0)
            r2_color = "#10b981" if r_squared > 0.7 else "#f59e0b" if r_squared > 0.4 else "#ef4444"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>R-Squared</div>
                <div class='metric-value' style='color: {r2_color};'>{r_squared:.4f}</div>
                <div style='color: #64748b; font-size: 0.75rem; margin-top: 0.5rem;'>
                    {"Excellent" if r_squared > 0.7 else "Moderate" if r_squared > 0.4 else "Weak"} Fit
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            zscore = analytics['zscore_last']
            zscore_abs = abs(zscore)
            
            if zscore_abs > 2.5:
                signal = "STRONG"
                signal_color = "#ef4444"
                signal_class = "signal-short" if zscore > 0 else "signal-long"
            elif zscore_abs > 2:
                signal = "MODERATE"
                signal_color = "#f59e0b"
                signal_class = "signal-short" if zscore > 0 else "signal-long"
            else:
                signal = "NEUTRAL"
                signal_color = "#64748b"
                signal_class = "signal-neutral"
            
            st.markdown(f"""
            <div class='metric-card' style='border-color: {signal_color};'>
                <div class='metric-label'>Z-Score</div>
                <div class='metric-value' style='color: {signal_color};'>{zscore:.2f}</div>
                <div style='margin-top: 0.5rem;'>
                    <span class='signal-badge {signal_class}'>{signal}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            corr = analytics['correlation_last']
            corr_color = "#10b981" if corr > 0.7 else "#f59e0b" if corr > 0.4 else "#ef4444"
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Correlation</div>
                <div class='metric-value' style='color: {corr_color};'>{corr:.3f}</div>
                <div style='color: #64748b; font-size: 0.75rem; margin-top: 0.5rem;'>
                    Rolling({window_size})
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            spread = analytics['spread_last']
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Current Spread</div>
                <div class='metric-value'>{spread:.2f}</div>
                <div style='color: #64748b; font-size: 0.75rem; margin-top: 0.5rem;'>
                    P₁ - β×P₂
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Trading signal interpretation
        if zscore_abs > 2:
            signal_text = "Short Spread" if zscore > 0 else "Long Spread"
            signal_desc = f"Spread is {zscore_abs:.2f}σ from mean. Consider {signal_text} position (mean reversion strategy)."
            st.markdown(f"""
            <div class='alert-box alert-warning'>
                <strong>🎯 Trading Signal:</strong> {signal_desc}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        
        # Charts section with better layout
        st.markdown("### 📈 Visual Analysis")
        
        # Price comparison chart
        st.markdown("#### Normalized Price Comparison")
        df1 = app.get_ohlcv_data(symbol1, timeframe, minutes=120)
        df2 = app.get_ohlcv_data(symbol2, timeframe, minutes=120)
        
        if not df1.empty and not df2.empty:
            # Normalize prices to start at 100
            norm1 = (df1['close'] / df1['close'].iloc[0]) * 100
            norm2 = (df2['close'] / df2['close'].iloc[0]) * 100
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df1.index,
                y=norm1,
                name=symbol1,
                line=dict(color='#06b6d4', width=3),
                fill='tonexty',
                fillcolor='rgba(6, 182, 212, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=df2.index,
                y=norm2,
                name=symbol2,
                line=dict(color='#8b5cf6', width=3),
                fill='tonexty',
                fillcolor='rgba(139, 92, 246, 0.1)'
            ))
            
            fig.update_layout(
                title=dict(
                    text="<b>Normalized Price Movement</b> (Base = 100)",
                    font=dict(size=16, color='#e2e8f0')
                ),
                height=400,
                template="plotly_dark",
                hovermode='x unified',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                paper_bgcolor='rgba(15, 23, 42, 0.8)',
                plot_bgcolor='rgba(30, 41, 59, 0.5)',
                yaxis_title="Normalized Price",
                xaxis_title="Time"
            )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Spread and Z-Score charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Spread Analysis")
            if analytics['spread'] is not None and len(analytics['spread']) > 0:
                spread_df = pd.DataFrame({'spread': analytics['spread']})
                
                fig = go.Figure()
                
                # Spread line
                fig.add_trace(go.Scatter(
                    x=spread_df.index,
                    y=spread_df['spread'],
                    name='Spread',
                    line=dict(color='#8b5cf6', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(139, 92, 246, 0.1)'
                ))
                
                # Mean line
                mean_spread = spread_df['spread'].mean()
                fig.add_hline(y=mean_spread, line_dash="dash", line_color="#94a3b8",
                             annotation_text="Mean", annotation_position="right")
                
                fig.update_layout(
                    title=dict(
                        text="<b>Spread Time Series</b>",
                        font=dict(size=14, color='#e2e8f0')
                    ),
                    height=350,
                    template="plotly_dark",
                    paper_bgcolor='rgba(15, 23, 42, 0.8)',
                    plot_bgcolor='rgba(30, 41, 59, 0.5)',
                    yaxis_title="Spread Value",
                    xaxis_title="Time",
                    showlegend=False
                )
                
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
                
                st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            st.markdown("#### Z-Score Analysis")
            if analytics['zscore'] is not None and len(analytics['zscore']) > 0:
                zscore_df = pd.DataFrame({'zscore': analytics['zscore']})
                
                fig = go.Figure()
                
                # Z-score line with conditional coloring
                colors = ['#10b981' if abs(z) <= 1 else '#f59e0b' if abs(z) <= 2 else '#ef4444' 
                         for z in zscore_df['zscore']]
                
                fig.add_trace(go.Scatter(
                    x=zscore_df.index,
                    y=zscore_df['zscore'],
                    name='Z-Score',
                    line=dict(color='#10b981', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(16, 185, 129, 0.1)'
                ))
                
                # Threshold lines
                fig.add_hline(y=2, line_dash="dash", line_color="#ef4444", line_width=2,
                             annotation_text="Entry (+2σ)", annotation_position="right")
                fig.add_hline(y=-2, line_dash="dash", line_color="#10b981", line_width=2,
                             annotation_text="Entry (-2σ)", annotation_position="right")
                fig.add_hline(y=0, line_dash="dot", line_color="#64748b",
                             annotation_text="Mean", annotation_position="right")
                
                # Shaded regions
                fig.add_hrect(y0=-2, y1=2, fillcolor="rgba(16, 185, 129, 0.05)", 
                             layer="below", line_width=0)
                fig.add_hrect(y0=2, y1=5, fillcolor="rgba(239, 68, 68, 0.05)", 
                             layer="below", line_width=0)
                fig.add_hrect(y0=-5, y1=-2, fillcolor="rgba(16, 185, 129, 0.05)", 
                             layer="below", line_width=0)
                
                fig.update_layout(
                    title=dict(
                        text=f"<b>Z-Score Evolution</b> (window={window_size})",
                        font=dict(size=14, color='#e2e8f0')
                    ),
                    height=350,
                    template="plotly_dark",
                    paper_bgcolor='rgba(15, 23, 42, 0.8)',
                    plot_bgcolor='rgba(30, 41, 59, 0.5)',
                    yaxis_title="Z-Score (σ)",
                    xaxis_title="Time",
                    showlegend=False
                )
                
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Rolling Correlation
        st.markdown("#### Rolling Correlation & Market Regime")
        if analytics['correlation'] is not None and len(analytics['correlation']) > 0:
            corr_df = pd.DataFrame({'correlation': analytics['correlation']})
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=corr_df.index,
                y=corr_df['correlation'],
                name='Correlation',
                line=dict(color='#ec4899', width=2),
                fill='tozeroy',
                fillcolor='rgba(236, 72, 153, 0.1)'
            ))
            
            # Correlation regime lines
            fig.add_hline(y=0.7, line_dash="dash", line_color="#10b981",
                         annotation_text="Strong (+)", annotation_position="right")
            fig.add_hline(y=0, line_dash="dot", line_color="#64748b",
                         annotation_text="Uncorrelated", annotation_position="right")
            
            fig.update_layout(
                title=dict(
                    text=f"<b>Rolling Correlation</b> (window={window_size})",
                    font=dict(size=14, color='#e2e8f0')
                ),
                height=300,
                template="plotly_dark",
                paper_bgcolor='rgba(15, 23, 42, 0.8)',
                plot_bgcolor='rgba(30, 41, 59, 0.5)',
                yaxis_title="Correlation Coefficient",
                xaxis_title="Time",
                showlegend=False,
                yaxis=dict(range=[-1, 1])
            )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
        
        # Statistical Tests & Advanced Metrics
        st.markdown("### 📐 Statistical Tests & Advanced Metrics")
        
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.markdown("""
            <div class='glass-card'>
                <h4 style='color: #06b6d4; font-size: 1rem; margin-bottom: 1rem;'>ADF Stationarity Test</h4>
            """, unsafe_allow_html=True)
            
            adf = analytics['adf']
            is_stationary = adf.get('is_stationary', False)
            p_value = adf.get('pvalue', 1)
            
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <span style='color: #94a3b8;'>Test Statistic:</span><br>
                    <strong style='color: #e2e8f0; font-size: 1.1rem;'>{adf.get('statistic', 0):.4f}</strong>
                </div>
                <div style='margin-bottom: 0.5rem;'>
                    <span style='color: #94a3b8;'>P-Value:</span><br>
                    <strong style='color: {"#10b981" if p_value < 0.05 else "#ef4444"}; font-size: 1.1rem;'>{p_value:.4f}</strong>
                </div>
                <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(148, 163, 184, 0.2);'>
                    <span style='color: #94a3b8;'>Result:</span><br>
                    <strong style='color: {"#10b981" if is_stationary else "#ef4444"};'>
                        {'✓ Stationary' if is_stationary else '✗ Non-Stationary'}
                    </strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col2:
            st.markdown("""
            <div class='glass-card'>
                <h4 style='color: #8b5cf6; font-size: 1rem; margin-bottom: 1rem;'>Mean Reversion</h4>
            """, unsafe_allow_html=True)
            
            half_life = analytics.get('half_life', float('nan'))
            
            if half_life == half_life and half_life > 0:  # Check not NaN
                st.markdown(f"""
                    <div style='margin-bottom: 0.5rem;'>
                        <span style='color: #94a3b8;'>Half-Life:</span><br>
                        <strong style='color: #e2e8f0; font-size: 1.5rem;'>{half_life:.1f}</strong>
                        <span style='color: #94a3b8;'> bars</span>
                    </div>
                    <div style='margin-top: 1rem; color: #94a3b8; font-size: 0.85rem;'>
                        Time for spread to revert halfway to mean
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='color: #64748b; text-align: center; padding: 1rem 0;'>
                        Insufficient data for calculation
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with stat_col3:
            st.markdown("""
            <div class='glass-card'>
                <h4 style='color: #f59e0b; font-size: 1rem; margin-bottom: 1rem;'>Regression Method</h4>
            """, unsafe_allow_html=True)
            
            method = analytics['regression'].get('method', 'ols').upper()
            method_desc = "Dynamic hedge ratio adapts to market conditions" if method == "KALMAN" else "Static hedge ratio from historical data"
            
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <span style='color: #94a3b8;'>Method:</span><br>
                    <strong style='color: #e2e8f0; font-size: 1.2rem;'>{method}</strong>
                </div>
                <div style='margin-top: 1rem; color: #94a3b8; font-size: 0.85rem;'>
                    {method_desc}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with stat_col4:
            st.markdown("""
            <div class='glass-card'>
                <h4 style='color: #ec4899; font-size: 1rem; margin-bottom: 1rem;'>Data Quality</h4>
            """, unsafe_allow_html=True)
            
            data_points = analytics.get('data_points', 0)
            quality = "Excellent" if data_points > 100 else "Good" if data_points > 50 else "Limited"
            quality_color = "#10b981" if data_points > 100 else "#f59e0b" if data_points > 50 else "#ef4444"
            
            st.markdown(f"""
                <div style='margin-bottom: 0.5rem;'>
                    <span style='color: #94a3b8;'>Data Points:</span><br>
                    <strong style='color: #e2e8f0; font-size: 1.5rem;'>{data_points}</strong>
                </div>
                <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(148, 163, 184, 0.2);'>
                    <span style='color: #94a3b8;'>Quality:</span><br>
                    <strong style='color: {quality_color};'>{quality}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Kalman filter visualization
        if use_kalman and 'kalman_hedge_ratios' in analytics and analytics['kalman_hedge_ratios'] is not None:
            st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
            st.markdown("### 🔄 Dynamic Hedge Ratio Evolution (Kalman Filter)")
            
            hedge_ratios = analytics['kalman_hedge_ratios']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=hedge_ratios.index,
                y=hedge_ratios.values,
                name='Hedge Ratio (β)',
                line=dict(color='#06b6d4', width=3),
                fill='tozeroy',
                fillcolor='rgba(6, 182, 212, 0.1)'
            ))
            
            # Add mean line
            mean_beta = hedge_ratios.mean()
            fig.add_hline(y=mean_beta, line_dash="dash", line_color="#94a3b8",
                         annotation_text=f"Mean: {mean_beta:.4f}", annotation_position="right")
            
            fig.update_layout(
                title=dict(
                    text="<b>Kalman Filter: Adaptive Hedge Ratio Tracking</b>",
                    font=dict(size=16, color='#e2e8f0')
                ),
                height=350,
                template="plotly_dark",
                paper_bgcolor='rgba(15, 23, 42, 0.8)',
                plot_bgcolor='rgba(30, 41, 59, 0.5)',
                yaxis_title="Beta (Hedge Ratio)",
                xaxis_title="Time",
                showlegend=False
            )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(148, 163, 184, 0.1)')
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(2)
        st.rerun()

# Tab 3: Backtest
with tab3:
    st.markdown("## Mean-Reversion Backtest")
    
    st.info("💡 This backtest simulates a simple mean-reversion strategy: Enter when |z-score| > threshold, exit when z-score reverts to zero.")
    
    # Backtest parameters
    param_col1, param_col2 = st.columns(2)
    
    with param_col1:
        entry_z = st.slider("Entry Z-Score Threshold", 1.0, 4.0, 2.0, 0.1)
    
    with param_col2:
        exit_z = st.slider("Exit Z-Score Threshold", -1.0, 1.0, 0.0, 0.1)
    
    if st.button("🚀 Run Backtest"):
        with st.spinner("Running backtest..."):
            backtest_results = app.run_backtest(symbol1, symbol2, timeframe, entry_z, exit_z)
        
        if 'error' in backtest_results:
            st.error(f"Error: {backtest_results['error']}")
        else:
            # Performance metrics
            st.markdown("### Performance Summary")
            
            metric_cols = st.columns(5)
            
            with metric_cols[0]:
                st.metric("Total Trades", backtest_results['total_trades'])
            
            with metric_cols[1]:
                st.metric("Win Rate", f"{backtest_results['win_rate']*100:.1f}%")
            
            with metric_cols[2]:
                st.metric("Total PnL", f"{backtest_results['total_pnl']:.2f}")
            
            with metric_cols[3]:
                st.metric("Avg PnL", f"{backtest_results['avg_pnl']:.2f}")
            
            with metric_cols[4]:
                st.metric("Sharpe Ratio", f"{backtest_results['sharpe_ratio']:.2f}")
            
            st.markdown("---")
            
            # Trades table
            if backtest_results['trades']:
                st.markdown("### Trade History")
                
                trades_df = pd.DataFrame(backtest_results['trades'])
                trades_df['pnl_color'] = trades_df['pnl'].apply(lambda x: '🟢' if x > 0 else '🔴')
                
                st.dataframe(
                    trades_df[['pnl_color', 'entry_time', 'exit_time', 'position', 'entry_price', 'exit_price', 'pnl', 'return_pct']],
                    use_container_width=True,
                    height=400
                )
                
                # Equity curve
                st.markdown("### Equity Curve")
                
                cumulative_pnl = np.cumsum([t['pnl'] for t in backtest_results['trades']])
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=cumulative_pnl,
                    mode='lines',
                    name='Cumulative PnL',
                    line=dict(color='#10b981', width=2),
                    fill='tozeroy'
                ))
                
                fig.update_layout(
                    title="Cumulative PnL",
                    xaxis_title="Trade Number",
                    yaxis_title="Cumulative PnL",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No trades generated. Try adjusting thresholds or wait for more data.")

# Tab 4: Alerts
with tab4:
    st.markdown("## 🔔 Active Alerts")
    
    # Get recent alerts
    alerts = app.get_alerts(limit=50)
    
    if alerts:
        st.markdown(f"**{len(alerts)} alert(s) triggered**")
        
        for alert in reversed(alerts[-10:]):  # Show last 10
            severity = alert['severity']
            css_class = 'alert-warning' if severity == 'warning' else 'alert-info'
            
            st.markdown(f"""
            <div class="alert-box {css_class}">
                <strong>{alert['name']}</strong><br>
                {alert['message']}<br>
                <small>{alert['triggered_at']}</small>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Clear All Alerts"):
            app.alert_manager.clear_alerts()
            st.success("Alerts cleared!")
            st.rerun()
    else:
        st.info("No alerts triggered yet.")
    
    # Active rules
    st.markdown("### Active Alert Rules")
    rules = list(app.alert_manager.rules.values())
    
    if rules:
        rules_data = [{
            'Name': rule.name,
            'Symbols': ', '.join(rule.symbols),
            'Severity': rule.severity
        } for rule in rules]
        
        st.dataframe(pd.DataFrame(rules_data), use_container_width=True)
    else:
        st.info("No active alert rules.")

# Tab 5: Data Export
with tab5:
    st.markdown("## 📥 Data Export")
    
    export_symbol = st.selectbox("Select Symbol to Export", symbols_list)
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_days = st.slider("Days of history", 1, 30, 1)
    
    with col2:
        export_format = st.selectbox("Format", ["CSV"])
    
    if st.button("📥 Export Data"):
        start_time = datetime.now() - timedelta(days=export_days)
        
        with st.spinner("Exporting..."):
            filepath = app.export_data(export_symbol, start_time=start_time)
        
        st.success(f"Data exported to: {filepath}")
        
        # Offer download
        try:
            with open(filepath, 'rb') as f:
                st.download_button(
                    label="⬇️ Download File",
                    data=f,
                    file_name=filepath.split('/')[-1],
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Download error: {e}")
    
    st.markdown("---")
    
    # Analytics export
    st.markdown("### Export Analytics Results")
    
    if st.button("📊 Export Current Analytics"):
        analytics = app.compute_pair_analytics(symbol1, symbol2, timeframe, window_size)
        
        if 'error' not in analytics:
            # Create DataFrame with analytics
            export_data = {
                'timestamp': datetime.now().isoformat(),
                'symbol1': symbol1,
                'symbol2': symbol2,
                'hedge_ratio': analytics['regression']['beta'],
                'r_squared': analytics['regression'].get('r_squared', 0),
                'zscore': analytics['zscore_last'],
                'correlation': analytics['correlation_last'],
                'spread': analytics['spread_last']
            }
            
            df = pd.DataFrame([export_data])
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download Analytics CSV",
                data=csv,
                file_name=f"analytics_{symbol1}_{symbol2}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Auto-refresh for Tab 2
if auto_refresh and st.session_state.get('current_tab') == 'Pair Analytics':
    time.sleep(2)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <p><strong>Trading Analytics Dashboard</strong> | Real-time quantitative analytics for statistical arbitrage</p>
    <p><small>Built with Streamlit, Plotly, and Python</small></p>
</div>
""", unsafe_allow_html=True)
