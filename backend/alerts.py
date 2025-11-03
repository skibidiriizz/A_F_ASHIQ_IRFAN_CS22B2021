"""
Alert System
Configurable rule-based alerts for trading signals.
"""
import pandas as pd
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


@dataclass
class Alert:
    """Alert data structure"""
    id: str
    name: str
    condition: str  # e.g., "zscore > 2"
    symbols: List[str]
    triggered_at: datetime
    value: float
    message: str
    severity: str = "info"  # info, warning, critical
    
    def to_dict(self):
        return {
            **asdict(self),
            'triggered_at': self.triggered_at.isoformat()
        }


class AlertRule:
    """
    Defines a single alert rule with condition checking logic.
    """
    
    def __init__(self, rule_id: str, name: str, symbols: List[str], 
                 condition_fn: Callable[[Dict], bool], 
                 message_fn: Callable[[Dict], str],
                 severity: str = "info"):
        """
        Args:
            rule_id: Unique identifier
            name: Human-readable name
            symbols: Symbols to monitor
            condition_fn: Function that returns True if alert should trigger
            message_fn: Function that generates alert message
            severity: Alert severity level
        """
        self.rule_id = rule_id
        self.name = name
        self.symbols = symbols
        self.condition_fn = condition_fn
        self.message_fn = message_fn
        self.severity = severity
        self.last_trigger = None
        self.cooldown_seconds = 60  # Prevent alert spam
    
    def check(self, data: Dict) -> Alert:
        """
        Check if alert condition is met.
        
        Args:
            data: Dictionary with analytics data
            
        Returns:
            Alert object if triggered, None otherwise
        """
        try:
            # Cooldown check
            if self.last_trigger:
                elapsed = (datetime.now() - self.last_trigger).total_seconds()
                if elapsed < self.cooldown_seconds:
                    return None
            
            # Evaluate condition
            if self.condition_fn(data):
                alert = Alert(
                    id=f"{self.rule_id}_{datetime.now().timestamp()}",
                    name=self.name,
                    condition=self.rule_id,
                    symbols=self.symbols,
                    triggered_at=datetime.now(),
                    value=data.get('value', 0),
                    message=self.message_fn(data),
                    severity=self.severity
                )
                self.last_trigger = datetime.now()
                return alert
            
            return None
        
        except Exception as e:
            logger.error(f"Error checking alert rule {self.rule_id}: {e}")
            return None


