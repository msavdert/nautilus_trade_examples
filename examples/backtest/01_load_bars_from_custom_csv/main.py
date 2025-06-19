#!/usr/bin/env python3
"""
Simple CSV Data Loading Backtest Example

This script demonstrates how to:
1. Load historical price data from CSV files
2. Set up a basic backtest environment
3. Run a simple trading strategy
4. View the results

For beginners learning NautilusTrader and algorithmic trading.
"""

import os
from decimal import Decimal
from pathlib import Path

import pandas as pd

from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig, LoggingConfig
from nautilus_trader.model import TraderId
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider

from strategy import SimpleStrategy


def download_sample_data():
    """Download sample EUR/USD data using Yahoo Finance if data folder is empty."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    csv_file = data_dir / "EURUSD_1h.csv"
    
    if csv_file.exists():
        print(f"✅ Using existing data file: {csv_file}")
        return str(csv_file)
    
    print("📥 Downloading sample EUR/USD data from Yahoo Finance...")
    
    try:
        import yfinance as yf
        
        # Download EUR/USD data (last 7 days, 1-minute intervals)
        ticker = "EURUSD=X"
        data = yf.download(ticker, period="7d", interval="1m", progress=False)
        
        if data.empty:
            raise ValueError("No data received from Yahoo Finance")
        
        # Convert to required format
        data.reset_index(inplace=True)
        data["timestamp_utc"] = data["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Select and rename columns
        result_data = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
        result_data.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
        
        # Remove any rows with NaN values
        result_data = result_data.dropna()
        
        # Save to CSV
        result_data.to_csv(csv_file, sep=";", index=False)
        
        print(f"✅ Downloaded {len(result_data)} bars to {csv_file}")
        print(f"📊 Data range: {result_data['timestamp_utc'].min()} to {result_data['timestamp_utc'].max()}")
        
        return str(csv_file)
        
    except ImportError:
        print("❌ yfinance not installed. Please install it with: pip install yfinance")
        print("Or create a CSV file manually in the data/ folder.")
        raise
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        print("Please check your internet connection or create a CSV file manually.")
        raise


def load_csv_data(csv_file_path: str):
    """Load and validate CSV data."""
    print(f"📖 Loading data from: {csv_file_path}")
    
    # Read CSV file
    try:
        df = pd.read_csv(csv_file_path, sep=";")
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        raise
    
    # Validate required columns
    required_columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        raise ValueError(f"CSV file must contain columns: {required_columns}")
    
    # Convert timestamp to datetime
    try:
        df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
    except Exception as e:
        print(f"❌ Error parsing timestamps: {e}")
        print("Ensure timestamp format is YYYY-MM-DD HH:MM:SS")
        raise
    
    # Sort by timestamp
    df = df.sort_values("timestamp_utc")
    
    # Set timestamp as index
    df = df.set_index("timestamp_utc")
    
    print(f"✅ Loaded {len(df)} bars")
    print(f"📊 Data range: {df.index.min()} to {df.index.max()}")
    
    return df


def main():
    """Main function to run the backtest."""
    print("🚀 Starting CSV Data Loading Backtest Example")
    print("=" * 50)
    
    # Step 1: Download or load sample data
    try:
        csv_file_path = download_sample_data()
        df = load_csv_data(csv_file_path)
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    print("\n🔧 Setting up backtest engine...")
    
    # Step 2: Configure backtest engine
    engine_config = BacktestEngineConfig(
        trader_id=TraderId("BACKTEST-001"),
        logging=LoggingConfig(log_level="INFO"),  # Set to DEBUG for more detailed logs
    )
    engine = BacktestEngine(config=engine_config)
    
    # Step 3: Add trading venue
    venue = Venue("SIM")
    engine.add_venue(
        venue=venue,
        oms_type=OmsType.NETTING,
        account_type=AccountType.MARGIN,
        starting_balances=[Money(100_000, USD)],  # Start with $100,000
        base_currency=USD,
        default_leverage=Decimal(1),  # No leverage
    )
    
    # Step 4: Create instrument
    instrument = TestInstrumentProvider.default_fx_ccy("EUR/USD", venue)
    engine.add_instrument(instrument)
    
    # Step 5: Convert data to NautilusTrader format
    print("🔄 Converting data to NautilusTrader format...")
    
    # Create bar type
    bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-MID-EXTERNAL")
    
    # Create wrangler and process data
    wrangler = BarDataWrangler(bar_type, instrument)
    bars: list[Bar] = wrangler.process(df)
    
    print(f"✅ Converted {len(bars)} bars")
    
    # Step 6: Add data to engine
    engine.add_data(bars)
    
    # Step 7: Create and add strategy
    print("📈 Setting up trading strategy...")
    strategy = SimpleStrategy(
        bar_type=bar_type,
        trade_size=Decimal("10000"),  # Trade $10,000 per position
    )
    engine.add_strategy(strategy)
    
    # Step 8: Run backtest
    print("\n🏃 Running backtest...")
    print("=" * 50)
    
    engine.run()
    
    # Step 9: Display results
    print("\n📊 Backtest Results")
    print("=" * 50)
    
    # Get account statistics
    accounts = list(engine.cache.accounts())
    if accounts:
        account = accounts[0]
        starting_balance = 100_000.0
        final_balance = float(account.balance_total(account.base_currency).as_double())
        total_return = final_balance - starting_balance
        return_pct = ((final_balance / starting_balance) - 1) * 100
        
        print(f"💰 Starting Balance: ${starting_balance:,.2f}")
        print(f"💰 Ending Balance: ${final_balance:,.2f}")
        print(f"📈 Total Return: ${total_return:,.2f}")
        print(f"📊 Return %: {return_pct:.2f}%")
    else:
        print("💰 No account data available")
    
    # Count trades
    orders = list(engine.cache.orders())
    filled_orders = [order for order in orders if hasattr(order, 'status') and str(order.status) == 'FILLED']
    
    print(f"🔄 Total Orders: {len(orders)}")
    print(f"✅ Filled Orders: {len(filled_orders)}")
    
    if filled_orders:
        print(f"📅 First Trade: {filled_orders[0].last_event.ts_event}")
        print(f"📅 Last Trade: {filled_orders[-1].last_event.ts_event}")
    
    print("\n✅ Backtest completed successfully!")
    print("\n💡 Next steps:")
    print("   - Modify the strategy in strategy.py")
    print("   - Try different timeframes or instruments")
    print("   - Add more indicators and risk management")
    print("   - Experiment with different data sources")
    
    # Clean up
    engine.dispose()


if __name__ == "__main__":
    main()
