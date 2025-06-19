#!/usr/bin/env python3
"""
Utilities for One-Three Risk Management Bot
==========================================

This module provides utility functions and classes to support the One-Three
trading strategy, including data management, performance calculations, and
helper functions for strategy development.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.currencies import USD


class RiskCalculator:
    """
    Risk management calculations for the One-Three strategy.
    
    This class provides methods to calculate position sizes, risk metrics,
    and portfolio-level risk management parameters.
    """
    
    def __init__(self, account_balance: float, max_risk_per_trade: float = 0.01):
        """
        Initialize the risk calculator.
        
        Args:
            account_balance: Current account balance in base currency
            max_risk_per_trade: Maximum risk per trade as percentage (default 1%)
        """
        self.account_balance = account_balance
        self.max_risk_per_trade = max_risk_per_trade
        
    def calculate_position_size(
        self, 
        entry_price: float, 
        stop_loss_price: float,
        pip_value: float = 10.0  # USD per pip for standard lot EUR/USD
    ) -> int:
        """
        Calculate optimal position size based on risk parameters.
        
        Args:
            entry_price: Planned entry price
            stop_loss_price: Stop loss price
            pip_value: Value per pip in account currency
            
        Returns:
            Position size in base currency units
        """
        risk_amount = self.account_balance * self.max_risk_per_trade
        stop_loss_pips = abs(entry_price - stop_loss_price) / 0.0001
        
        if stop_loss_pips == 0:
            return 0
            
        max_units = risk_amount / (stop_loss_pips * pip_value) * 100000
        
        # Round to standard lot sizes
        return int(max_units // 10000) * 10000
        
    def calculate_risk_reward_ratio(
        self, 
        entry_price: float, 
        take_profit_price: float, 
        stop_loss_price: float
    ) -> float:
        """Calculate risk-reward ratio for a trade."""
        profit_pips = abs(take_profit_price - entry_price) / 0.0001
        loss_pips = abs(entry_price - stop_loss_price) / 0.0001
        
        if loss_pips == 0:
            return float('inf')
            
        return profit_pips / loss_pips
        
    def update_balance(self, new_balance: float) -> None:
        """Update account balance for position size calculations."""
        self.account_balance = new_balance


class PerformanceTracker:
    """
    Track and analyze trading performance metrics.
    
    This class maintains running statistics of trading performance and
    provides methods to calculate various performance metrics.
    """
    
    def __init__(self):
        """Initialize the performance tracker."""
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.start_time = datetime.now()
        
    def add_trade(
        self, 
        entry_time: datetime,
        exit_time: datetime,
        entry_price: float,
        exit_price: float,
        position_size: int,
        pnl: float,
        reason: str
    ) -> None:
        """
        Add a completed trade to the performance tracker.
        
        Args:
            entry_time: Trade entry timestamp
            exit_time: Trade exit timestamp
            entry_price: Entry price
            exit_price: Exit price
            position_size: Position size in base currency
            pnl: Profit/loss in account currency
            reason: Exit reason (TAKE_PROFIT, STOP_LOSS, etc.)
        """
        trade = {
            'entry_time': entry_time,
            'exit_time': exit_time,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'position_size': position_size,
            'pnl': pnl,
            'reason': reason,
            'duration': (exit_time - entry_time).total_seconds() / 60,  # minutes
        }
        
        self.trades.append(trade)
        
        # Update equity curve
        if self.equity_curve:
            self.equity_curve.append(self.equity_curve[-1] + pnl)
        else:
            self.equity_curve.append(pnl)
            
    def get_statistics(self) -> Dict:
        """
        Calculate comprehensive performance statistics.
        
        Returns:
            Dictionary containing performance metrics
        """
        if not self.trades:
            return {}
            
        df = pd.DataFrame(self.trades)
        
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]
        
        stats = {
            'total_trades': len(self.trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(self.trades) * 100 if self.trades else 0,
            'total_pnl': df['pnl'].sum(),
            'avg_win': winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            'avg_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            'largest_win': df['pnl'].max(),
            'largest_loss': df['pnl'].min(),
            'avg_duration': df['duration'].mean(),
            'profit_factor': self._calculate_profit_factor(df),
            'max_drawdown': self._calculate_max_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio(df),
        }
        
        return stats
        
    def _calculate_profit_factor(self, df: pd.DataFrame) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = df[df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0
            
        return gross_profit / gross_loss
        
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from equity curve."""
        if not self.equity_curve:
            return 0.0
            
        cumulative = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        
        return drawdown.min()
        
    def _calculate_sharpe_ratio(self, df: pd.DataFrame, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(df) < 2:
            return 0.0
            
        returns = df['pnl']
        excess_return = returns.mean() - risk_free_rate / 252  # Daily risk-free rate
        volatility = returns.std()
        
        if volatility == 0:
            return 0.0
            
        return excess_return / volatility * np.sqrt(252)  # Annualized
        
    def export_trades(self, filename: str = "trades_export.csv") -> None:
        """Export trade history to CSV file."""
        if self.trades:
            df = pd.DataFrame(self.trades)
            df.to_csv(filename, index=False)
            print(f"Trades exported to {filename}")


class MarketDataGenerator:
    """
    Generate realistic market data for testing and backtesting.
    
    This class creates synthetic but realistic EUR/USD price data with
    proper spreads, volatility patterns, and market microstructure.
    """
    
    def __init__(self, seed: int = 42):
        """Initialize the market data generator."""
        np.random.seed(seed)
        
    def generate_tick_data(
        self,
        start_date: datetime,
        end_date: datetime,
        num_ticks: int,
        base_price: float = 1.0800,
        daily_volatility: float = 0.01
    ) -> pd.DataFrame:
        """
        Generate realistic tick-by-tick EUR/USD data.
        
        Args:
            start_date: Start date for data generation
            end_date: End date for data generation
            num_ticks: Number of ticks to generate
            base_price: Starting price level
            daily_volatility: Daily volatility (as decimal, e.g., 0.01 = 1%)
            
        Returns:
            DataFrame with tick data
        """
        # Generate timestamps
        time_delta = (end_date - start_date).total_seconds()
        tick_interval = time_delta / num_ticks
        
        timestamps = [
            start_date + timedelta(seconds=i * tick_interval)
            for i in range(num_ticks)
        ]
        
        # Generate price series with realistic patterns
        prices = self._generate_price_series(num_ticks, base_price, daily_volatility)
        
        # Generate spreads (0.5-2.0 pips typical for EUR/USD)
        spreads = np.random.uniform(0.00005, 0.00020, num_ticks)
        
        # Calculate bid/ask prices
        bid_prices = [p - s/2 for p, s in zip(prices, spreads)]
        ask_prices = [p + s/2 for p, s in zip(prices, spreads)]
        
        # Generate volumes
        bid_sizes = np.random.uniform(100000, 5000000, num_ticks)
        ask_sizes = np.random.uniform(100000, 5000000, num_ticks)
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'bid_price': bid_prices,
            'ask_price': ask_prices,
            'bid_size': bid_sizes,
            'ask_size': ask_sizes,
        })
        
    def _generate_price_series(self, num_ticks: int, base_price: float, volatility: float) -> List[float]:
        """Generate realistic price movements."""
        prices = [base_price]
        
        # Hourly volatility pattern (higher during London/NY sessions)
        hourly_vol = np.array([
            0.3, 0.2, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0,  # Asian session
            1.2, 1.5, 1.8, 2.0, 2.2, 2.0, 1.8, 1.5,  # London session
            1.8, 2.2, 2.5, 2.0, 1.5, 1.0, 0.8, 0.5   # NY session
        ])
        
        for i in range(1, num_ticks):
            # Current hour for volatility adjustment
            current_hour = (i * 24 // num_ticks) % 24
            vol_multiplier = hourly_vol[current_hour] / 2.0
            
            # Price change with mean reversion
            price_change = np.random.normal(0, volatility * vol_multiplier / np.sqrt(365 * 24))
            
            # Add small trend component
            trend = 0.00001 * np.sin(i / 1000)
            
            # Mean reversion
            mean_reversion = (base_price - prices[-1]) * 0.001
            
            new_price = prices[-1] + price_change + trend + mean_reversion
            
            # Keep prices in reasonable range
            new_price = max(base_price * 0.95, min(base_price * 1.05, new_price))
            prices.append(new_price)
            
        return prices


class ConfigurationManager:
    """
    Manage configuration settings for the One-Three strategy.
    
    This class provides methods to load, validate, and manage
    configuration parameters for different environments.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.config_file = config_file
        self.default_config = self._get_default_config()
        
    def _get_default_config(self) -> Dict:
        """Get default configuration settings."""
        return {
            'strategy': {
                'instrument_id': 'EUR/USD.SIM',
                'trade_size': 100_000,
                'take_profit_pips': 1.3,
                'stop_loss_pips': 1.3,
                'max_daily_trades': 20,
                'entry_delay_seconds': 60,
                'use_tick_data': True,
                'enable_time_filter': False,
            },
            'risk_management': {
                'max_risk_per_trade': 0.01,  # 1% of account
                'max_daily_risk': 0.05,      # 5% of account
                'max_drawdown_limit': 0.10,  # 10% of account
            },
            'execution': {
                'slippage_tolerance': 0.5,   # pips
                'max_order_retry': 3,
                'order_timeout': 30,         # seconds
            },
            'data': {
                'tick_data_buffer_size': 1000,
                'bar_data_buffer_size': 500,
            },
            'logging': {
                'log_level': 'INFO',
                'log_to_file': True,
                'log_directory': 'logs',
            }
        }
        
    def get_config(self, section: Optional[str] = None) -> Dict:
        """
        Get configuration settings.
        
        Args:
            section: Specific configuration section to retrieve
            
        Returns:
            Configuration dictionary
        """
        if section:
            return self.default_config.get(section, {})
        return self.default_config
        
    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate configuration parameters.
        
        Args:
            config: Configuration to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Validate strategy parameters
        strategy = config.get('strategy', {})
        if strategy.get('take_profit_pips', 0) <= 0:
            errors.append("Take profit pips must be positive")
        if strategy.get('stop_loss_pips', 0) <= 0:
            errors.append("Stop loss pips must be positive")
        if strategy.get('trade_size', 0) <= 0:
            errors.append("Trade size must be positive")
            
        # Validate risk management
        risk = config.get('risk_management', {})
        if risk.get('max_risk_per_trade', 0) <= 0 or risk.get('max_risk_per_trade', 1) > 0.1:
            errors.append("Max risk per trade should be between 0 and 10%")
            
        return len(errors) == 0, errors


# Utility functions

def pips_to_price_difference(pips: float, pip_size: float = 0.0001) -> float:
    """Convert pips to actual price difference."""
    return pips * pip_size


def price_difference_to_pips(price_diff: float, pip_size: float = 0.0001) -> float:
    """Convert price difference to pips."""
    return price_diff / pip_size


def format_pnl(pnl: float, currency: str = "USD") -> str:
    """Format P&L for display."""
    sign = "+" if pnl >= 0 else ""
    return f"{sign}{pnl:.2f} {currency}"


def calculate_compound_return(trades_pnl: List[float], initial_balance: float) -> float:
    """Calculate compound return from series of P&L values."""
    balance = initial_balance
    for pnl in trades_pnl:
        balance += pnl
    return (balance / initial_balance - 1) * 100


if __name__ == "__main__":
    print("🛠️ One-Three Strategy Utilities")
    print("=" * 40)
    print()
    print("This module provides utility classes and functions for:")
    print("• Risk management calculations")
    print("• Performance tracking and analysis") 
    print("• Market data generation for testing")
    print("• Configuration management")
    print()
    print("Import these utilities in your strategy for enhanced functionality.")