class AlertManager:
    """
    Manages alert rules and triggered alerts.
    Extensible design allows adding custom rules easily.
    """
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self.triggered_alerts: List[Alert] = []
        self.alert_callbacks: List[Callable[[Alert], None]] = []
    
    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove an alert rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
    
    def add_callback(self, callback: Callable[[Alert], None]):
        """Add callback function to be called when alert triggers"""
        self.alert_callbacks.append(callback)
    
    def check_all_rules(self, analytics_data: Dict):
        """
        Check all rules against current analytics data.
        
        Args:
            analytics_data: Dictionary with all analytics results
        """
        for rule in self.rules.values():
            alert = rule.check(analytics_data)
            
            if alert:
                self.triggered_alerts.append(alert)
                logger.info(f"Alert triggered: {alert.name} - {alert.message}")
                
                # Execute callbacks
                for callback in self.alert_callbacks:
                    try:
                        callback(alert)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")
    
    def get_recent_alerts(self, limit: int = 100) -> List[Dict]:
        """Get recent triggered alerts"""
        return [alert.to_dict() for alert in self.triggered_alerts[-limit:]]
    
    def clear_alerts(self):
        """Clear all triggered alerts"""
        self.triggered_alerts.clear()
        logger.info("Cleared all alerts")
    
    @staticmethod
    def create_zscore_rule(symbol1: str, symbol2: str, threshold: float = 2.0, 
                          severity: str = "warning") -> AlertRule:
        """
        Factory method: Create a z-score threshold alert.
        
        Args:
            symbol1, symbol2: Trading pair
            threshold: Z-score threshold
            severity: Alert severity
            
        Returns:
            AlertRule instance
        """
        def condition(data: Dict) -> bool:
            zscore = data.get('zscore', 0)
            return abs(zscore) > threshold
        
        def message(data: Dict) -> str:
            zscore = data.get('zscore', 0)
            return f"Z-score {zscore:.2f} exceeded threshold {threshold} for {symbol1}/{symbol2}"
        
        return AlertRule(
            rule_id=f"zscore_{symbol1}_{symbol2}_{threshold}",
            name=f"Z-Score Alert ({symbol1}/{symbol2})",
            symbols=[symbol1, symbol2],
            condition_fn=condition,
            message_fn=message,
            severity=severity
        )
    
    @staticmethod
    def create_price_threshold_rule(symbol: str, threshold: float, 
                                   direction: str = "above", severity: str = "info") -> AlertRule:
        """
        Factory method: Create a price threshold alert.
        
        Args:
            symbol: Trading symbol
            threshold: Price threshold
            direction: 'above' or 'below'
            severity: Alert severity
            
        Returns:
            AlertRule instance
        """
        def condition(data: Dict) -> bool:
            price = data.get('price', 0)
            if direction == "above":
                return price > threshold
            else:
                return price < threshold
        
        def message(data: Dict) -> str:
            price = data.get('price', 0)
            return f"{symbol} price {price:.2f} is {direction} threshold {threshold}"
        
        return AlertRule(
            rule_id=f"price_{symbol}_{direction}_{threshold}",
            name=f"Price {direction.capitalize()} ({symbol})",
            symbols=[symbol],
            condition_fn=condition,
            message_fn=message,
            severity=severity
        )
    
    @staticmethod
    def create_spread_rule(symbol1: str, symbol2: str, threshold: float, 
                          severity: str = "warning") -> AlertRule:
        """
        Factory method: Create a spread threshold alert.
        
        Args:
            symbol1, symbol2: Trading pair
            threshold: Spread threshold
            severity: Alert severity
            
        Returns:
            AlertRule instance
        """
        def condition(data: Dict) -> bool:
            spread = data.get('spread', 0)
            return abs(spread) > threshold
        
        def message(data: Dict) -> str:
            spread = data.get('spread', 0)
            return f"Spread {spread:.2f} exceeded threshold {threshold} for {symbol1}/{symbol2}"
        
        return AlertRule(
            rule_id=f"spread_{symbol1}_{symbol2}_{threshold}",
            name=f"Spread Alert ({symbol1}/{symbol2})",
            symbols=[symbol1, symbol2],
            condition_fn=condition,
            message_fn=message,
            severity=severity
        )
    
    @staticmethod
    def create_correlation_rule(symbol1: str, symbol2: str, min_correlation: float = 0.5,
                               severity: str = "info") -> AlertRule:
        """
        Factory method: Alert when correlation drops below threshold.
        
        Args:
            symbol1, symbol2: Trading pair
            min_correlation: Minimum acceptable correlation
            severity: Alert severity
            
        Returns:
            AlertRule instance
        """
        def condition(data: Dict) -> bool:
            corr = data.get('correlation', 1)
            return corr < min_correlation
        
        def message(data: Dict) -> str:
            corr = data.get('correlation', 0)
            return f"Correlation {corr:.3f} dropped below {min_correlation} for {symbol1}/{symbol2}"
        
        return AlertRule(
            rule_id=f"correlation_{symbol1}_{symbol2}_{min_correlation}",
            name=f"Correlation Alert ({symbol1}/{symbol2})",
            symbols=[symbol1, symbol2],
            condition_fn=condition,
            message_fn=message,
            severity=severity
        )
    
    @staticmethod
    def create_volume_spike_rule(symbol: str, spike_threshold: float = 3.0,
                                severity: str = "info") -> AlertRule:
        """
        Factory method: Alert on volume spikes (relative to average).
        
        Args:
            symbol: Trading symbol
            spike_threshold: Multiple of average volume
            severity: Alert severity
            
        Returns:
            AlertRule instance
        """
        def condition(data: Dict) -> bool:
            current_volume = data.get('current_volume', 0)
            avg_volume = data.get('avg_volume', 0)
            if avg_volume == 0:
                return False
            return current_volume > avg_volume * spike_threshold
        
        def message(data: Dict) -> str:
            current_volume = data.get('current_volume', 0)
            avg_volume = data.get('avg_volume', 0)
            ratio = current_volume / avg_volume if avg_volume > 0 else 0
            return f"{symbol} volume spike: {ratio:.1f}x average ({current_volume:.0f} vs {avg_volume:.0f})"
        
        return AlertRule(
            rule_id=f"volume_spike_{symbol}_{spike_threshold}",
            name=f"Volume Spike ({symbol})",
            symbols=[symbol],
            condition_fn=condition,
            message_fn=message,
            severity=severity
        )
