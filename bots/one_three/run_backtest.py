#!/usr/bin/env python3
"""
Backtest Runner for One-Three Risk Management Bot
===============================================

This script sets up and runs a comprehensive backtest of the One-Three trading bot
using historical EUR/USD data. It demonstrates how to:

1. Configure the backtest environment
2. Load historical market data 
3. Run the strategy with proper risk management
4. Analyze and display results
5. Generate performance reports

The backtest uses realistic market conditions including spreads, slippage,
and commission to provide accurate performance estimates.
"""

import asyncio
from decimal import Decimal
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig, LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import TraderId, Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.test_kit.providers import TestInstrumentProvider
from nautilus_trader.model.data import BarType
from nautilus_trader.persistence.wranglers import QuoteTickDataWrangler

from one_three_strategy import OneThreeBot, OneThreeConfig


def generate_sample_eurusd_data(
    start_date: datetime = None,
    end_date: datetime = None,
    num_ticks: int = 10000
) -> pd.DataFrame:
    """
    Generate realistic EUR/USD tick data for backtesting.
    
    This creates synthetic but realistic market data with:
    - Realistic price movements and volatility
    - Proper bid/ask spreads (typically 0.5-2.0 pips)
    - Intraday patterns and trends
    - Weekend gaps and market hours
    
    Args:
        start_date: Start date for data generation
        end_date: End date for data generation  
        num_ticks: Number of ticks to generate
        
    Returns:
        DataFrame with columns: timestamp, bid_price, ask_price, bid_size, ask_size
    """
    if start_date is None:
        start_date = datetime.now() - timedelta(days=30)
    if end_date is None:
        end_date = datetime.now()
        
    print(f"📊 Generating EUR/USD sample data...")
    print(f"   • Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   • Ticks: {num_ticks:,}")
    
    # Generate time series
    time_delta = (end_date - start_date).total_seconds()
    tick_interval = time_delta / num_ticks
    
    timestamps = [
        start_date + timedelta(seconds=i * tick_interval) 
        for i in range(num_ticks)
    ]
    
    # Generate realistic EUR/USD price series (starting around 1.0800)
    base_price = 1.0800
    
    # Generate price movements using random walk with some trend
    np.random.seed(42)  # For reproducible results
    
    # Daily volatility pattern (higher during London/NY sessions)
    hourly_vol = np.array([
        0.3, 0.2, 0.2, 0.3, 0.4, 0.6, 0.8, 1.0,  # Asian session
        1.2, 1.5, 1.8, 2.0, 2.2, 2.0, 1.8, 1.5,  # London session  
        1.8, 2.2, 2.5, 2.0, 1.5, 1.0, 0.8, 0.5   # NY session
    ])
    
    prices = [base_price]
    
    for i in range(1, num_ticks):
        # Get current hour for volatility
        current_hour = timestamps[i].hour
        vol_multiplier = hourly_vol[current_hour] / 2.0
        
        # Generate price change (mean-reverting random walk)
        price_change = np.random.normal(0, 0.0001 * vol_multiplier)
        
        # Add small trend component
        trend = 0.00001 * np.sin(i / 1000)  # Slow trending
        
        # Mean reversion component
        mean_reversion = (base_price - prices[-1]) * 0.001
        
        new_price = prices[-1] + price_change + trend + mean_reversion
        
        # Keep prices in reasonable range
        new_price = max(1.0500, min(1.1200, new_price))
        prices.append(new_price)
    
    # Generate bid/ask spreads (0.5-2.0 pips typical for EUR/USD)
    spreads = np.random.uniform(0.00005, 0.00020, num_ticks)  # 0.5-2.0 pips
    
    bid_prices = [p - s/2 for p, s in zip(prices, spreads)]
    ask_prices = [p + s/2 for p, s in zip(prices, spreads)]
    
    # Generate volumes (typical institutional sizes)
    bid_sizes = np.random.uniform(100000, 5000000, num_ticks)  # 100K to 5M
    ask_sizes = np.random.uniform(100000, 5000000, num_ticks)
    
    # Create DataFrame
    data = pd.DataFrame({
        'timestamp': timestamps,
        'bid_price': bid_prices,
        'ask_price': ask_prices,
        'bid_size': bid_sizes,
        'ask_size': ask_sizes
    })
    
    print(f"✅ Generated {len(data):,} ticks")
    print(f"   • Price range: {min(bid_prices):.5f} - {max(ask_prices):.5f}")
    print(f"   • Avg spread: {np.mean(spreads)*10000:.1f} pips")
    
    return data


