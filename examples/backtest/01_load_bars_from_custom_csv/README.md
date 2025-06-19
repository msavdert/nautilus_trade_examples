# CSV Data Loading Backtest Example

This project demonstrates how to download CSV financial data and perform backtesting using NautilusTrader framework with automatic data downloading and format conversion.

## 🎯 Purpose

This example shows you how to:

- **Automatic Data Download**: Download financial data from Yahoo Finance automatically
- **CSV Data Integration**: Load your own price data into NautilusTrader
- **Data Format Conversion**: Convert downloaded data to NautilusTrader format
- **Backtest Fundamentals**: Set up a simple backtest engine
- **Strategy Development**: Create a moving average crossover trading strategy

## 📁 File Structure

```
01_load_bars_from_custom_csv/
├── README.md                    # This file (English)
├── README.tr.md                 # Turkish version
├── pyproject.toml              # Python project configuration
├── main.py                     # Main program (data download + backtest)
├── strategy.py                 # Moving Average crossover strategy
├── download_data.py            # Standalone data download utilities
└── data/                       # Directory for CSV files (auto-created)
    └── EURUSD_1min.csv        # Downloaded EUR/USD 1-minute data
```

## 🚀 Quick Start (Fully Automatic)

This example is designed to work completely automatically. Just run:

```bash
python main.py
```

The program will automatically:
1. **Download data**: Download last 7 days of EUR/USD data from Yahoo Finance
2. **Format conversion**: Convert data to NautilusTrader format
3. **Run backtest**: Test the Moving Average crossover strategy
4. **Show results**: Display performance statistics

## 📥 Automatic Data Download System

### Data Download Function in main.py

The `download_sample_data()` function in `main.py` performs these operations:

```python
def download_sample_data():
    """Download sample EUR/USD data using Yahoo Finance if data folder is empty."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)  # Create data directory
    
    csv_file = data_dir / "EURUSD_1min.csv"
    
    # Use existing file if available
    if csv_file.exists():
        print(f"✅ Using existing data file: {csv_file}")
        return str(csv_file)
    
    print("📥 Downloading sample EUR/USD data from Yahoo Finance...")
    
    import yfinance as yf
    
    # Download EUR/USD data (last 7 days, 1-minute intervals)
    ticker = "EURUSD=X"
    data = yf.download(ticker, period="7d", interval="1m", progress=False)
    
    # Convert to NautilusTrader format
    data.reset_index(inplace=True)
    data["timestamp_utc"] = data["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Select and rename required columns
    result_data = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
    result_data.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
    
    # Clean NaN values
    result_data = result_data.dropna()
    
    # Save as CSV with semicolon delimiter
    result_data.to_csv(csv_file, sep=";", index=False)
    
    print(f"✅ Downloaded {len(result_data)} bars to {csv_file}")
    return str(csv_file)
```

### Data Download Process Details

1. **Directory Check**: Creates `data/` directory if it doesn't exist
2. **File Check**: Skips download if `EURUSD_1min.csv` already exists
3. **Yahoo Finance Connection**: Connects using `yfinance` library
4. **Data Download**: Downloads last 7 days of 1-minute EUR/USD data
5. **Format Conversion**: Converts to NautilusTrader-compatible format
6. **Save**: Saves as CSV with semicolon (`;`) delimiter

## 🛠️ Advanced Data Download with download_data.py

The `download_data.py` script provides additional utilities for different data sources and formats. This standalone script offers more flexibility and advanced features compared to the basic download function in `main.py`.

### Available Commands

```bash
# Download from Yahoo Finance with custom parameters
python download_data.py yahoo EURUSD=X 7d 1m

# Download from Alpha Vantage (requires free API key)
python download_data.py alphavantage EUR USD your_api_key

# Convert HistData.com format to NautilusTrader format
python download_data.py convert histdata_raw.csv data/EURUSD_1min.csv

# Validate CSV format for NautilusTrader compatibility
python download_data.py validate data/EURUSD_1min.csv
```

### download_data.py Script Features

The script contains several utility functions:

1. **`download_yahoo_data()`**: Enhanced Yahoo Finance download with error handling
2. **`download_alpha_vantage_data()`**: Support for Alpha Vantage API
3. **`convert_histdata_format()`**: Convert HistData.com tick data to OHLC bars
4. **`validate_csv_format()`**: Validate CSV files for NautilusTrader compatibility

### Yahoo Finance Download Function

