"""
Backtesting Module
Simple mean-reversion backtest for spread trading strategies.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a single trade"""
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    position: str  # 'long' or 'short'
    pnl: float
    return_pct: float


@dataclass
class BacktestResult:
    """Backtest performance metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Trade]
    
    def to_dict(self):
        return {
            **asdict(self),
            'trades': [asdict(t) for t in self.trades]
        }


class SimpleBacktester:
    """
    Mean-reversion backtest engine for spread trading.
    Entry: Z-score crosses threshold (e.g., > 2)
    Exit: Z-score reverts (e.g., < 0)
    """
    
    def __init__(self, entry_threshold: float = 2.0, exit_threshold: float = 0.0,
                 stop_loss: float = None, take_profit: float = None):
        """
        Args:
            entry_threshold: Z-score level to enter position
            exit_threshold: Z-score level to exit position
            stop_loss: Optional stop loss (in z-score units)
            take_profit: Optional take profit (in z-score units)
        """
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
        self.stop_loss = stop_loss
        self.take_profit = take_profit
    
    def run_backtest(self, spread_series: pd.Series, zscore_series: pd.Series) -> BacktestResult:
        """
        Run backtest on spread and z-score data.
        
        Args:
            spread_series: Spread time series
            zscore_series: Z-score time series
            
        Returns:
            BacktestResult with performance metrics
        """
        if len(spread_series) < 10 or len(zscore_series) < 10:
            return BacktestResult(0, 0, 0, 0, 0, 0, 0, 0, [])
        
        trades: List[Trade] = []
        position = None  # None, 'long', or 'short'
        entry_zscore = 0
        entry_spread = 0
        entry_time = None
        
        df = pd.DataFrame({
            'spread': spread_series,
            'zscore': zscore_series
        }).dropna()
        
        if df.empty:
            return BacktestResult(0, 0, 0, 0, 0, 0, 0, 0, [])
        
        for idx, row in df.iterrows():
            zscore = row['zscore']
            spread = row['spread']
            
            # Entry logic
            if position is None:
                if zscore > self.entry_threshold:
                    # Enter short (expect spread to revert down)
                    position = 'short'
                    entry_zscore = zscore
                    entry_spread = spread
                    entry_time = idx
                
                elif zscore < -self.entry_threshold:
                    # Enter long (expect spread to revert up)
                    position = 'long'
                    entry_zscore = zscore
                    entry_spread = spread
                    entry_time = idx
            
            # Exit logic
            elif position is not None:
                should_exit = False
                
                # Mean reversion exit
                if position == 'short' and zscore < self.exit_threshold:
                    should_exit = True
                elif position == 'long' and zscore > -self.exit_threshold:
                    should_exit = True
                
                # Stop loss
                if self.stop_loss:
                    if position == 'short' and zscore > entry_zscore + self.stop_loss:
                        should_exit = True
                    elif position == 'long' and zscore < entry_zscore - self.stop_loss:
                        should_exit = True
                
                # Take profit
                if self.take_profit:
                    if position == 'short' and zscore < entry_zscore - self.take_profit:
                        should_exit = True
                    elif position == 'long' and zscore > entry_zscore + self.take_profit:
                        should_exit = True
                
                if should_exit:
                    # Calculate PnL
                    if position == 'short':
                        pnl = entry_spread - spread
                    else:  # long
                        pnl = spread - entry_spread
                    
                    return_pct = (pnl / abs(entry_spread)) * 100 if entry_spread != 0 else 0
                    
                    trade = Trade(
                        entry_time=str(entry_time),
                        exit_time=str(idx),
                        entry_price=entry_spread,
                        exit_price=spread,
                        position=position,
                        pnl=pnl,
                        return_pct=return_pct
                    )
                    trades.append(trade)
                    
                    # Reset position
                    position = None
        
        # Calculate performance metrics
        if not trades:
            return BacktestResult(0, 0, 0, 0, 0, 0, 0, 0, [])
        
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl > 0)
        losing_trades = sum(1 for t in trades if t.pnl < 0)
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in trades)
        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        # Drawdown calculation
        cumulative_pnl = np.cumsum([t.pnl for t in trades])
        running_max = np.maximum.accumulate(cumulative_pnl)
        drawdown = running_max - cumulative_pnl
        max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
        
        # Sharpe ratio (annualized, assuming daily data)
        returns = [t.return_pct for t in trades]
        sharpe_ratio = 0
        if len(returns) > 1:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            if std_return > 0:
                sharpe_ratio = (mean_return / std_return) * np.sqrt(252)  # Annualized
        
        return BacktestResult(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_pnl=total_pnl,
            avg_pnl=avg_pnl,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trades=trades
        )
