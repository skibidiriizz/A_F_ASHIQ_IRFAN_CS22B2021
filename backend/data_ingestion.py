"""
Data Ingestion Module
Handles WebSocket connections to Binance and real-time tick data streaming.
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Callable, List, Optional
import websockets
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TickData:
    """Normalized tick data structure"""
    symbol: str
    timestamp: datetime
    price: float
    size: float
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'size': self.size
        }


class BinanceWebSocketClient:
    """
    WebSocket client for Binance Futures market data.
    Designed for extensibility - can be swapped with other data sources.
    """
    
    def __init__(self, symbols: List[str], on_tick: Callable[[TickData], None]):
        """
        Args:
            symbols: List of trading symbols (e.g., ['btcusdt', 'ethusdt'])
            on_tick: Callback function to handle incoming tick data
        """
        self.symbols = [s.lower() for s in symbols]
        self.on_tick = on_tick
        self.connections = []
        self.running = False
        
    async def connect_symbol(self, symbol: str):
        """Connect to WebSocket stream for a single symbol"""
        url = f"wss://fstream.binance.com/ws/{symbol}@trade"
        
        try:
            async with websockets.connect(url, ping_interval=20) as ws:
                logger.info(f"Connected to {symbol} stream")
                self.connections.append(ws)
                
                async for message in ws:
                    if not self.running:
                        break
                        
                    try:
                        data = json.loads(message)
                        if data.get('e') == 'trade':
                            tick = TickData(
                                symbol=data['s'],
                                timestamp=datetime.fromtimestamp(data['T'] / 1000),
                                price=float(data['p']),
                                size=float(data['q'])
                            )
                            self.on_tick(tick)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket error for {symbol}: {e}")
        finally:
            logger.info(f"Disconnected from {symbol}")
    
    async def start(self):
        """Start all WebSocket connections"""
        self.running = True
        tasks = [self.connect_symbol(symbol) for symbol in self.symbols]
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def stop(self):
        """Stop all connections"""
        self.running = False
        logger.info("Stopping all WebSocket connections")


class DataIngestionService:
    """
    Main ingestion service that coordinates data collection and storage.
    Follows single responsibility principle - only handles ingestion logic.
    """
    
    def __init__(self, symbols: List[str], storage_callback: Callable[[TickData], None]):
        """
        Args:
            symbols: Trading symbols to monitor
            storage_callback: Function to store incoming ticks
        """
        self.symbols = symbols
        self.storage_callback = storage_callback
        self.ws_client: Optional[BinanceWebSocketClient] = None
        self.task: Optional[asyncio.Task] = None
        
    def on_tick_received(self, tick: TickData):
        """Handle incoming tick data"""
        try:
            self.storage_callback(tick)
            logger.debug(f"Stored tick: {tick.symbol} @ {tick.price}")
        except Exception as e:
            logger.error(f"Error storing tick: {e}")
    
    async def start_async(self):
        """Start ingestion service asynchronously"""
        self.ws_client = BinanceWebSocketClient(self.symbols, self.on_tick_received)
        logger.info(f"Starting ingestion for symbols: {self.symbols}")
        await self.ws_client.start()
    
    def start(self):
        """Start ingestion service in new event loop"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.start_async())
        finally:
            loop.close()
    
    def stop(self):
        """Stop ingestion service"""
        if self.ws_client:
            self.ws_client.stop()
        logger.info("Ingestion service stopped")