```python
def download_yahoo_data(symbol: str = "EURUSD=X", period: str = "7d", interval: str = "1m"):
    """
    Download data from Yahoo Finance with comprehensive error handling.
    
    Available symbols: EURUSD=X, GBPUSD=X, USDJPY=X, BTCUSD=X, AAPL, ^GSPC
    Available periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    Available intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo
    """
    import yfinance as yf
    
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    
    # Handle different datetime column names
    datetime_col = "Datetime" if "Datetime" in data.columns else "Date"
    data.reset_index(inplace=True)
    data["timestamp_utc"] = data[datetime_col].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Select and rename columns to NautilusTrader format
    result = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
    result.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
    
    return result.dropna()
```

### HistData.com Format Conversion

The script can convert HistData.com tick data (format: `YYYYMMDD HHMMSSMMM,bid,ask`) to OHLC bars:

```python
def convert_histdata_format(input_file: str, output_file: str):
    """Convert HistData.com tick format to NautilusTrader OHLC format."""
    
    # Read tick data: YYYYMMDD HHMMSSMMM,bid_price,ask_price
    df = pd.read_csv(input_file, header=None, names=['timestamp', 'bid', 'ask'])
    
    # Convert timestamp format and calculate mid price
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d %H%M%S%f')
    df['mid'] = (df['bid'] + df['ask']) / 2
    
    # Resample tick data to 1-minute OHLC bars
    df.set_index('timestamp', inplace=True)
    ohlc = df['mid'].resample('1min').ohlc()
    ohlc['volume'] = 100  # Add dummy volume for forex data
    
    # Format for NautilusTrader
    ohlc.reset_index(inplace=True)
    ohlc['timestamp_utc'] = ohlc['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Save in NautilusTrader format
    result = ohlc[['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']]
    result.to_csv(output_file, sep=';', index=False)
```

## 📋 NautilusTrader CSV Format Requirements

NautilusTrader requires a specific CSV format for historical data:

```csv
timestamp_utc;open;high;low;close;volume
2024-12-01 23:01:00;1.1076;1.10785;1.1076;1.1078;205
2024-12-01 23:02:00;1.10775;1.1078;1.1077;1.10775;86
2024-12-01 23:03:00;1.10775;1.1079;1.1077;1.10785;142
```

### Format Requirements

- **Column Names**: Exactly `timestamp_utc`, `open`, `high`, `low`, `close`, `volume`
- **Delimiter**: Use semicolon (`;`) as field separator
- **Decimal Separator**: Use dot (`.`) for decimal numbers
- **Timestamp Format**: `YYYY-MM-DD HH:MM:SS` in UTC timezone
- **Data Order**: Must be sorted by timestamp (ascending)
- **Headers**: First row must contain column names

### Data Validation

The `download_data.py` script includes a validation function:

```python
def validate_csv_format(csv_file: str):
    """Validate CSV file format for NautilusTrader compatibility."""
    
    df = pd.read_csv(csv_file, sep=';')
    
    # Check required columns
    required_columns = ['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False
    
    # Validate timestamp format
    try:
        pd.to_datetime(df['timestamp_utc'])
    except:
        print("❌ Invalid timestamp format")
        return False
    
    # Check numeric columns
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"❌ Column '{col}' is not numeric")
            return False
    
    print("✅ CSV format is valid for NautilusTrader")
    return True
```

## 🔄 Data Format Conversion Process

### From Yahoo Finance to NautilusTrader

The conversion process transforms Yahoo Finance data structure:

```python
# Yahoo Finance raw format (pandas DataFrame after download):
#    Datetime                   Open     High     Low      Close    Volume
# 0  2024-12-01 23:01:00+00:00  1.1076  1.10785  1.1076   1.1078   205
# 1  2024-12-01 23:02:00+00:00  1.10775 1.1078   1.1077   1.10775  86

# Step 1: Reset index and format timestamp
data.reset_index(inplace=True)
data["timestamp_utc"] = data["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Step 2: Select and rename columns
result = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
result.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]

# Step 3: Clean data and save
result = result.dropna()  # Remove any NaN values
result.to_csv("data/EURUSD_1min.csv", sep=";", index=False)

# Final NautilusTrader format:
# timestamp_utc;open;high;low;close;volume
# 2024-12-01 23:01:00;1.1076;1.10785;1.1076;1.1078;205
# 2024-12-01 23:02:00;1.10775;1.1078;1.1077;1.10775;86
```

### Data Loading in NautilusTrader

The converted CSV data is loaded into NautilusTrader using the BarDataWrangler:

