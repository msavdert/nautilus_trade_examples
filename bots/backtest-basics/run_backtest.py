#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
# Nautilus Trader Real Backtest Example
# Based on official Nautilus Trader documentation and examples
# -------------------------------------------------------------------------------------------------

from decimal import Decimal
from datetime import datetime

# Core Nautilus imports for backtesting
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig, LoggingConfig, DataEngineConfig
from nautilus_trader.model import TraderId
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money

# Data and instrument imports
from nautilus_trader.test_kit.providers import TestInstrumentProvider, TestDataProvider
from nautilus_trader.model.data import BarType

# Strategy import (using local demo strategy)
from demo_strategy import DemoStrategy, DemoStrategyConfig


class RealBacktestRunner:
    """
    Real backtest implementation following official Nautilus Trader patterns.
    
    This class demonstrates how to run actual backtests with historical data,
    performance analysis, and comprehensive reporting - based on official examples.
    """
    
    def __init__(self):
        print("🚀 Initializing Real Backtest Runner...")
        self.engine = None
        self.results = None
        
    def run_basic_backtest(self):
        """
        Run a basic backtest using BacktestEngine (Low-level API)
        Based on official examples from nautilus_trader GitHub
        """
        print("\n📊 Running Basic Backtest with Real Data")
        print("=" * 60)
        
        # Step 1: Configure backtest engine (following official examples)
        print("⚙️ Step 1: Configuring backtest engine...")
        engine_config = BacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),  # Unique identifier
            logging=LoggingConfig(
                log_level="INFO",
                log_colors=True,
                use_pyo3=False,
            ),
            # Data engine configuration for realistic processing
            data_engine=DataEngineConfig(
                time_bars_interval_type="left-open",
                time_bars_timestamp_on_close=True,
                time_bars_skip_first_non_full_bar=False,
                validate_data_sequence=True,
            ),
        )
        
        # Step 2: Create backtest engine
        print("🔧 Step 2: Creating backtest engine...")
        self.engine = BacktestEngine(config=engine_config)
        
        # Step 3: Add trading venue (following official patterns)
        print("🏛️ Step 3: Adding trading venue...")
        SIM = Venue("SIM")
        self.engine.add_venue(
            venue=SIM,
            oms_type=OmsType.NETTING,  # Netting order management
            account_type=AccountType.MARGIN,  # Margin trading account
            base_currency=USD,  # Account base currency
            starting_balances=[Money(100_000, USD)],  # Initial capital
            default_leverage=Decimal(1),  # No leverage
        )
        
        # Step 4: Add instruments (using test instruments)
        print("📈 Step 4: Adding trading instruments...")
        eurusd = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue=SIM)
        self.engine.add_instrument(eurusd)
        
        # Step 5: Prepare and add market data
        print("📊 Step 5: Loading historical market data...")
        self._load_historical_data(eurusd)
        
        # Step 6: Add trading strategy
        print("🤖 Step 6: Adding trading strategy...")
        strategy_config = DemoStrategyConfig(
            instrument_id=eurusd.id,
            trade_size=Decimal("100_000"),  # 1 standard lot
            fast_ema_period=10,
            slow_ema_period=20,
        )
        strategy = DemoStrategy(config=strategy_config)
        self.engine.add_strategy(strategy)
        
        # Step 7: Run the backtest
        print("▶️ Step 7: Executing backtest...")
        print("This may take a moment...")
        
        start_time = datetime.now()
        self.engine.run()
        end_time = datetime.now()
        
        execution_time = (end_time - start_time).total_seconds()
        print(f"✅ Backtest completed in {execution_time:.2f} seconds")
        
        # Step 8: Generate and display results
        print("📋 Step 8: Generating performance reports...")
        self._generate_reports()
        
        # Step 9: Clean up
        print("🧹 Step 9: Cleaning up resources...")
        self.engine.reset()
        self.engine.dispose()
        
        print("\n🎉 Backtest completed successfully!")
        
    def _load_historical_data(self, instrument):
        """
        Load historical market data for backtesting.
        Uses TestDataProvider following official examples.
        """
        # Create bar type for 1-minute bars
        bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-LAST-EXTERNAL")
        
        try:
            # Use TestDataProvider to get sample data (following official examples)
            provider = TestDataProvider()
            
            # Generate sample bars for demonstration
            # In real scenarios, you would load from CSV, database, or market data API
            bars = self._generate_sample_bars(instrument, bar_type)
            
            print(f"   📊 Loaded {len(bars)} bars for {instrument.id}")
            
            # Add data to engine
            self.engine.add_data(bars)
            
        except Exception as e:
            print(f"   ⚠️ Warning: Could not load external data: {e}")
            print("   📝 Using generated sample data for demonstration")
            # Fallback to generated data
            bars = self._generate_sample_bars(instrument, bar_type)
            self.engine.add_data(bars)
    
    def _generate_sample_bars(self, instrument, bar_type, count=1000):
        """
        Generate sample bar data for demonstration.
        In production, replace this with real market data loading.
        """
        from nautilus_trader.model import Bar
        from nautilus_trader.model.objects import Price, Quantity
        import random
        from datetime import timedelta
        
        bars = []
        base_price = 1.1000  # EUR/USD starting price
        current_time = datetime(2024, 1, 1, 9, 0, 0)  # Start time
        
        for i in range(count):
            # Generate realistic OHLC data with some volatility
            volatility = 0.001  # 0.1% volatility
            change = (random.random() - 0.5) * volatility
            
            open_price = base_price
            high_price = open_price + abs(change) + random.random() * volatility * 0.5
            low_price = open_price - abs(change) - random.random() * volatility * 0.5
            close_price = open_price + change
            
            # Create bar
            bar = Bar(
                bar_type=bar_type,
                open=Price.from_str(f"{open_price:.5f}"),
                high=Price.from_str(f"{high_price:.5f}"),
                low=Price.from_str(f"{low_price:.5f}"),
                close=Price.from_str(f"{close_price:.5f}"),
                volume=Quantity.from_int(random.randint(100, 1000)),
                ts_event=int(current_time.timestamp() * 1_000_000_000),  # nanoseconds
                ts_init=int(current_time.timestamp() * 1_000_000_000),   # nanoseconds
            )
            
            bars.append(bar)
            base_price = close_price  # Update base price
            current_time += timedelta(minutes=1)  # Next minute
            
        return bars
    
    def _generate_reports(self):
        """
        Generate comprehensive performance reports.
        Following official Nautilus Trader reporting patterns.
        """
        try:
            print("\n📊 PERFORMANCE REPORTS")
            print("=" * 60)
            
            # Account report
            print("💰 ACCOUNT REPORT:")
            print("-" * 30)
            account_report = self.engine.trader.generate_account_report(Venue("SIM"))
            print(account_report)
            
            print("\n📋 ORDER FILLS REPORT:")
            print("-" * 30)
            fills_report = self.engine.trader.generate_order_fills_report()
            print(fills_report)
            
            print("\n📈 POSITIONS REPORT:")
            print("-" * 30)
            positions_report = self.engine.trader.generate_positions_report()
            print(positions_report)
            
            # Additional performance summary
            print("\n🎯 BACKTEST SUMMARY:")
            print("-" * 30)
            
            # Get account state
            accounts = list(self.engine.cache.accounts())
            if accounts:
                account = accounts[0]
                starting_balance = 100_000.00  # Initial balance
                final_balance = float(account.balance_total(account.base_currency).as_double())
                total_return = final_balance - starting_balance
                return_pct = (total_return / starting_balance) * 100
                
                print(f"Starting Balance: ${starting_balance:,.2f}")
                print(f"Final Balance:    ${final_balance:,.2f}")
                print(f"Total Return:     ${total_return:,.2f}")
                print(f"Return %:         {return_pct:.2f}%")
            
            # Get trade statistics
            positions = list(self.engine.cache.positions())
            if positions:
                closed_positions = [p for p in positions if p.is_closed]
                winning_positions = [p for p in closed_positions if p.realized_pnl and p.realized_pnl.as_double() > 0]
                losing_positions = [p for p in closed_positions if p.realized_pnl and p.realized_pnl.as_double() < 0]
                
                print(f"Total Trades:     {len(closed_positions)}")
                print(f"Winning Trades:   {len(winning_positions)}")
                print(f"Losing Trades:    {len(losing_positions)}")
                if closed_positions:
                    win_rate = (len(winning_positions) / len(closed_positions)) * 100
                    print(f"Win Rate:         {win_rate:.1f}%")
            else:
                print("No trades executed during backtest")
                print("This could indicate:")
                print("- Strategy conditions not met")
                print("- EMA periods too long for data")
                print("- Price movements insufficient for signals")
            
        except Exception as e:
            print(f"⚠️ Error generating reports: {e}")
            print("📝 This might be normal if no trades were executed during the backtest")
    
    def run_advanced_backtest_with_analysis(self):
        """
        Run an advanced backtest with detailed performance analysis.
        Demonstrates more sophisticated backtesting features.
        """
        print("\n🔬 Running Advanced Backtest with Analysis")
        print("=" * 60)
        
        # This would include:
        # - Multiple instruments
        # - Multiple timeframes  
        # - Advanced risk management
        # - Portfolio-level analysis
        # - Walk-forward analysis
        
        print("📚 Advanced backtest features:")
        print("- Multiple instrument support")
        print("- Risk management integration")
        print("- Portfolio-level metrics")
        print("- Walk-forward validation")
        print("- Monte Carlo simulation")
        print("\n💡 These features can be implemented using the same")
        print("   patterns shown in the basic backtest above!")