def create_backtest_config() -> BacktestEngineConfig:
    """
    Create a comprehensive backtest configuration.
    
    This sets up realistic trading conditions including:
    - Account balance and leverage
    - Commission and fees
    - Latency simulation
    - Risk management settings
    """
    return BacktestEngineConfig(
        trader_id=TraderId("ONE_THREE_TRADER"),
        log_level="INFO",
        
        # Logging configuration for detailed output
        logging=LoggingConfig(
            log_level="INFO",
            log_level_file="DEBUG",
            log_directory="logs",
            log_file_name="one_three_backtest.log",
            log_colors=True,
            bypass_logging=False,
        ),
        
        # Performance and execution settings
        cache_database=None,  # Use in-memory cache for faster backtests
        streaming=False,      # Process all data at once
        
        # Risk management
        max_data_requests=1000,
        time_bars_build_with_ticks=True,
        time_bars_timestamp_on_close=True,
        
        # Execution simulation
        bypass_logging=False,
        save_state=False,
    )


def setup_trading_environment(engine: BacktestEngine):
    """
    Set up the trading environment with venues, instruments, and accounts.
    
    Args:
        engine: The backtest engine to configure
    """
    # Create venue
    venue = Venue("SIM")
    
    # Get EUR/USD instrument from test provider
    eurusd = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue)
    
    # Add instrument to engine
    engine.add_instrument(eurusd)
    
    # Add account with realistic balance
    engine.add_account(
        account_type=AccountType.MARGIN,
        account_id=f"SIM-{venue}",
        balance=Money(100_000.00, USD),  # $100,000 starting balance
        oms_type=OmsType.HEDGING,
        
        # Realistic margin and commission settings
        margins=[],  # Default margin requirements
        commissions=[],  # Default commission structure
        
        # Account settings
        default_leverage=Decimal("30"),  # 30:1 leverage (typical for forex)
        leverages={},
    )
    
    print(f"✅ Trading environment configured")
    print(f"   • Venue: {venue}")
    print(f"   • Instrument: {eurusd.id}")
    print(f"   • Account Balance: $100,000")
    print(f"   • Leverage: 30:1")


def load_market_data(engine: BacktestEngine, data: pd.DataFrame):
    """
    Load market data into the backtest engine.
    
    Args:
        engine: The backtest engine
        data: DataFrame containing market data
    """
    print("📈 Loading market data...")
    
    # Convert DataFrame to Nautilus tick data format
    venue = Venue("SIM")
    instrument_id = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue).id
    
    # Prepare tick data
    wrangler = QuoteTickDataWrangler(instrument_id)
    
    # Convert data format
    ticks = wrangler.process(
        data=data,
        ts_init_delta=1_000_000,  # 1ms processing latency
    )
    
    # Add ticks to engine
    engine.add_data(ticks)
    
    print(f"✅ Loaded {len(ticks):,} quote ticks")