```python
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.model.data import BarType

# Read the CSV file
df = pd.read_csv("data/EURUSD_1min.csv", sep=";")

# Convert timestamp to datetime and set as index
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
df = df.set_index("timestamp_utc")

# Create bar type for EUR/USD 1-minute bars
bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-MID-EXTERNAL")

# Create wrangler and process data
wrangler = BarDataWrangler(bar_type, instrument)
bars: list[Bar] = wrangler.process(df)

# Add bars to backtest engine
engine.add_data(bars)
```

## 🎮 Understanding the Trading Strategy

The example strategy (`strategy.py`) implements a simple Moving Average crossover system:

### Strategy Components

```python
class SimpleStrategy(Strategy):
    def __init__(self, bar_type, trade_size, fast_ma_period=10, slow_ma_period=20):
        super().__init__()
        
        # Strategy parameters
        self.bar_type = bar_type
        self.instrument_id = bar_type.instrument_id
        self.trade_size = trade_size
        
        # Technical indicators
        self.fast_ma = SimpleMovingAverage(fast_ma_period)  # 10-period MA
        self.slow_ma = SimpleMovingAverage(slow_ma_period)  # 20-period MA
        
        # Strategy state tracking
        self.last_signal = None
        self.trades_count = 0
```

### Trading Logic

The strategy implements the following rules:

```python
def on_bar(self, bar: Bar):
    """Called for each new price bar."""
    
    # Update moving averages with new price data
    self.fast_ma.update_raw(bar.close)
    self.slow_ma.update_raw(bar.close)
    
    # Wait for indicators to initialize (need at least 20 bars)
    if not (self.fast_ma.initialized and self.slow_ma.initialized):
        return
    
    # Determine current market signal
    fast_value = self.fast_ma.value
    slow_value = self.slow_ma.value
    
    if fast_value > slow_value:
        current_signal = "BUY"    # Fast MA above slow MA = bullish
    elif fast_value < slow_value:
        current_signal = "SELL"   # Fast MA below slow MA = bearish
    else:
        current_signal = None     # No clear signal
    
    # Execute trades only on signal changes
    if current_signal != self.last_signal and current_signal is not None:
        self._execute_signal(current_signal, bar)
        self.last_signal = current_signal
```

### Position Management

```python
def _execute_signal(self, signal: str, bar: Bar):
    """Execute trading signal with position management."""
    
    # Check current position
    positions = self.cache.positions_open(instrument_id=self.instrument_id)
    position = positions[0] if positions else None
    
    if signal == "BUY":
        if position is None or position.is_closed:
            # Open new long position
            self._place_market_order(OrderSide.BUY, bar.close)
        elif position.is_short:
            # Close short and open long
            self._close_position(position)
            self._place_market_order(OrderSide.BUY, bar.close)
    
    elif signal == "SELL":
        if position is None or position.is_closed:
            # Open new short position
            self._place_market_order(OrderSide.SELL, bar.close)
        elif position.is_long:
            # Close long and open short
            self._close_position(position)
            self._place_market_order(OrderSide.SELL, bar.close)
```

## 🔧 Installation and Setup

### Prerequisites

```bash
# Install required packages
pip install nautilus_trader pandas yfinance requests

# Alternative: using uv (faster package manager)
uv add nautilus_trader pandas yfinance requests
```

### Running the Example

```bash
# Navigate to the example directory
cd examples/backtest/01_load_bars_from_custom_csv/

# Option 1: Run complete automated example
python main.py

# Option 2: Use download_data.py for custom data download
python download_data.py yahoo EURUSD=X 1mo 5m  # Download 1 month of 5-minute data
python main.py                                  # Then run backtest

# Option 3: Download and convert HistData
python download_data.py convert histdata_file.csv data/converted.csv
python main.py
```

## 📊 Alternative Data Sources

### 1. Yahoo Finance (Free, Default)

**Supported Instruments:**
```python
# Forex pairs
"EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"

# Cryptocurrencies  
"BTC-USD", "ETH-USD", "LTC-USD"

# Stock indices
"^GSPC"    # S&P 500
"^IXIC"    # NASDAQ
"^DJI"     # Dow Jones

# Individual stocks
"AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"
```

**Time Periods and Intervals:**
```python
# Available periods
periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

# Available intervals  
intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo"]
```

### 2. Alpha Vantage (Free with API Key)

```bash
# Get free API key from: https://www.alphavantage.co/support/#api-key
# 500 requests per day, 5 per minute limit

python download_data.py alphavantage EUR USD your_api_key_here
```

### 3. HistData.com (Free Manual Download)

1. Visit: https://www.histdata.com/download-free-forex-historical-data/
2. Choose currency pair and time period
3. Download ZIP file and extract CSV
4. Convert format: `python download_data.py convert downloaded_file.csv data/output.csv`

