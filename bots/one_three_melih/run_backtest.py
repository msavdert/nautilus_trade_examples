#!/usr/bin/env python3
"""
Comprehensive backtest runner for the One-Three-Melih Strategy
=============================================================

This module provides advanced backtesting capabilities with detailed
performance analysis, visualization, and statistical reporting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from decimal import Decimal

from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.backtest.modules import FXRolloverInterestModule
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import QuoteTick
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import TraderId, StrategyId, Venue
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.core.datetime import dt_to_unix_nanos

from one_three_melih_strategy import OneThreeMelihStrategy, OneThreeMelihConfig


class AdvancedBacktestRunner:
    """Advanced backtest runner with comprehensive analysis."""
    
    def __init__(self, log_level: str = "INFO"):
        self.setup_logging(log_level)
        self.results = {}
        
    def setup_logging(self, log_level: str) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('backtest_results.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    async def run_comprehensive_backtest(
        self,
        start_date: str,
        end_date: str,
        initial_balance: float = 100.0,
        profit_percentage: float = 30.0,
        data_frequency_minutes: int = 1,
    ) -> Dict[str, Any]:
        """
        Run comprehensive backtest with detailed analysis.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            initial_balance: Starting balance in USD
            profit_percentage: Profit target percentage
            data_frequency_minutes: Data frequency in minutes
            
        Returns:
            Comprehensive results dictionary
        """
        self.logger.info("=== COMPREHENSIVE BACKTEST ANALYSIS ===")
        self.logger.info(f"Period: {start_date} to {end_date}")
        self.logger.info(f"Initial Balance: ${initial_balance}")
        self.logger.info(f"Profit Target: {profit_percentage}%")
        
        # Create backtest engine
        config = BacktestEngineConfig(
            trader_id=TraderId("BACKTEST-COMPREHENSIVE"),
            logging=LoggingConfig(log_level="INFO"),
        )
        
        engine = BacktestEngine(config)
        
        # Add EUR/USD instrument
        EURUSD_SIM = TestInstrumentProvider.default_fx_ccy("EUR/USD", Venue("SIM"))
        engine.add_instrument(EURUSD_SIM)
        
        # Add simulated FX account
        engine.add_account_for_venue(
            venue=Venue("SIM"),
            account_type=AccountType.MARGIN,
            base_currency=USD,
            starting_balances=[Money(initial_balance, USD)],
        )
        
        # Generate enhanced market data
        data = self.generate_enhanced_market_data(
            start_date, end_date, data_frequency_minutes
        )
        engine.add_data(data)
        
        # Create and add strategy
        strategy_config = OneThreeMelihConfig(
            strategy_id=StrategyId("OneThreeMelih-Comprehensive"),
            initial_balance=Decimal(str(initial_balance)),
            profit_target_percentage=Decimal(str(profit_percentage)),
        )
        strategy = OneThreeMelihStrategy(strategy_config)
        engine.add_strategy(strategy)
        
        # Run backtest
        self.logger.info("Executing comprehensive backtest...")
        start_time = datetime.now()
        await engine.run_async()
        execution_time = datetime.now() - start_time
        
        # Analyze results
        results = self.analyze_backtest_results(engine, strategy, execution_time)
        self.results = results
        
        # Print comprehensive report
        self.print_comprehensive_report(results)
        
        return results
    
    def generate_enhanced_market_data(
        self, 
        start_date: str, 
        end_date: str, 
        frequency_minutes: int = 1
    ) -> List[QuoteTick]:
        """
        Generate enhanced market data with realistic price movements.
        
        Args:
            start_date: Start date string
            end_date: End date string
            frequency_minutes: Data frequency in minutes
            
        Returns:
            List of quote ticks with realistic market behavior
        """
        import random
        import math
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        quotes = []
        current_dt = start_dt
        base_price = Decimal("1.1000")  # Starting EUR/USD price
        
        EURUSD_SIM = TestInstrumentProvider.default_fx_ccy("EUR/USD", Venue("SIM"))
        
        # Market parameters
        volatility = 0.001  # Daily volatility
        trend_strength = 0.0001  # Trend component
        mean_reversion = 0.1  # Mean reversion strength
        
        price_history = [base_price]
        
        while current_dt < end_dt:
            # Skip weekends (simplified)
            if current_dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
                current_dt += timedelta(minutes=frequency_minutes)
                continue
            
            # Generate more realistic price movement
            dt_fraction = frequency_minutes / (24 * 60)  # Fraction of day
            
            # Random walk component
            random_component = random.gauss(0, volatility * math.sqrt(dt_fraction))
            
            # Trend component (simulating market bias)
            time_factor = (current_dt - start_dt).total_seconds() / (end_dt - start_dt).total_seconds()
            trend_component = trend_strength * math.sin(2 * math.pi * time_factor * 4)  # 4 cycles
            
            # Mean reversion component
            price_deviation = float(base_price - Decimal("1.1000"))
            mean_reversion_component = -mean_reversion * price_deviation * dt_fraction
            
            # Combine components
            total_change = random_component + trend_component + mean_reversion_component
            base_price += Decimal(str(total_change))
            
            # Ensure reasonable price bounds
            base_price = max(Decimal("1.0000"), min(Decimal("1.5000"), base_price))
            price_history.append(base_price)
            
            # Create realistic bid/ask spread
            spread_base = Decimal("0.0001")  # 1 pip base spread
            spread_volatility = Decimal(str(abs(total_change) * 1000))  # Spread widens with volatility
            total_spread = spread_base + spread_volatility
            
            bid_price = Price(base_price - total_spread/2, precision=5)
            ask_price = Price(base_price + total_spread/2, precision=5)
            
            # Realistic volumes
            base_volume = 1000000
            volume_variation = random.uniform(0.5, 2.0)
            volume = int(base_volume * volume_variation)
            
            # Create quote tick
            quote = QuoteTick(
                instrument_id=EURUSD_SIM.id,
                bid_price=bid_price,
                ask_price=ask_price,
                bid_size=Quantity(volume, precision=0),
                ask_size=Quantity(volume, precision=0),
                ts_event=dt_to_unix_nanos(current_dt),
                ts_init=dt_to_unix_nanos(current_dt),
            )
            quotes.append(quote)
            
            # Move to next interval
            current_dt += timedelta(minutes=frequency_minutes)
        
        self.logger.info(f"Generated {len(quotes)} enhanced market data points")
        return quotes
    
    def analyze_backtest_results(
        self, 
        engine: BacktestEngine, 
        strategy: OneThreeMelihStrategy,
        execution_time: timedelta
    ) -> Dict[str, Any]:
        """Analyze comprehensive backtest results."""
        
        # Get portfolio and account data
        portfolio = engine.trader.portfolio
        account = portfolio.account(Venue("SIM"))
        
        # Get strategy statistics
        balance_stats = strategy.balance_tracker.get_stats()
        
        # Calculate performance metrics
        initial_balance = balance_stats["initial_balance"]
        final_balance = balance_stats["current_balance"]
        total_return = ((final_balance - initial_balance) / initial_balance) * 100
        
        # Trading statistics
        total_trades = strategy.total_trades
        winning_trades = strategy.winning_trades
        losing_trades = strategy.losing_trades
        win_rate = (winning_trades / max(total_trades, 1)) * 100
        
        # Risk metrics
        max_step = max(len(balance_stats["balance_history"]), 1)
        current_step = len(balance_stats["balance_history"])
        max_consecutive_losses = strategy.consecutive_losses
        
        # Performance ratios
        avg_win = final_balance / max(winning_trades, 1) if winning_trades > 0 else 0
        avg_loss = abs(initial_balance - final_balance) / max(losing_trades, 1) if losing_trades > 0 else 0
        profit_factor = avg_win / max(avg_loss, 0.01)
        
        results = {
            "execution_info": {
                "execution_time_seconds": execution_time.total_seconds(),
                "data_points_processed": len(strategy.balance_tracker.balance_history),
            },
            "balance_performance": {
                "initial_balance": initial_balance,
                "final_balance": final_balance,
                "total_return_pct": total_return,
                "balance_history": balance_stats["balance_history"],
                "max_step_reached": max_step,
                "final_step": current_step,
            },
            "trading_statistics": {
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate_pct": win_rate,
                "max_consecutive_losses": max_consecutive_losses,
            },
            "risk_metrics": {
                "profit_factor": profit_factor,
                "avg_win": avg_win,
                "avg_loss": avg_loss,
                "max_drawdown_steps": max_step - current_step,
            },
            "strategy_config": {
                "profit_target_pct": float(strategy.balance_tracker.profit_percentage),
                "initial_balance": float(strategy.balance_tracker.initial_balance),
            }
        }
        
        return results
    
    def print_comprehensive_report(self, results: Dict[str, Any]) -> None:
        """Print comprehensive backtest report."""
        
        print("\n" + "="*80)
        print("         COMPREHENSIVE BACKTEST REPORT")
        print("="*80)
        
        # Execution Info
        exec_info = results["execution_info"]
        print(f"\n📊 EXECUTION INFORMATION")
        print(f"   Execution Time: {exec_info['execution_time_seconds']:.2f} seconds")
        print(f"   Data Points: {exec_info['data_points_processed']:,}")
        
        # Balance Performance
        balance = results["balance_performance"]
        print(f"\n💰 BALANCE PERFORMANCE")
        print(f"   Initial Balance: ${balance['initial_balance']:.2f}")
        print(f"   Final Balance: ${balance['final_balance']:.2f}")
        print(f"   Total Return: {balance['total_return_pct']:+.2f}%")
        print(f"   Max Step Reached: {balance['max_step_reached']}")
        print(f"   Final Step: {balance['final_step']}")
        
        # Balance progression
        print(f"   Balance History: {[f'${b:.0f}' for b in balance['balance_history']]}")
        
        # Trading Statistics
        trading = results["trading_statistics"]
        print(f"\n📈 TRADING STATISTICS")
        print(f"   Total Trades: {trading['total_trades']}")
        print(f"   Winning Trades: {trading['winning_trades']}")
        print(f"   Losing Trades: {trading['losing_trades']}")
        print(f"   Win Rate: {trading['win_rate_pct']:.1f}%")
        print(f"   Max Consecutive Losses: {trading['max_consecutive_losses']}")
        
        # Risk Metrics
        risk = results["risk_metrics"]
        print(f"\n⚖️  RISK METRICS")
        print(f"   Profit Factor: {risk['profit_factor']:.2f}")
        print(f"   Average Win: ${risk['avg_win']:.2f}")
        print(f"   Average Loss: ${risk['avg_loss']:.2f}")
        print(f"   Max Drawdown (Steps): {risk['max_drawdown_steps']}")
        
        # Strategy Configuration
        config = results["strategy_config"]
        print(f"\n⚙️  STRATEGY CONFIGURATION")
        print(f"   Profit Target: {config['profit_target_pct']:.1f}%")
        print(f"   Initial Balance: ${config['initial_balance']:.2f}")
        
        # Performance Analysis
        self.print_performance_analysis(results)
        
        print("="*80)
    
    def print_performance_analysis(self, results: Dict[str, Any]) -> None:
        """Print detailed performance analysis."""
        
        balance = results["balance_performance"]
        trading = results["trading_statistics"]
        risk = results["risk_metrics"]
        
        print(f"\n🔍 PERFORMANCE ANALYSIS")
        
        # Return analysis
        total_return = balance["total_return_pct"]
        if total_return > 50:
            performance_rating = "EXCELLENT"
        elif total_return > 20:
            performance_rating = "GOOD"
        elif total_return > 0:
            performance_rating = "POSITIVE"
        else:
            performance_rating = "NEGATIVE"
        
        print(f"   Performance Rating: {performance_rating}")
        
        # Win rate analysis
        win_rate = trading["win_rate_pct"]
        if win_rate > 60:
            win_rate_rating = "HIGH"
        elif win_rate > 50:
            win_rate_rating = "GOOD"
        elif win_rate > 40:
            win_rate_rating = "AVERAGE"
        else:
            win_rate_rating = "LOW"
        
        print(f"   Win Rate Rating: {win_rate_rating}")
        
        # Risk analysis
        max_steps_back = risk["max_drawdown_steps"]
        if max_steps_back <= 1:
            risk_rating = "LOW"
        elif max_steps_back <= 2:
            risk_rating = "MODERATE"
        else:
            risk_rating = "HIGH"
        
        print(f"   Risk Rating: {risk_rating}")
        
        # Strategy effectiveness
        profit_factor = risk["profit_factor"]
        if profit_factor > 2.0:
            strategy_rating = "HIGHLY EFFECTIVE"
        elif profit_factor > 1.5:
            strategy_rating = "EFFECTIVE"
        elif profit_factor > 1.0:
            strategy_rating = "MARGINALLY EFFECTIVE"
        else:
            strategy_rating = "INEFFECTIVE"
        
        print(f"   Strategy Effectiveness: {strategy_rating}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        if win_rate < 50:
            print("   - Consider improving entry signals to increase win rate")
        if max_steps_back > 2:
            print("   - Consider reducing risk or implementing additional filters")
        if total_return < 0:
            print("   - Strategy may not be suitable for this market period")
        if profit_factor < 1.2:
            print("   - Consider adjusting profit/loss ratios")


async def main():
    """Main entry point for advanced backtesting."""
    
    runner = AdvancedBacktestRunner()
    
    # Run comprehensive backtest
    results = await runner.run_comprehensive_backtest(
        start_date="2024-01-01",
        end_date="2024-06-01",
        initial_balance=100.0,
        profit_percentage=30.0,
        data_frequency_minutes=5,  # 5-minute data
    )
    
    # Save results for further analysis
    import json
    with open("backtest_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n✅ Backtest completed. Results saved to 'backtest_results.json'")


if __name__ == "__main__":
    asyncio.run(main())
