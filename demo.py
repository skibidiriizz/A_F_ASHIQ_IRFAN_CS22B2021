"""
Demo/Test Script
Demonstrates core functionality without frontend.
"""
import time
import sys
from datetime import datetime
from app import TradingAnalyticsApp

def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def demo_analytics():
    """Demo analytics computation"""
    print_header("🚀 Trading Analytics Platform - Demo")
    
    # Initialize app
    print("\n[1/5] Initializing application...")
    app = TradingAnalyticsApp(['BTCUSDT', 'ETHUSDT'])
    print("✓ App initialized")
    
    # Start ingestion
    print("\n[2/5] Starting data ingestion...")
    app.start_ingestion()
    print("✓ WebSocket connections established")
    print("  ⏳ Collecting data (please wait 60 seconds)...")
    
    # Wait for data collection
    for i in range(60, 0, -10):
        print(f"     {i} seconds remaining...", end='\r')
        time.sleep(10)
    print("\n✓ Data collection complete")
    
    # Get tick data
    print("\n[3/5] Retrieving tick data...")
    btc_ticks = app.get_tick_data('BTCUSDT', minutes=5)
    eth_ticks = app.get_tick_data('ETHUSDT', minutes=5)
    print(f"✓ Retrieved {len(btc_ticks)} BTC ticks, {len(eth_ticks)} ETH ticks")
    
    if len(btc_ticks) > 0:
        print(f"\n  Latest BTC price: ${btc_ticks['price'].iloc[-1]:,.2f}")
        print(f"  Latest ETH price: ${eth_ticks['price'].iloc[-1]:,.2f}")
    
    # Get OHLCV data
    print("\n[4/5] Getting resampled OHLCV data...")
    btc_ohlcv = app.get_ohlcv_data('BTCUSDT', '1m', minutes=10)
    eth_ohlcv = app.get_ohlcv_data('ETHUSDT', '1m', minutes=10)
    print(f"✓ Retrieved {len(btc_ohlcv)} BTC bars, {len(eth_ohlcv)} ETH bars")
    
    # Compute pair analytics
    print("\n[5/5] Computing pair analytics...")
    analytics = app.compute_pair_analytics('BTCUSDT', 'ETHUSDT', timeframe='1m', window=20)
    
    if 'error' in analytics:
        print(f"⚠️  Error: {analytics['error']}")
        print("\n💡 Tip: Wait longer for more data or check WebSocket connection")
    else:
        print("✓ Analytics computed successfully!")
        
        print_header("📊 Analytics Results")
        
        print(f"\n📈 Regression:")
        print(f"  Hedge Ratio (β): {analytics['regression']['beta']:.4f}")
        print(f"  R-squared: {analytics['regression'].get('r_squared', 0):.4f}")
        print(f"  Method: {analytics['regression'].get('method', 'ols').upper()}")
        
        print(f"\n📉 Spread Analysis:")
        print(f"  Current Spread: {analytics['spread_last']:.2f}")
        print(f"  Z-Score: {analytics['zscore_last']:.2f}")
        
        if abs(analytics['zscore_last']) > 2:
            print(f"  ⚠️  Trading Signal: Z-score exceeds threshold!")
        else:
            print(f"  ✓ Normal range")
        
        print(f"\n🔗 Correlation:")
        print(f"  Current: {analytics['correlation_last']:.3f}")
        
        print(f"\n📊 Stationarity Test (ADF):")
        adf = analytics['adf']
        print(f"  P-value: {adf.get('pvalue', 1):.4f}")
        print(f"  Stationary: {'✓ Yes' if adf.get('is_stationary', False) else '✗ No'}")
        
        print(f"\n⏱️  Mean Reversion:")
        half_life = analytics.get('half_life', float('nan'))
        if half_life == half_life:  # Check not NaN
            print(f"  Half-life: {half_life:.2f} bars")
        else:
            print(f"  Half-life: N/A (need more data)")
    
    # Demonstrate alerts
    print_header("🔔 Alert System")
    
    # Add custom alert
    print("\nAdding custom z-score alert...")
    app.add_alert_rule('zscore', symbol1='BTCUSDT', symbol2='ETHUSDT', 
                      threshold=1.5, severity='warning')
    print("✓ Alert rule added")
    
    alerts = app.get_alerts()
    if alerts:
        print(f"\n📢 {len(alerts)} alert(s) triggered:")
        for alert in alerts[-3:]:  # Show last 3
            print(f"  - {alert['name']}: {alert['message']}")
    else:
        print("\n  No alerts triggered yet")
    
    # Demonstrate export
    print_header("📥 Data Export")
    
    print("\nExporting BTC tick data...")
    export_path = app.export_data('BTCUSDT')
    print(f"✓ Data exported to: {export_path}")
    
    # Stop ingestion
    print("\n" + "-"*60)
    print("Stopping data ingestion...")
    app.stop_ingestion()
    print("✓ Stopped")
    
    print_header("✅ Demo Complete!")
    print("\nNext steps:")
    print("  1. Run 'streamlit run frontend.py' for full dashboard")
    print("  2. Check README.md for detailed documentation")
    print("  3. Explore exported data in the 'data/' directory")
    print("\n")

def quick_test():
    """Quick functionality test"""
    print("Running quick functionality test...")
    
    try:
        # Test imports
        from backend import (
            DataIngestionService, StorageLayer, ResamplingEngine,
            AnalyticsEngine, AlertManager, SimpleBacktester
        )
        print("✓ All imports successful")
        
        # Test analytics functions
        import pandas as pd
        import numpy as np
        
        # Generate dummy data
        dates = pd.date_range('2024-01-01', periods=100, freq='1min')
        price1 = pd.Series(np.random.randn(100).cumsum() + 50000, index=dates)
        price2 = pd.Series(np.random.randn(100).cumsum() + 3000, index=dates)
        
        analytics = AnalyticsEngine()
        
        # Test regression
        regression = analytics.ols_regression(price1, price2)
        print(f"✓ OLS regression: β={regression['beta']:.4f}, R²={regression['r_squared']:.4f}")
        
        # Test spread and z-score
        spread = analytics.compute_spread(price1, price2, regression['beta'])
        zscore = analytics.compute_zscore(spread, window=20)
        print(f"✓ Spread & Z-score computed: {len(spread)} points")
        
        # Test ADF
        adf = analytics.adf_test(spread)
        print(f"✓ ADF test: p-value={adf['pvalue']:.4f}")
        
        # Test correlation
        corr = analytics.rolling_correlation(price1, price2, window=20)
        print(f"✓ Rolling correlation computed")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        quick_test()
    else:
        try:
            demo_analytics()
        except KeyboardInterrupt:
            print("\n\n⏹️  Demo interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