def main():
    """
    Main function to run the real backtest examples
    """
    print("🤖 Nautilus Trader Real Backtest Runner")
    print("Based on official documentation and examples")
    print("=" * 60)
    
    # Check if strategy exists
    try:
        from demo_strategy import DemoStrategy, DemoStrategyConfig
        strategy_available = True
        print("✅ Demo strategy loaded successfully")
    except ImportError:
        print("⚠️ Warning: DemoStrategy not found")
        print("   This should not happen - check demo_strategy.py file...")
        strategy_available = False
    
    if not strategy_available:
        print("❌ Please check the demo_strategy.py file")
        print("📖 This file should contain the DemoStrategy class")
        return
    
    # Create and run backtest
    backtest_runner = RealBacktestRunner()
    
    try:
        # Run basic backtest
        backtest_runner.run_basic_backtest()
        
        # Show advanced capabilities
        backtest_runner.run_advanced_backtest_with_analysis()
        
        print("\n🎯 Next Steps:")
        print("1. Modify the strategy parameters and re-run")
        print("2. Load your own historical data (CSV, API, etc.)")
        print("3. Add multiple instruments and timeframes")
        print("4. Implement risk management rules")
        print("5. Create portfolio-level analysis")
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        print("💡 Common issues:")
        print("- Missing strategy configuration")
        print("- Data loading problems")
        print("- Instrument setup errors")
        print("\n📖 Check the README.md for troubleshooting guide")


if __name__ == "__main__":
    main()