## 📈 Backtest Results Analysis

The backtest provides comprehensive performance statistics:

```
🚀 Starting CSV Data Loading Backtest Example
==================================================
📥 Downloading sample EUR/USD data from Yahoo Finance...
✅ Downloaded 2016 bars to data/EURUSD_1min.csv
📊 Data range: 2024-12-01 23:01:00 to 2024-12-07 22:59:00

🔧 Setting up backtest engine...
🔄 Converting data to NautilusTrader format...
✅ Converted 2016 bars
📈 Setting up trading strategy...

🏃 Running backtest...
==================================================

📊 Backtest Results
==================================================
💰 Starting Balance: $100,000.00
💰 Ending Balance: $101,250.00
📈 Total Return: $1,250.00
📊 Return %: 1.25%
🔄 Total Orders: 24
✅ Filled Orders: 24
📅 First Trade: 2024-12-01 08:15:00+00:00
📅 Last Trade: 2024-12-07 22:45:00+00:00

✅ Backtest completed successfully!
```

### Performance Metrics Explained

- **Starting/Ending Balance**: Account balance before and after backtest period
- **Total Return**: Absolute profit/loss in base currency (USD)
- **Return %**: Percentage return on initial capital
- **Total Orders**: All orders placed by the strategy
- **Filled Orders**: Successfully executed orders (should match total for market orders)
- **Trade Timing**: First and last trade execution timestamps

## 🔍 Troubleshooting

### Common Issues and Solutions

**1. Installation Issues**
```bash
# If pip fails, try upgrading pip first
python -m pip install --upgrade pip
pip install nautilus_trader pandas yfinance requests

# For M1/M2 Macs, you might need:
pip install --no-binary=nautilus_trader nautilus_trader
```

**2. Data Download Issues**
```bash
# Test internet connection and Yahoo Finance access
python -c "import yfinance as yf; print(yf.download('EURUSD=X', period='1d'))"

# If no data returned, try different symbol or time period
python download_data.py yahoo GBPUSD=X 5d 5m
```

**3. CSV Format Issues**
```bash
# Validate your CSV file
python download_data.py validate data/your_file.csv

# Check file content manually
head -5 data/EURUSD_1min.csv
```

**4. Strategy Issues**
```python
# Enable debug logging in main.py
engine_config = BacktestEngineConfig(
    trader_id=TraderId("BACKTEST-001"),
    logging=LoggingConfig(log_level="DEBUG"),  # Changed from INFO
)
```

**5. AttributeError Issues (Fixed)**
- The original issue with `order.is_filled` has been resolved
- Current code correctly uses `order.status` for checking order state

### Debug Mode

For detailed execution information:

```python
# In main.py, change logging level
logging=LoggingConfig(log_level="DEBUG")

# This will show:
# - Individual bar processing
# - Indicator calculations  
# - Order placements and fills
# - Position changes
```

## 📚 Next Steps and Enhancements

### 1. Parameter Optimization

```python
# Try different moving average periods
fast_periods = [5, 8, 10, 12, 15]
slow_periods = [20, 25, 30, 35, 40]

# Test different timeframes
timeframes = ["1m", "5m", "15m", "30m", "1h"]

# Test different instruments
instruments = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTCUSD=X"]
```

### 2. Strategy Enhancements

```python
# Add more indicators
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.indicators.macd import MACD

# Implement risk management
stop_loss_percent = 0.02    # 2% stop loss
take_profit_percent = 0.04  # 4% take profit

# Add position sizing
risk_per_trade = 0.01  # Risk 1% of account per trade
```

### 3. Advanced Data Sources

- **Professional Data**: Databento, Polygon.io, IEX Cloud
- **Higher Frequency**: Tick data for more precise entries
- **Multiple Assets**: Portfolio backtesting with correlation analysis
- **Alternative Data**: News sentiment, economic indicators

### 4. Production Considerations

- **Paper Trading**: Test strategies with live data but simulated trades
- **Risk Management**: Maximum drawdown limits, position size limits
- **Portfolio Management**: Multi-asset strategies, correlation analysis
- **Performance Analytics**: Sharpe ratio, maximum drawdown, win rate

## 📖 Additional Resources

- **NautilusTrader Documentation**: https://nautilustrader.io/
- **API Reference**: https://nautilustrader.io/docs/api_reference/
- **Strategy Examples**: https://github.com/nautechsystems/nautilus_trader/tree/develop/examples
- **Technical Indicators**: https://nautilustrader.io/docs/api_reference/indicators/
- **Community Discord**: https://discord.gg/nautilustrader
