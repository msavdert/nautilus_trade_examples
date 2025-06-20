"""
Utility functions and classes for the Binance Futures Testnet Bot.

This module provides common utility functions used throughout the bot:
- Logging setup and management
- Data formatting and conversion
- Performance monitoring
- Error handling helpers
- Math and statistical utilities
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pathlib import Path
from dataclasses import dataclass
import json

import numpy as np
import pandas as pd


@dataclass
class PerformanceStats:
    """Performance statistics for monitoring."""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_win: float = 0.0
    max_loss: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0


class LoggingUtils:
    """Utility functions for logging setup and management."""
    
    @staticmethod
    def setup_logger(name: str, 
                    level: str = "INFO", 
                    log_dir: Optional[Path] = None) -> logging.Logger:
        """
        Setup a logger with console and file handlers.
        
        Args:
            name: Logger name
            level: Logging level
            log_dir: Directory for log files
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        # Don't add handlers if already configured
        if logger.handlers:
            return logger
        
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)-20s | %(levelname)-8s | %(funcName)-15s | %(message)s'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        if log_dir:
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def log_dict(logger: logging.Logger, data: Dict[str, Any], title: str = "Data") -> None:
        """
        Log a dictionary in a formatted way.
        
        Args:
            logger: Logger instance
            data: Dictionary to log
            title: Title for the log entry
        """
        logger.info(f"=== {title} ===")
        for key, value in data.items():
            if isinstance(value, float):
                logger.info(f"  {key}: {value:.4f}")
            else:
                logger.info(f"  {key}: {value}")


class DataUtils:
    """Utility functions for data processing and conversion."""
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Float value or default
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """
        Safely convert value to int.
        
        Args:
            value: Value to convert
            default: Default value if conversion fails
            
        Returns:
            Integer value or default
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def format_currency(amount: float, symbol: str = "$") -> str:
        """
        Format currency amount.
        
        Args:
            amount: Amount to format
            symbol: Currency symbol
            
        Returns:
            Formatted currency string
        """
        if abs(amount) >= 1_000_000:
            return f"{symbol}{amount/1_000_000:.2f}M"
        elif abs(amount) >= 1_000:
            return f"{symbol}{amount/1_000:.2f}K"
        else:
            return f"{symbol}{amount:.2f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """
        Format percentage value.
        
        Args:
            value: Percentage value (0.1 = 10%)
            decimals: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value * 100:.{decimals}f}%"
    
    @staticmethod
    def calculate_returns(prices: List[float]) -> List[float]:
        """
        Calculate percentage returns from price series.
        
        Args:
            prices: List of prices
            
        Returns:
            List of percentage returns
        """
        if len(prices) < 2:
            return []
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                return_pct = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(return_pct)
            else:
                returns.append(0.0)
        
        return returns


class MathUtils:
    """Mathematical utility functions."""
    
    @staticmethod
    def calculate_volatility(returns: List[float], window: int = 20) -> float:
        """
        Calculate rolling volatility from returns.
        
        Args:
            returns: List of returns
            window: Rolling window size
            
        Returns:
            Volatility value
        """
        if len(returns) < window:
            return 0.0
        
        recent_returns = returns[-window:]
        return float(np.std(recent_returns)) if recent_returns else 0.0
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: List of returns
            risk_free_rate: Risk-free rate (annualized)
            
        Returns:
            Sharpe ratio
        """
        if not returns:
            return 0.0
        
        excess_returns = [r - risk_free_rate/252 for r in returns]  # Daily risk-free rate
        
        mean_return = np.mean(excess_returns)
        std_return = np.std(excess_returns)
        
        if std_return == 0:
            return 0.0
        
        return float(mean_return / std_return * np.sqrt(252))  # Annualized
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Maximum drawdown as percentage
        """
        if len(equity_curve) < 2:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve[1:]:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, drawdown)
        
        return max_dd


