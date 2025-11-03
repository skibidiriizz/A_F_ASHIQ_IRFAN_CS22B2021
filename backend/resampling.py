"""
Resampling Module
Converts tick data into OHLCV bars at different timeframes.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from threading import Thread, Event
import time

logger = logging.getLogger(__name__)


class ResamplingEngine:
    """
    Resamples tick data into OHLCV bars at configurable intervals.
    Designed to be extensible for different aggregation strategies.
    """
    
    TIMEFRAMES = {
        '1s': '1S',
        '1m': '1T',
        '5m': '5T',
        '15m': '15T',
        '1h': '1H'
    }
    
    def __init__(self, storage_layer):
        """
        Args:
            storage_layer: Storage instance for data access
        """
        self.storage = storage_layer
        self.running = False
        self.resampling_threads: Dict[str, Thread] = {}
        self.stop_events: Dict[str, Event] = {}
    
    @staticmethod
    def resample_ticks_to_ohlcv(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """
        Convert tick data to OHLCV bars.
        
        Args:
            df: DataFrame with columns [timestamp, price, size]
            timeframe: Pandas frequency string (e.g., '1T', '5T')
            
        Returns:
            OHLCV DataFrame
        """
        if df.empty:
            return pd.DataFrame(columns=['open', 'high', 'low', 'close', 'volume', 'num_trades'])
        
        df = df.set_index('timestamp')
        
        ohlcv = pd.DataFrame()
        ohlcv['open'] = df['price'].resample(timeframe).first()
        ohlcv['high'] = df['price'].resample(timeframe).max()
        ohlcv['low'] = df['price'].resample(timeframe).min()
        ohlcv['close'] = df['price'].resample(timeframe).last()
        ohlcv['volume'] = df['size'].resample(timeframe).sum()
        ohlcv['num_trades'] = df['price'].resample(timeframe).count()
        
        # Remove incomplete bars and NaN values
        ohlcv = ohlcv.dropna()
        
        return ohlcv
    
    def resample_symbol(self, symbol: str, timeframe_key: str, lookback_minutes: int = 60):
        """
        Resample recent ticks for a symbol and store results.
        
        Args:
            symbol: Trading symbol
            timeframe_key: Timeframe key ('1s', '1m', '5m', etc.)
            lookback_minutes: How far back to look for ticks
        """
        try:
            timeframe = self.TIMEFRAMES.get(timeframe_key, '1T')
            
            # Get recent ticks
            start_time = datetime.now() - timedelta(minutes=lookback_minutes)
            df = self.storage.get_ticks(symbol, start_time=start_time)
            
            if df.empty or len(df) < 2:
                logger.debug(f"Insufficient data for {symbol} {timeframe_key}")
                return
            
            # Resample to OHLCV
            ohlcv = self.resample_ticks_to_ohlcv(df, timeframe)
            
            if not ohlcv.empty:
                # Store resampled data
                self.storage.store_resampled(symbol, timeframe_key, ohlcv)
                logger.debug(f"Resampled {symbol} {timeframe_key}: {len(ohlcv)} bars")
        
        except Exception as e:
            logger.error(f"Error resampling {symbol} {timeframe_key}: {e}")
    
    def start_continuous_resampling(self, symbols: List[str], timeframe_key: str, interval_seconds: int = 5):
        """
        Start a background thread that continuously resamples data.
        
        Args:
            symbols: List of symbols to resample
            timeframe_key: Timeframe to resample to
            interval_seconds: How often to run resampling
        """
        thread_key = f"{','.join(symbols)}_{timeframe_key}"
        
        if thread_key in self.resampling_threads and self.resampling_threads[thread_key].is_alive():
            logger.warning(f"Resampling thread already running for {thread_key}")
            return
        
        stop_event = Event()
        self.stop_events[thread_key] = stop_event
        
        def resampling_loop():
            logger.info(f"Started resampling thread: {thread_key}")
            
            while not stop_event.is_set():
                for symbol in symbols:
                    if stop_event.is_set():
                        break
                    self.resample_symbol(symbol, timeframe_key)
                
                # Sleep in small intervals to allow quick stopping
                for _ in range(interval_seconds * 10):
                    if stop_event.is_set():
                        break
                    time.sleep(0.1)
            
            logger.info(f"Stopped resampling thread: {thread_key}")
        
        thread = Thread(target=resampling_loop, daemon=True)
        thread.start()
        self.resampling_threads[thread_key] = thread
    
    def stop_all(self):
        """Stop all resampling threads"""
        for stop_event in self.stop_events.values():
            stop_event.set()
        
        for thread in self.resampling_threads.values():
            thread.join(timeout=2)
        
        self.resampling_threads.clear()
        self.stop_events.clear()
        logger.info("All resampling threads stopped")
