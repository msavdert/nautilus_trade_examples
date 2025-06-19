#!/usr/bin/env python3
"""
Main execution script for the One-Three-Melih Trading Bot
=========================================================

This script provides multiple execution modes:
- Backtest: Run strategy against historical data
- Demo: Run strategy with simulated live data
- Live: Run strategy with real market data (use with caution)

Usage:
    python main.py --mode demo
    python main.py --mode backtest --start-date 2024-01-01 --end-date 2024-06-01
    python main.py --mode live --config live_config.json
"""

import argparse
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional, Dict, Any

from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.backtest.modules import FXRolloverInterestModule
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import TraderId, StrategyId, Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import QuoteTickDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.test_kit.stubs.data import TestDataStubs

from one_three_melih_strategy import OneThreeMelihStrategy, OneThreeMelihConfig


class TradingBotRunner:
    """
    Main runner for the One-Three-Melih trading bot with multiple execution modes.
    """
    
    def __init__(self):
        self.setup_logging()
        
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('one_three_melih.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_backtest(self, start_date: str, end_date: str, initial_balance: float = 100.0) -> None:
        """
        Run backtest with historical data.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            initial_balance: Starting balance in USD
        """
        self.logger.info("=== Starting Backtest Mode ===")
        self.logger.info(f"Period: {start_date} to {end_date}")
        self.logger.info(f"Initial Balance: ${initial_balance}")
        
        # Create backtest engine configuration
        config = BacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),
            logging=LoggingConfig(log_level="INFO"),
        )
        
        # Create backtest engine
        engine = BacktestEngine(config)
        
        # Add simulated execution venue
        venue = Venue("SIM")
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.HEDGING,
            account_type=AccountType.MARGIN,
            base_currency=USD,
            starting_balances=[Money(initial_balance, USD)],
            default_leverage=Decimal(1),  # No leverage
        )
        
        # Add EUR/USD instrument
        EURUSD_SIM = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue)
        engine.add_instrument(EURUSD_SIM)
        
        # Generate sample data for backtesting
        data = self.generate_sample_data(start_date, end_date)
        engine.add_data(data)
        
        # Create and add strategy
        strategy_config = OneThreeMelihConfig(
            initial_balance=initial_balance,
        )
        strategy = OneThreeMelihStrategy(strategy_config)
        engine.add_strategy(strategy)
        
        # Run backtest
        self.logger.info("Running backtest...")
        engine.run()
        
        # Print results
        self.print_backtest_results(engine)
    
    def run_demo(self, initial_balance: float = 100.0) -> None:
        """
        Run demo mode with simulated live market data.
        
        Args:
            initial_balance: Starting balance in USD
        """
        self.logger.info("=== Starting Demo Mode ===")
        self.logger.info(f"Initial Balance: ${initial_balance}")
        self.logger.info("Press Ctrl+C to stop the demo")
        
        # Create backtest engine for demo (simulating live data)
        config = BacktestEngineConfig(
            trader_id=TraderId("DEMO-001"),
            logging=LoggingConfig(log_level="INFO"),
        )
        
        engine = BacktestEngine(config)
        
        # Add simulated execution venue
        venue = Venue("SIM")
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.HEDGING,
            account_type=AccountType.MARGIN,
            base_currency=USD,
            starting_balances=[Money(initial_balance, USD)],
            default_leverage=Decimal(1),  # No leverage
        )
        
        # Add EUR/USD instrument
        EURUSD_SIM = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue)
        engine.add_instrument(EURUSD_SIM)
        
        # Generate demo data (recent data with random walks)
        demo_data = self.generate_demo_data()
        engine.add_data(demo_data)
        
        # Create and add strategy
        strategy_config = OneThreeMelihConfig(
            initial_balance=initial_balance,
        )
        strategy = OneThreeMelihStrategy(strategy_config)
        engine.add_strategy(strategy)
        
        # Run demo
        try:
            engine.run()
        except KeyboardInterrupt:
            self.logger.info("Demo stopped by user")
        
        # Print results
        self.print_backtest_results(engine)
    
    def generate_sample_data(self, start_date: str, end_date: str) -> list:
        """
        Generate sample EUR/USD data for backtesting.
        
        Args:
            start_date: Start date string
            end_date: End date string
            
        Returns:
            List of sample quote tick data
        """
        from decimal import Decimal
        import random
        from nautilus_trader.model.data import QuoteTick
        from nautilus_trader.model.objects import Price, Quantity
        from nautilus_trader.core.datetime import dt_to_unix_nanos
        
        # Parse dates
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate sample quote data
        quotes = []
        current_dt = start_dt
        base_price = Decimal("1.1000")  # Starting EUR/USD price
        
        EURUSD_SIM = TestInstrumentProvider.default_fx_ccy("EUR/USD", Venue("SIM"))
        
        while current_dt < end_dt:
            # Random walk for price movement
            price_change = Decimal(str(random.uniform(-0.002, 0.002)))
            base_price += price_change
            base_price = max(Decimal("1.0000"), min(Decimal("1.5000"), base_price))
            
            # Create bid/ask spread
            spread = Decimal("0.0001")
            bid_price = Price(base_price - spread/2, precision=5)
            ask_price = Price(base_price + spread/2, precision=5)
            
            # Create quote tick
            quote = QuoteTick(
                instrument_id=EURUSD_SIM.id,
                bid_price=bid_price,
                ask_price=ask_price,
                bid_size=Quantity(1000000, precision=0),
                ask_size=Quantity(1000000, precision=0),
                ts_event=dt_to_unix_nanos(current_dt),
                ts_init=dt_to_unix_nanos(current_dt),
            )
            quotes.append(quote)
            
            # Move to next minute
            current_dt += timedelta(minutes=1)
        
        self.logger.info(f"Generated {len(quotes)} sample quotes")
        return quotes
    
    def generate_demo_data(self) -> list:
        """Generate demo data for live simulation."""
        # Use today's data with 24 hours of quotes
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        return self.generate_sample_data(start_date, end_date)
    
    def print_backtest_results(self, engine: BacktestEngine) -> None:
        """Print comprehensive backtest results."""
        self.logger.info("=== BACKTEST RESULTS ===")
        
        # Get portfolio statistics
        portfolio = engine.trader._portfolio  # Use private attribute
        account = portfolio.account(Venue("SIM"))
        
        if account:
            self.logger.info(f"Final Account Balance: {account.balance_total()}")
            self.logger.info("Backtest completed successfully!")
        
        # Get strategy statistics if available
        for strategy in engine.trader.strategies():
            if hasattr(strategy, 'print_final_statistics'):
                strategy.print_final_statistics()


def main():
    """Main entry point for the trading bot."""
    parser = argparse.ArgumentParser(description="One-Three-Melih Trading Bot")
    parser.add_argument("--mode", choices=["demo", "backtest", "live"], 
                       default="demo", help="Execution mode")
    parser.add_argument("--start-date", type=str, default="2024-01-01",
                       help="Start date for backtest (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2024-06-01", 
                       help="End date for backtest (YYYY-MM-DD)")
    parser.add_argument("--initial-balance", type=float, default=100.0,
                       help="Initial balance in USD")
    parser.add_argument("--config", type=str, help="Configuration file path")
    
    args = parser.parse_args()
    
    runner = TradingBotRunner()
    
    try:
        if args.mode == "demo":
            runner.run_demo(args.initial_balance)
        elif args.mode == "backtest":
            runner.run_backtest(args.start_date, args.end_date, args.initial_balance)
        elif args.mode == "live":
            print("Live trading mode not implemented yet. Use demo mode for testing.")
        else:
            print(f"Unknown mode: {args.mode}")
    except Exception as e:
        logging.error(f"Error running bot: {e}")
        raise


if __name__ == "__main__":
    main()
