#!/usr/bin/env python3
"""
Utility functions for the One-Three-Melih Trading Bot
=====================================================

This module provides utility functions for data analysis, performance
calculations, and visualization support.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Tuple, Optional
import json
import logging
from datetime import datetime, timedelta


class PerformanceAnalyzer:
    """Analyze trading performance and generate insights."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_sharpe_ratio(
        self, 
        returns: List[float], 
        risk_free_rate: float = 0.02
    ) -> float:
        """
        Calculate the Sharpe ratio for a series of returns.
        
        Args:
            returns: List of period returns
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Sharpe ratio
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        import statistics
        import math
        
        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        if std_return == 0:
            return 0.0
        
        # Adjust risk-free rate for period
        period_risk_free = risk_free_rate / len(returns)
        
        sharpe = (avg_return - period_risk_free) / std_return
        return sharpe
    
    def calculate_max_drawdown(self, balance_history: List[float]) -> Dict[str, Any]:
        """
        Calculate maximum drawdown from balance history.
        
        Args:
            balance_history: List of balance values over time
            
        Returns:
            Dictionary with drawdown metrics
        """
        if len(balance_history) < 2:
            return {"max_drawdown_pct": 0.0, "max_drawdown_periods": 0}
        
        peak = balance_history[0]
        max_drawdown = 0.0
        current_drawdown_periods = 0
        max_drawdown_periods = 0
        
        for balance in balance_history:
            if balance > peak:
                peak = balance
                current_drawdown_periods = 0
            else:
                current_drawdown_periods += 1
                drawdown = (peak - balance) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    max_drawdown_periods = current_drawdown_periods
        
        return {
            "max_drawdown_pct": max_drawdown * 100,
            "max_drawdown_periods": max_drawdown_periods,
            "peak_balance": peak,
        }
    
    def analyze_trade_distribution(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze the distribution of trades.
        
        Args:
            trades: List of trade dictionaries
            
        Returns:
            Trade distribution analysis
        """
        if not trades:
            return {}
        
        wins = [t for t in trades if t.get("pnl", 0) > 0]
        losses = [t for t in trades if t.get("pnl", 0) < 0]
        
        win_amounts = [t["pnl"] for t in wins]
        loss_amounts = [abs(t["pnl"]) for t in losses]
        
        analysis = {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": len(wins) / len(trades) * 100 if trades else 0,
            "avg_win": sum(win_amounts) / len(win_amounts) if win_amounts else 0,
            "avg_loss": sum(loss_amounts) / len(loss_amounts) if loss_amounts else 0,
            "largest_win": max(win_amounts) if win_amounts else 0,
            "largest_loss": max(loss_amounts) if loss_amounts else 0,
        }
        
        # Profit factor
        total_wins = sum(win_amounts)
        total_losses = sum(loss_amounts)
        analysis["profit_factor"] = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return analysis


class BalanceCalculator:
    """Calculate balance progression and step management."""
    
    @staticmethod
    def calculate_step_progression(
        initial_balance: Decimal,
        profit_percentage: Decimal,
        num_steps: int
    ) -> List[Decimal]:
        """
        Calculate balance progression for a given number of profit steps.
        
        Args:
            initial_balance: Starting balance
            profit_percentage: Profit percentage per step
            num_steps: Number of steps to calculate
            
        Returns:
            List of balance values for each step
        """
        balances = [initial_balance]
        current_balance = initial_balance
        
        for _ in range(num_steps):
            current_balance = current_balance * (Decimal("1") + profit_percentage / Decimal("100"))
            current_balance = current_balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            balances.append(current_balance)
        
        return balances
    
    @staticmethod
    def calculate_required_loss_percentage(
        current_balance: Decimal,
        target_balance: Decimal
    ) -> Decimal:
        """
        Calculate the loss percentage needed to reach target balance.
        
        Args:
            current_balance: Current balance amount
            target_balance: Target balance amount
            
        Returns:
            Required loss percentage
        """
        if current_balance <= target_balance:
            return Decimal("0")
        
        loss_amount = current_balance - target_balance
        loss_percentage = (loss_amount / current_balance) * Decimal("100")
        
        return loss_percentage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def simulate_balance_scenario(
        initial_balance: Decimal,
        profit_percentage: Decimal,
        win_loss_sequence: List[bool]
    ) -> List[Dict[str, Any]]:
        """
        Simulate balance progression for a given win/loss sequence.
        
        Args:
            initial_balance: Starting balance
            profit_percentage: Profit percentage per win
            win_loss_sequence: List of boolean values (True=win, False=loss)
            
        Returns:
            List of balance progression records
        """
        from one_three_melih_strategy import BalanceTracker
        
        tracker = BalanceTracker(initial_balance, profit_percentage)
        progression = []
        
        for i, is_win in enumerate(win_loss_sequence):
            step_info = {
                "trade_number": i + 1,
                "is_win": is_win,
                "balance_before": tracker.get_current_balance(),
                "profit_target": tracker.get_profit_target(),
                "stop_loss_pct": tracker.get_stop_loss_percentage(),
                "stop_loss_amount": tracker.get_stop_loss_amount(),
            }
            
            if is_win:
                new_balance = tracker.record_profit()
            else:
                new_balance = tracker.record_loss()
            
            step_info.update({
                "balance_after": new_balance,
                "step_level": len(tracker.balance_history),
                "balance_change": new_balance - step_info["balance_before"],
            })
            
            progression.append(step_info)
        
        return progression