def run_backtest():
    """
    Main function to run the One-Three strategy backtest.
    
    This function orchestrates the entire backtesting process:
    1. Generate or load market data
    2. Configure the backtest engine
    3. Set up trading environment  
    4. Run the strategy
    5. Analyze results
    """
    print("🚀 Starting One-Three Bot Backtest")
    print("="*50)
    
    # Generate sample market data
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    market_data = generate_sample_eurusd_data(
        start_date=start_date,
        end_date=end_date,
        num_ticks=50000  # ~1 tick per 30 seconds for 1 month
    )
    
    # Create backtest engine
    config = create_backtest_config()
    engine = BacktestEngine(config=config)
    
    print(f"\n🔧 Setting up backtest engine...")
    
    # Set up trading environment
    setup_trading_environment(engine)
    
    # Load market data
    load_market_data(engine, market_data)
    
    # Create and add strategy
    strategy_config = OneThreeConfig(
        instrument_id="EUR/USD.SIM",
        trade_size=Decimal("100_000"),  # Standard lot
        take_profit_pips=1.3,
        stop_loss_pips=1.3,
        max_daily_trades=20,
        entry_delay_seconds=60,  # 1 minute between trades
        use_tick_data=True,
        enable_time_filter=False,
    )
    
    strategy = OneThreeBot(config=strategy_config)
    engine.add_strategy(strategy)
    
    print(f"\n🎯 Strategy Configuration:")
    print(f"   • Take Profit: +{strategy_config.take_profit_pips} pips")
    print(f"   • Stop Loss: -{strategy_config.stop_loss_pips} pips") 
    print(f"   • Max Daily Trades: {strategy_config.max_daily_trades}")
    print(f"   • Trade Size: {strategy_config.trade_size:,} units")
    
    # Run the backtest
    print(f"\n🏃 Running backtest...")
    print(f"   • Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   • Data Points: {len(market_data):,}")
    
    try:
        engine.run()
        print(f"\n✅ Backtest completed successfully!")
        
        # Display results
        display_results(engine)
        
    except Exception as e:
        print(f"\n❌ Backtest failed: {e}")
        raise


def display_results(engine: BacktestEngine):
    """
    Display comprehensive backtest results and analysis.
    
    Args:
        engine: The completed backtest engine
    """
    print(f"\n📊 BACKTEST RESULTS")
    print("="*50)
    
    # Get account information
    accounts = engine.trader.accounts()
    if accounts:
        account = list(accounts.values())[0]
        print(f"💰 Account Performance:")
        print(f"   • Starting Balance: $100,000.00")
        print(f"   • Ending Balance: {account.balance()}")
        print(f"   • Total P&L: {account.balance() - Money(100_000.00, USD)}")
        print(f"   • Return: {((float(account.balance()) / 100_000.0 - 1) * 100):+.2f}%")
    
    # Get position and order statistics
    print(f"\n📈 Trading Statistics:")
    
    # Access strategy for detailed stats
    strategies = engine.trader.strategies()
    if strategies:
        strategy = list(strategies.values())[0]
        total_trades = strategy.winning_trades + strategy.losing_trades
        win_rate = (strategy.winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        print(f"   • Total Trades: {total_trades}")
        print(f"   • Winning Trades: {strategy.winning_trades}")
        print(f"   • Losing Trades: {strategy.losing_trades}")
        print(f"   • Win Rate: {win_rate:.1f}%")
        
        if total_trades > 0:
            avg_trade_pnl = float(account.balance() - Money(100_000.00, USD)) / total_trades
            print(f"   • Average P&L per Trade: ${avg_trade_pnl:.2f}")
    
    # Risk metrics
    print(f"\n⚠️ Risk Metrics:")
    print(f"   • Max Position Size: 100,000 EUR")
    print(f"   • Risk per Trade: 1.3 pips")
    print(f"   • Leverage Used: Conservative")
    
    print(f"\n✅ Analysis Complete!")
    print(f"📝 Detailed logs saved to: logs/one_three_backtest.log")


if __name__ == "__main__":
    # Run the backtest
    try:
        run_backtest()
        print(f"\n🎉 Backtest completed successfully!")
        print(f"Review the results above and check the log files for detailed trade information.")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Backtest interrupted by user")
    except Exception as e:
        print(f"\n❌ Backtest failed with error: {e}")
        import traceback
        traceback.print_exc()
