"""
Main Application Orchestrator
Coordinates all backend services and provides clean API for frontend.
"""
import threading
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd

from backend.data_ingestion import DataIngestionService, TickData
from backend.storage import StorageLayer
from backend.resampling import ResamplingEngine
from backend.analytics import AnalyticsEngine
from backend.alerts import AlertManager, Alert
from backend.backtest import SimpleBacktester

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingAnalyticsApp:
    """
    Main application class that orchestrates all services.
    Designed with clean separation of concerns and extensibility.
    """
    
    def __init__(self, symbols: List[str] = None):
        """
        Initialize the trading analytics application.
        
        Args:
            symbols: Initial list of symbols to monitor
        """
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT']
        
        # Initialize core services
        self.storage = StorageLayer()
        self.resampling = ResamplingEngine(self.storage)
        self.analytics = AnalyticsEngine()
        self.alert_manager = AlertManager()
        self.backtester = SimpleBacktester()
        
        # Ingestion service (started separately)
        self.ingestion: Optional[DataIngestionService] = None
        self.ingestion_thread: Optional[threading.Thread] = None
        
        # State
        self.running = False
        
        # Setup default alerts
        self._setup_default_alerts()
        
        logger.info(f"Trading Analytics App initialized with symbols: {self.symbols}")
    
    def _setup_default_alerts(self):
        """Setup some default alert rules"""
        # Z-score alerts for BTC/ETH pair
        zscore_alert = self.alert_manager.create_zscore_rule(
            'BTCUSDT', 'ETHUSDT', threshold=2.0, severity='warning'
        )
        self.alert_manager.add_rule(zscore_alert)
        
        # Volume spike alerts
        for symbol in self.symbols:
            volume_alert = self.alert_manager.create_volume_spike_rule(
                symbol, spike_threshold=3.0, severity='info'
            )
            self.alert_manager.add_rule(volume_alert)
    
    def start_ingestion(self, symbols: List[str] = None):
        """
        Start real-time data ingestion.
        
        Args:
            symbols: Symbols to ingest (uses default if None)
        """
        if self.running:
            logger.warning("Ingestion already running")
            return
        
        symbols = symbols or self.symbols
        self.symbols = [s.upper() for s in symbols]
        
        def on_tick(tick: TickData):
            """Callback for incoming ticks"""
            self.storage.store_tick(
                tick.symbol,
                tick.timestamp,
                tick.price,
                tick.size
            )
        
        self.ingestion = DataIngestionService(symbols, on_tick)
        
        # Run in separate thread
        self.ingestion_thread = threading.Thread(
            target=self.ingestion.start,
            daemon=True
        )
        self.ingestion_thread.start()
        
        # Start resampling threads
        for timeframe in ['1s', '1m', '5m']:
            self.resampling.start_continuous_resampling(
                self.symbols, timeframe, interval_seconds=5
            )
        
        self.running = True
        logger.info(f"Started ingestion for {symbols}")
    
    def stop_ingestion(self):
        """Stop data ingestion and resampling"""
        if not self.running:
            return
        
        if self.ingestion:
            self.ingestion.stop()
        
        self.resampling.stop_all()
        
        self.running = False
        logger.info("Stopped ingestion")
    
    def get_tick_data(self, symbol: str, minutes: int = 60) -> pd.DataFrame:
        """
        Get recent tick data for a symbol.
        
        Args:
            symbol: Trading symbol
            minutes: Minutes of history to retrieve
            
        Returns:
            DataFrame with tick data
        """
        start_time = datetime.now() - timedelta(minutes=minutes)
        return self.storage.get_ticks(symbol.upper(), start_time=start_time)
    
    def get_ohlcv_data(self, symbol: str, timeframe: str, minutes: int = 60) -> pd.DataFrame:
        """
        Get OHLCV data for a symbol and timeframe.
        
        Args:
            symbol: Trading symbol
            timeframe: Timeframe ('1s', '1m', '5m', etc.)
            minutes: Minutes of history
            
        Returns:
            OHLCV DataFrame
        """
        start_time = datetime.now() - timedelta(minutes=minutes)
        return self.storage.get_resampled(symbol.upper(), timeframe, start_time=start_time)
    
    def compute_pair_analytics(self, symbol1: str, symbol2: str, 
                               timeframe: str = '1m', window: int = 20,
                               use_kalman: bool = False) -> Dict:
        """
        Compute analytics for a trading pair.
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            timeframe: Timeframe to use
            window: Rolling window size
            use_kalman: Use Kalman filter for hedge ratio
            
        Returns:
            Dictionary with all analytics results
        """
        logger.info(f"=== compute_pair_analytics called ===")
        logger.info(f"symbol1={symbol1}, symbol2={symbol2}, timeframe={timeframe}, window={window}, use_kalman={use_kalman}")
        
        try:
            # Get OHLCV data
            logger.info("Fetching OHLCV data...")
            df1 = self.get_ohlcv_data(symbol1, timeframe, minutes=120)
            df2 = self.get_ohlcv_data(symbol2, timeframe, minutes=120)
            
            logger.info(f"Analytics: {symbol1} has {len(df1)} bars, {symbol2} has {len(df2)} bars")
            
            if df1.empty or df2.empty:
                return {
                    'error': f'Insufficient data. {symbol1}: {len(df1)} bars, {symbol2}: {len(df2)} bars. Please wait for data collection or start ingestion.'
                }
            
            # Align timestamps
            df = pd.DataFrame({
                'price1': df1['close'],
                'price2': df2['close'],
                'volume1': df1['volume'],
                'volume2': df2['volume']
            }).dropna()
            
            if len(df) < window:
                return {
                    'error': f'Need at least {window} data points, got {len(df)}. Please wait for more data collection.'
                }
            
            results = {
                'symbol1': symbol1,
                'symbol2': symbol2,
                'timeframe': timeframe,
                'data_points': len(df),
                'last_update': datetime.now().isoformat()
            }
            
            # Price statistics
            results['stats1'] = self.analytics.compute_price_stats(
                pd.DataFrame({'close': df['price1']})
            )
            results['stats2'] = self.analytics.compute_price_stats(
                pd.DataFrame({'close': df['price2']})
            )
            
            # Regression (hedge ratio)
            if use_kalman:
                kalman_result = self.analytics.kalman_hedge_ratio(df['price1'], df['price2'])
                results['regression'] = {
                    'beta': kalman_result.get('last_hedge_ratio', 0),
                    'method': 'kalman'
                }
                results['kalman_hedge_ratios'] = kalman_result.get('hedge_ratios')
                hedge_ratio = kalman_result.get('last_hedge_ratio', 1)
            else:
                regression = self.analytics.ols_regression(df['price1'], df['price2'])
                results['regression'] = regression
                results['regression']['method'] = 'ols'
                hedge_ratio = regression['beta']
            
            # Spread
            spread = self.analytics.compute_spread(df['price1'], df['price2'], hedge_ratio)
            results['spread'] = spread
            results['spread_last'] = float(spread.iloc[-1]) if len(spread) > 0 else 0
            
            # Z-score
            zscore = self.analytics.compute_zscore(spread, window=window)
            results['zscore'] = zscore
            results['zscore_last'] = float(zscore.iloc[-1]) if len(zscore) > 0 else 0
            
            # ADF test on spread
            adf_result = self.analytics.adf_test(spread)
            results['adf'] = adf_result
            
            # Rolling correlation
            correlation = self.analytics.rolling_correlation(df['price1'], df['price2'], window=window)
            results['correlation'] = correlation
            results['correlation_last'] = float(correlation.iloc[-1]) if len(correlation) > 0 else 0
            
            # Half-life
            half_life = self.analytics.half_life(spread)
            results['half_life'] = half_life
            
            # Liquidity metrics
            results['liquidity1'] = self.analytics.liquidity_metrics(
                pd.DataFrame({'volume': df['volume1']}), window=window
            )
            results['liquidity2'] = self.analytics.liquidity_metrics(
                pd.DataFrame({'volume': df['volume2']}), window=window
            )
            
            # Check alerts
            alert_data = {
                'zscore': results['zscore_last'],
                'spread': results['spread_last'],
                'correlation': results['correlation_last'],
                'value': results['zscore_last']
            }
            self.alert_manager.check_all_rules(alert_data)
            
            return results
            
        except Exception as e:
            import traceback
            logger.error(f"Error computing pair analytics: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {'error': f'Computation error: {str(e)}. Check logs for details.'}
    
    def run_backtest(self, symbol1: str, symbol2: str, timeframe: str = '1m',
                    entry_threshold: float = 2.0, exit_threshold: float = 0.0) -> Dict:
        """
        Run mean-reversion backtest on a trading pair.
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            timeframe: Timeframe to use
            entry_threshold: Z-score entry threshold
            exit_threshold: Z-score exit threshold
            
        Returns:
            Backtest results
        """
        try:
            # Get analytics
            analytics = self.compute_pair_analytics(symbol1, symbol2, timeframe)
            
            if 'error' in analytics:
                return analytics
            
            spread = analytics['spread']
            zscore = analytics['zscore']
            
            if spread is None or zscore is None:
                return {'error': 'No spread/zscore data'}
            
            # Run backtest
            backtester = SimpleBacktester(
                entry_threshold=entry_threshold,
                exit_threshold=exit_threshold
            )
            
            result = backtester.run_backtest(spread, zscore)
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            return {'error': str(e)}
    
    def get_alerts(self, limit: int = 100) -> List[Dict]:
        """Get recent alerts"""
        return self.alert_manager.get_recent_alerts(limit)
    
    def add_alert_rule(self, rule_type: str, **kwargs):
        """
        Add a new alert rule.
        
        Args:
            rule_type: Type of alert ('zscore', 'price', 'spread', etc.)
            **kwargs: Rule parameters
        """
        if rule_type == 'zscore':
            rule = self.alert_manager.create_zscore_rule(**kwargs)
        elif rule_type == 'price':
            rule = self.alert_manager.create_price_threshold_rule(**kwargs)
        elif rule_type == 'spread':
            rule = self.alert_manager.create_spread_rule(**kwargs)
        elif rule_type == 'correlation':
            rule = self.alert_manager.create_correlation_rule(**kwargs)
        elif rule_type == 'volume':
            rule = self.alert_manager.create_volume_spike_rule(**kwargs)
        else:
            logger.error(f"Unknown alert type: {rule_type}")
            return
        
        self.alert_manager.add_rule(rule)
    
    def export_data(self, symbol: str, start_time: datetime = None, 
                   end_time: datetime = None) -> str:
        """
        Export tick data to CSV.
        
        Args:
            symbol: Trading symbol
            start_time: Start time (optional)
            end_time: End time (optional)
            
        Returns:
            Path to exported file
        """
        return self.storage.export_to_csv(symbol.upper(), start_time, end_time)
    
    def upload_ohlc_data(self, filepath: str, symbol: str, timeframe: str):
        """
        Upload OHLC data from CSV file.
        
        Args:
            filepath: Path to CSV file
            symbol: Symbol name
            timeframe: Timeframe of data
        """
        try:
            df = pd.read_csv(filepath)
            
            # Expected columns: timestamp, open, high, low, close, volume
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            if not all(col in df.columns for col in required_cols):
                logger.error(f"CSV must have columns: {required_cols}")
                return False
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            # Store in database
            self.storage.store_resampled(symbol.upper(), timeframe, df)
            
            logger.info(f"Uploaded {len(df)} bars for {symbol} {timeframe}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading OHLC data: {e}")
            return False