class PerformanceTracker:
    """Track and calculate trading performance metrics."""
    
    def __init__(self):
        """Initialize performance tracker."""
        self.trades: List[Dict[str, Any]] = []
        self.equity_curve: List[float] = []
        self.daily_returns: List[float] = []
        
    def add_trade(self, 
                 instrument: str,
                 side: str,
                 entry_price: float,
                 exit_price: float,
                 quantity: float,
                 entry_time: datetime,
                 exit_time: datetime) -> None:
        """
        Add a completed trade.
        
        Args:
            instrument: Trading instrument
            side: Trade side (BUY/SELL)
            entry_price: Entry price
            exit_price: Exit price
            quantity: Trade quantity
            entry_time: Entry timestamp
            exit_time: Exit timestamp
        """
        # Calculate PnL
        if side.upper() == "BUY":
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        trade = {
            "instrument": instrument,
            "side": side,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "quantity": quantity,
            "pnl": pnl,
            "entry_time": entry_time,
            "exit_time": exit_time,
            "duration": (exit_time - entry_time).total_seconds() / 3600,  # hours
        }
        
        self.trades.append(trade)
    
    def add_equity_point(self, equity: float) -> None:
        """
        Add an equity curve point.
        
        Args:
            equity: Current equity value
        """
        self.equity_curve.append(equity)
        
        # Calculate daily return if we have previous equity
        if len(self.equity_curve) > 1:
            prev_equity = self.equity_curve[-2]
            if prev_equity > 0:
                daily_return = (equity - prev_equity) / prev_equity
                self.daily_returns.append(daily_return)
    
    def get_stats(self) -> PerformanceStats:
        """
        Calculate comprehensive performance statistics.
        
        Returns:
            Performance statistics
        """
        if not self.trades:
            return PerformanceStats()
        
        # Basic trade statistics
        total_trades = len(self.trades)
        winning_trades = sum(1 for trade in self.trades if trade["pnl"] > 0)
        losing_trades = total_trades - winning_trades
        
        total_pnl = sum(trade["pnl"] for trade in self.trades)
        
        # Win/loss statistics
        wins = [trade["pnl"] for trade in self.trades if trade["pnl"] > 0]
        losses = [trade["pnl"] for trade in self.trades if trade["pnl"] < 0]
        
        max_win = max(wins) if wins else 0.0
        max_loss = min(losses) if losses else 0.0
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0
        
        # Ratios
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        gross_profit = sum(wins) if wins else 0.0
        gross_loss = abs(sum(losses)) if losses else 0.0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        # Sharpe ratio
        sharpe_ratio = MathUtils.calculate_sharpe_ratio(self.daily_returns)
        
        return PerformanceStats(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            total_pnl=total_pnl,
            max_win=max_win,
            max_loss=max_loss,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio
        )
    
    def save_to_file(self, filepath: Path) -> None:
        """
        Save performance data to JSON file.
        
        Args:
            filepath: File path to save to
        """
        data = {
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "daily_returns": self.daily_returns,
            "stats": self.get_stats().__dict__,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Convert datetime objects to strings
        for trade in data["trades"]:
            trade["entry_time"] = trade["entry_time"].isoformat()
            trade["exit_time"] = trade["exit_time"].isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)


class TimingUtils:
    """Utilities for timing and performance measurement."""
    
    @staticmethod
    def time_function(func):
        """Decorator to time function execution."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger = logging.getLogger(func.__module__)
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
            
            return result
        return wrapper
    
    @staticmethod
    def get_market_hours() -> Dict[str, datetime]:
        """
        Get market hours information.
        
        Returns:
            Dictionary with market open/close times
        """
        now = datetime.now(timezone.utc)
        
        # Crypto markets are 24/7, but we can define "sessions"
        # for monitoring purposes
        return {
            "market_open": now.replace(hour=0, minute=0, second=0, microsecond=0),
            "market_close": now.replace(hour=23, minute=59, second=59, microsecond=999999),
            "current_time": now
        }


# Exception classes for better error handling
class BotError(Exception):
    """Base exception for bot-related errors."""
    pass


class ConfigurationError(BotError):
    """Error in bot configuration."""
    pass


class TradingError(BotError):
    """Error in trading operations."""
    pass


class RiskManagementError(BotError):
    """Error in risk management."""
    pass


class DataError(BotError):
    """Error in data processing."""
    pass
