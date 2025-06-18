# CSV Data Loading Backtest Example

This bot demonstrates how to load price data from custom CSV files and perform backtesting using NautilusTrader framework.

## 🎯 Purpose

This bot is specifically designed for:

- **CSV Data Integration**: Learn how to load your own price data into the NautilusTrader system
- **Backtest Fundamentals**: See the simplest backtest engine setup
- **Data Wrangling**: Learn how to transform CSV data into NautilusTrader format using pandas
- **Strategy Development Basics**: Understand how to create a simple strategy class

## 📁 File Structure

```
example_01_load_bars_from_custom_csv/
├── README.md                    # This file
├── README.tr.md                # Turkish version
├── pyproject.toml              # Python project configuration
├── main.py                     # Simple entry point
├── run_example.py              # Main backtest execution script
├── strategy.py                 # Demo strategy class
└── 6EH4.XCME_1min_bars.csv    # Sample EUR/USD futures 1-minute bar data
```

## 🔧 Usage

### 1. Running the Project

```bash
# To run the project:
python run_example.py

# Or using uv:
uv run run_example.py
```

### 2. Using Your Own Data

Your CSV file should be in this format:

```csv
timestamp_utc;open;high;low;close;volume;pricetype
2024-01-01 23:01:00;1.1076;1.10785;1.1076;1.1078;205;Last
2024-01-01 23:02:00;1.10775;1.1078;1.1077;1.10775;86;Last
```

**Required columns:**
- `timestamp_utc`: UTC timestamp (YYYY-MM-DD HH:MM:SS format)
- `open`: Opening price
- `high`: Highest price
- `low`: Lowest price
- `close`: Closing price
- `volume`: Trading volume (optional)

## 📊 Code Explanation

### Main Components

#### 1. BacktestEngine Configuration
```python
engine_config = BacktestEngineConfig(
    trader_id=TraderId("BACKTEST_TRADER-001"),
    logging=LoggingConfig(log_level="DEBUG"),
)
```

#### 2. Venue (Exchange) Definition
```python
XCME = Venue("XCME")
engine.add_venue(
    venue=XCME,
    oms_type=OmsType.NETTING,
    account_type=AccountType.MARGIN,
    starting_balances=[Money(1_000_000, USD)],
    base_currency=USD,
)
```

#### 3. CSV Data Loading Process
```python
# Load CSV into pandas DataFrame
df = pd.read_csv(csv_file_path, sep=";", decimal=".")

# Transform data to NautilusTrader format
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
df = df.rename(columns={"timestamp_utc": "timestamp"})
df = df.set_index("timestamp")

# Convert to Bar objects using BarDataWrangler
wrangler = BarDataWrangler(bar_type, instrument)
bars_list = wrangler.process(df)
```

#### 4. Strategy Definition (DemoStrategy)
```python
class DemoStrategy(Strategy):
    def on_start(self):
        # Subscribe to bars at startup
        self.subscribe_bars(self.primary_bar_type)
    
    def on_bar(self, bar: Bar):
        # Runs for each new bar
        self.bars_processed += 1
```

## 🎓 Learning Points

### 1. Data Preparation
- Preparing CSV files in the correct format
- Data manipulation with pandas
- Converting timestamp formats

### 2. NautilusTrader Fundamentals
- How to set up BacktestEngine
- Venue (exchange) definitions
- Instrument (financial asset) configuration
- Money management and initial balance

### 3. Strategy Development
- Inheriting from Strategy class
- Subscribing to bar data
- Event-driven programming approach
- Logging and debugging

## 📈 Sample Output

When you run the bot, you'll see logs like this:

```
2024-06-17 10:30:00 [INFO] Strategy started at: 2024-06-17 10:30:00
2024-06-17 10:30:00 [INFO] Processed bars: 1
2024-06-17 10:30:00 [INFO] Processed bars: 2
...
2024-06-17 10:30:05 [INFO] Strategy finished at: 2024-06-17 10:30:05
2024-06-17 10:30:05 [INFO] Total bars processed: 10
```

## 🛠 Development Suggestions

To enhance this basic example, you could try:

1. **Write a Real Strategy**: Moving average crossover, RSI-based signals
2. **Add Risk Management**: Stop-loss, take-profit levels
3. **Multiple Instruments**: Multiple currency pairs or stocks
4. **Performance Analysis**: Sharpe ratio, maximum drawdown calculations
5. **Different Data Sources**: Different CSV formats, APIs

## 🔗 Related Resources

- [NautilusTrader Documentation](https://docs.nautilustrader.io/)
- [Backtest Engine Guide](https://docs.nautilustrader.io/guides/backtest.html)
- [Strategy Development](https://docs.nautilustrader.io/guides/strategy.html)
- [Data Wrangling](https://docs.nautilustrader.io/guides/data.html)

## ⚠️ Notes

- This example is for educational purposes only, do not use directly for real trading
- The sample dataset is very small, use larger datasets for real backtests
- The strategy doesn't place any trade orders, it only demonstrates data processing
- Always add risk management when developing real strategies

---

**This bot is an excellent starting point for CSV data integration and backtest fundamentals in NautilusTrader! 🚀**
