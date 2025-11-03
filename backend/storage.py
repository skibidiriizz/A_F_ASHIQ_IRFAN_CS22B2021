"""
Storage Module
Handles persistence of tick data using SQLite for durability and Redis for real-time access.
"""
import sqlite3
import json
import redis
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging
from threading import Lock
import os

logger = logging.getLogger(__name__)


class StorageLayer:
    """
    Hybrid storage strategy:
    - SQLite: Durable storage for all tick data
    - Redis: Fast in-memory cache for recent data and resampled OHLCV
    
    Design allows easy swapping of storage backends (e.g., TimescaleDB, InfluxDB)
    """
    
    def __init__(self, db_path: str = "data/ticks.db", redis_host: str = "localhost", redis_port: int = 6379):
        self.db_path = db_path
        self.lock = Lock()
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize SQLite
        self._init_sqlite()
        
        # Initialize Redis (optional - graceful fallback if not available)
        try:
            self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Using SQLite only.")
            self.redis_client = None
            self.use_redis = False
    
    def _init_sqlite(self):
        """Initialize SQLite database with proper schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tick data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ticks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    price REAL NOT NULL,
                    size REAL NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for fast queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
                ON ticks(symbol, timestamp)
            """)
            
            # Resampled data table (OHLCV)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resampled_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume REAL NOT NULL,
                    num_trades INTEGER,
                    UNIQUE(symbol, timeframe, timestamp)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_resampled 
                ON resampled_data(symbol, timeframe, timestamp)
            """)
            
            conn.commit()
            logger.info(f"SQLite database initialized at {self.db_path}")
    
    def store_tick(self, symbol: str, timestamp: datetime, price: float, size: float):
        """Store a single tick to both SQLite and Redis"""
        with self.lock:
            # SQLite storage
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO ticks (symbol, timestamp, price, size) VALUES (?, ?, ?, ?)",
                    (symbol, timestamp.isoformat(), price, size)
                )
                conn.commit()
            
            # Redis cache (recent ticks only - keep last 10000 per symbol)
            if self.use_redis:
                try:
                    tick_data = json.dumps({
                        'timestamp': timestamp.isoformat(),
                        'price': price,
                        'size': size
                    })
                    
                    # Use sorted set with timestamp as score for ordered retrieval
                    key = f"ticks:{symbol}"
                    self.redis_client.zadd(key, {tick_data: timestamp.timestamp()})
                    
                    # Keep only recent ticks (memory management)
                    self.redis_client.zremrangebyrank(key, 0, -10001)
                except Exception as e:
                    logger.error(f"Redis error: {e}")
    
    def get_ticks(self, symbol: str, start_time: Optional[datetime] = None, 
                  end_time: Optional[datetime] = None, limit: int = 10000) -> pd.DataFrame:
        """Retrieve ticks from storage"""
        query = "SELECT timestamp, price, size FROM ticks WHERE symbol = ?"
        params = [symbol]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
            df = df.sort_values('timestamp')
        
        return df
    
    def get_recent_ticks_redis(self, symbol: str, seconds: int = 60) -> pd.DataFrame:
        """Get recent ticks from Redis (faster for real-time queries)"""
        if not self.use_redis:
            return self.get_ticks(symbol, start_time=datetime.now() - timedelta(seconds=seconds))
        
        try:
            key = f"ticks:{symbol}"
            cutoff = (datetime.now() - timedelta(seconds=seconds)).timestamp()
            
            # Get ticks from sorted set
            ticks = self.redis_client.zrangebyscore(key, cutoff, '+inf')
            
            if not ticks:
                return pd.DataFrame(columns=['timestamp', 'price', 'size'])
            
            data = []
            for tick_json in ticks:
                tick = json.loads(tick_json)
                data.append(tick)
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
            return df.sort_values('timestamp')
            
        except Exception as e:
            logger.error(f"Redis query error: {e}")
            return self.get_ticks(symbol, start_time=datetime.now() - timedelta(seconds=seconds))
    
    def store_resampled(self, symbol: str, timeframe: str, df: pd.DataFrame):
        """Store resampled OHLCV data"""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                for idx, row in df.iterrows():
                    try:
                        conn.execute("""
                            INSERT OR REPLACE INTO resampled_data 
                            (symbol, timeframe, timestamp, open, high, low, close, volume, num_trades)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            symbol, timeframe, idx.isoformat(),
                            row['open'], row['high'], row['low'], row['close'],
                            row['volume'], row.get('num_trades', 0)
                        ))
                    except Exception as e:
                        logger.error(f"Error storing resampled data: {e}")
                
                conn.commit()
        
        # Also cache in Redis
        if self.use_redis:
            try:
                key = f"ohlcv:{symbol}:{timeframe}"
                self.redis_client.set(key, df.to_json(), ex=300)  # 5 min expiry
            except Exception as e:
                logger.error(f"Redis cache error: {e}")
    
    def get_resampled(self, symbol: str, timeframe: str, 
                     start_time: Optional[datetime] = None) -> pd.DataFrame:
        """Retrieve resampled OHLCV data"""
        query = """
            SELECT timestamp, open, high, low, close, volume, num_trades
            FROM resampled_data 
            WHERE symbol = ? AND timeframe = ?
        """
        params = [symbol, timeframe]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        query += " ORDER BY timestamp"
        
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
            df = df.set_index('timestamp')
        
        return df
    
    def get_all_symbols(self) -> List[str]:
        """Get list of all symbols in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT symbol FROM ticks")
            return [row[0] for row in cursor.fetchall()]
    
    def export_to_csv(self, symbol: str, start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None, filename: str = None) -> str:
        """Export tick data to CSV file"""
        df = self.get_ticks(symbol, start_time, end_time, limit=1000000)
        
        if filename is None:
            filename = f"data/export_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df.to_csv(filename, index=False)
        logger.info(f"Exported {len(df)} ticks to {filename}")
        return filename