class DataExporter:
    """Export trading data and results to various formats."""
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], filename: str) -> None:
        """Export data to JSON file."""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def export_balance_history_csv(balance_history: List[float], filename: str) -> None:
        """Export balance history to CSV format."""
        import csv
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Step', 'Balance'])
            for i, balance in enumerate(balance_history):
                writer.writerow([i, balance])
    
    @staticmethod
    def export_trade_log_csv(trades: List[Dict[str, Any]], filename: str) -> None:
        """Export trade log to CSV format."""
        import csv
        
        if not trades:
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=trades[0].keys())
            writer.writeheader()
            writer.writerows(trades)


class ConfigurationHelper:
    """Helper functions for strategy configuration and optimization."""
    
    @staticmethod
    def generate_config_variations(
        base_config: Dict[str, Any],
        parameter_ranges: Dict[str, List[Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate configuration variations for parameter optimization.
        
        Args:
            base_config: Base configuration dictionary
            parameter_ranges: Dictionary of parameter names and their ranges
            
        Returns:
            List of configuration variations
        """
        import itertools
        
        # Get parameter names and values
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())
        
        # Generate all combinations
        combinations = list(itertools.product(*param_values))
        
        # Create configurations
        configs = []
        for combination in combinations:
            config = base_config.copy()
            for param_name, param_value in zip(param_names, combination):
                config[param_name] = param_value
            configs.append(config)
        
        return configs
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """
        Validate strategy configuration and return any warnings.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of validation warnings
        """
        warnings = []
        
        # Check initial balance
        if config.get("initial_balance", 0) <= 0:
            warnings.append("Initial balance must be positive")
        
        # Check profit percentage
        profit_pct = config.get("profit_target_percentage", 0)
        if profit_pct <= 0 or profit_pct > 100:
            warnings.append("Profit target percentage should be between 0 and 100")
        
        # Check maximum consecutive losses
        max_losses = config.get("max_consecutive_losses", 0)
        if max_losses <= 0 or max_losses > 50:
            warnings.append("Max consecutive losses should be between 1 and 50")
        
        return warnings


class MarketDataGenerator:
    """Generate realistic market data for testing and simulation."""
    
    def __init__(self, base_price: float = 1.1000, volatility: float = 0.001):
        self.base_price = base_price
        self.volatility = volatility
    
    def generate_random_walk(
        self,
        num_points: int,
        time_step: float = 1.0
    ) -> List[Tuple[datetime, float]]:
        """
        Generate random walk price data.
        
        Args:
            num_points: Number of price points to generate
            time_step: Time step in hours
            
        Returns:
            List of (datetime, price) tuples
        """
        import random
        import math
        
        prices = []
        current_price = self.base_price
        current_time = datetime.now()
        
        for i in range(num_points):
            # Random walk with drift
            change = random.gauss(0, self.volatility * math.sqrt(time_step))
            current_price += change
            
            # Ensure reasonable bounds
            current_price = max(0.8, min(1.5, current_price))
            
            prices.append((current_time, current_price))
            current_time += timedelta(hours=time_step)
        
        return prices
    
    def generate_trending_data(
        self,
        num_points: int,
        trend_strength: float = 0.0001,
        time_step: float = 1.0
    ) -> List[Tuple[datetime, float]]:
        """
        Generate trending price data with noise.
        
        Args:
            num_points: Number of price points
            trend_strength: Strength of the trend
            time_step: Time step in hours
            
        Returns:
            List of (datetime, price) tuples
        """
        import random
        import math
        
        prices = []
        current_price = self.base_price
        current_time = datetime.now()
        
        for i in range(num_points):
            # Trend component
            trend = trend_strength * time_step
            
            # Random component
            noise = random.gauss(0, self.volatility * math.sqrt(time_step))
            
            # Combine trend and noise
            current_price += trend + noise
            
            # Ensure reasonable bounds
            current_price = max(0.8, min(1.5, current_price))
            
            prices.append((current_time, current_price))
            current_time += timedelta(hours=time_step)
        
        return prices


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount for display."""
    if currency == "USD":
        return f"${amount:.2f}"
    return f"{amount:.2f} {currency}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format percentage for display."""
    return f"{value:.{decimals}f}%"


def calculate_compound_growth(
    initial_value: float,
    growth_rate: float,
    periods: int
) -> float:
    """Calculate compound growth over periods."""
    return initial_value * ((1 + growth_rate) ** periods)


def parse_date_string(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date: {date_str}")


if __name__ == "__main__":
    # Example usage of utility functions
    print("One-Three-Melih Utility Functions")
    print("=" * 40)
    
    # Test balance calculation
    calc = BalanceCalculator()
    progression = calc.calculate_step_progression(
        Decimal("100"), Decimal("30"), 5
    )
    print(f"Balance progression: {[float(b) for b in progression]}")
    
    # Test loss percentage calculation
    loss_pct = calc.calculate_required_loss_percentage(
        Decimal("169"), Decimal("130")
    )
    print(f"Required loss percentage: {loss_pct}%")
    
    # Test scenario simulation
    sequence = [True, True, False, True, False, False]  # Win, Win, Loss, Win, Loss, Loss
    scenario = calc.simulate_balance_scenario(
        Decimal("100"), Decimal("30"), sequence
    )
    
    print("\nScenario simulation:")
    for step in scenario:
        print(f"Trade {step['trade_number']}: {'Win' if step['is_win'] else 'Loss'} "
              f"${step['balance_before']:.0f} → ${step['balance_after']:.0f} "
              f"(Step {step['step_level']})")
