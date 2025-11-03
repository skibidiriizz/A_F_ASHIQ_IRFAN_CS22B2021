"""
Backend Package
Modular components for trading analytics platform.
"""

__version__ = "1.0.0"
__author__ = "Trading Analytics Team"

from .data_ingestion import DataIngestionService, TickData, BinanceWebSocketClient
from .storage import StorageLayer
from .resampling import ResamplingEngine
from .analytics import AnalyticsEngine
from .alerts import AlertManager, Alert, AlertRule
from .backtest import SimpleBacktester, BacktestResult

__all__ = [
    'DataIngestionService',
    'TickData',
    'BinanceWebSocketClient',
    'StorageLayer',
    'ResamplingEngine',
    'AnalyticsEngine',
    'AlertManager',
    'Alert',
    'AlertRule',
    'SimpleBacktester',
    'BacktestResult'
]
