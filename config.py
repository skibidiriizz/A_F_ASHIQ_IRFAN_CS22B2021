"""
Configuration File
Centralized settings for the trading analytics platform.
"""
import os

class Config:
    """Application configuration"""
    
    # Application
    APP_NAME = "Trading Analytics Platform"
    VERSION = "1.0.0"
    
    # Data Storage
    DATA_DIR = "data"
    DB_PATH = os.path.join(DATA_DIR, "ticks.db")
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # WebSocket Configuration
    BINANCE_WS_BASE = "wss://fstream.binance.com/ws"
    WS_PING_INTERVAL = 20
    WS_TIMEOUT = 30
    
    # Default Symbols
    DEFAULT_SYMBOLS = ['BTCUSDT', 'ETHUSDT']
    
    # Resampling Configuration
    TIMEFRAMES = {
        '1s': '1S',
        '1m': '1T',
        '5m': '5T',
        '15m': '15T',
        '1h': '1H'
    }
    RESAMPLING_INTERVAL = 5  # seconds
    
    # Analytics Configuration
    DEFAULT_WINDOW = 20
    DEFAULT_LOOKBACK_MINUTES = 120
    ZSCORE_THRESHOLD = 2.0
    
    # Alert Configuration
    ALERT_COOLDOWN = 60  # seconds
    MAX_ALERTS = 1000
    
    # Backtest Configuration
    DEFAULT_ENTRY_THRESHOLD = 2.0
    DEFAULT_EXIT_THRESHOLD = 0.0
    
    # Storage Limits
    MAX_TICKS_REDIS = 10000  # per symbol
    MAX_TICKS_QUERY = 100000
    REDIS_CACHE_TTL = 300  # seconds
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Export Configuration
    EXPORT_DIR = os.path.join(DATA_DIR, "exports")
    
    # Performance
    TICK_BUFFER_SIZE = 1000
    ANALYTICS_CACHE_SIZE = 100
    
    @classmethod
    def create_directories(cls):
        """Create necessary directories"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.EXPORT_DIR, exist_ok=True)
    
    @classmethod
    def get_db_path(cls):
        """Get database path"""
        cls.create_directories()
        return cls.DB_PATH


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    RESAMPLING_INTERVAL = 2  # faster updates for development


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    WS_TIMEOUT = 60
    TICK_BUFFER_SIZE = 5000


# Select configuration based on environment
ENV = os.getenv("ENV", "development").lower()

if ENV == "production":
    config = ProductionConfig()
else:
    config = DevelopmentConfig()
