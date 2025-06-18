# Backtest Tutorial - Complete Guide to Backtesting with Nautilus Trader

Welcome to the comprehensive guide for backtesting trading strategies with Nautilus Trader! This tutorial teaches you everything you need to know about testing your strategies on historical data.

## 🎯 What You'll Learn

This guide covers:
- Three different approaches to backtesting
- How to use historical market data
- Performance analysis and optimization
- Best practices for reliable backtesting
- Real-world examples and use cases

## 📚 Prerequisites

Before starting, ensure you have:
- Completed the [my-first-bot tutorial](../my-first-bot/)
- Docker and Nautilus Trader environment running  
- Basic understanding of trading concepts
- Historical market data (we'll show you how to get this)

## 🚀 Project Setup

**Important**: All commands must be run inside the Docker container using `docker exec`.

Start by creating the backtest project in the Docker environment:

```bash
# 1. Ensure Docker environment is running (from project root)
docker-compose up -d

# 2. Create new backtest project
docker exec -it nautilus-trader bash -c "cd /workspace/bots/ && uv init backtest"

# 3. Add required dependencies  
docker exec -it nautilus-trader bash -c "cd /workspace/bots/backtest && uv add nautilus_trader pandas"
```

These commands will:
1. Create a new project structure for backtesting
2. Add `nautilus_trader` for the backtesting framework
3. Add `pandas` for data analysis and manipulation

### 📝 Project Structure After Setup

```
backtest/
├── pyproject.toml          # Project configuration and dependencies
├── README.md              # This comprehensive guide
├── main.py                # Complete backtest tutorial and concepts
├── run_backtest.py        # Real backtest implementation with actual data
├── data/                  # Directory for historical market data
├── results/               # Directory for backtest results
└── uv.lock               # Dependency lock file
```

## 📚 Two Approaches: Tutorial vs Real Implementation

This project provides two complementary files:

### 1. **main.py** - Educational Tutorial
- **Purpose**: Learn backtest concepts and theory
- **Content**: Detailed explanations and code examples
- **Execution**: Prints educational content, no actual backtesting
- **Use when**: You want to understand how backtesting works

### 2. **run_backtest.py** - Real Implementation  
- **Purpose**: Run actual backtests with historical data
- **Content**: Production-ready backtest code based on official examples
- **Execution**: Performs real backtests and generates performance reports
- **Use when**: You want to test strategies with real data

> **💡 Recommended Learning Path**: Start with `main.py` to understand concepts, then use `run_backtest.py` for actual strategy testing.

### 🔧 Dependencies in pyproject.toml

After setup, your `pyproject.toml` includes:

```toml
[project]
name = "backtest"
version = "0.1.0"
description = "Nautilus Trader backtest tutorial"
requires-python = ">=3.13"
dependencies = [
    "nautilus-trader>=1.218.0",
    "pandas>=2.0.0",
]
```

**Key dependencies used in main.py:**
- `nautilus_trader.backtest.engine` - Core backtesting engine
- `nautilus_trader.backtest.node` - High-level backtesting API
- `nautilus_trader.config` - Configuration classes
- `pandas` - Data analysis for results

## 🧭 Understanding Backtesting in Nautilus Trader

### What is Backtesting?

Backtesting is the process of testing a trading strategy on historical data to evaluate:
- **Profitability**: How much money the strategy would have made
- **Risk**: Maximum drawdowns and volatility
- **Consistency**: Performance across different market conditions
- **Efficiency**: Number of trades and transaction costs

### Two API Levels

Nautilus Trader offers two levels of backtesting APIs:

1. **Low-level API (BacktestEngine)**: Direct control, manual setup
2. **High-level API (BacktestNode)**: Recommended for most use cases

## 🏗️ Backtest Approaches Covered in main.py

Our `main.py` demonstrates three complete backtesting approaches:

### 1. Basic BacktestEngine (Low-level API)

```python
# From main.py - Basic approach
def run_basic_backtest_engine(self):
    # Configure engine
    engine_config = BacktestEngineConfig(trader_id="BACKTEST-001")
    engine = BacktestEngine(config=engine_config)
    
    # Add venue, instrument, data, strategy
    engine.add_venue(venue=Venue("SIM"), oms_type=OmsType.HEDGING, ...)
    engine.add_instrument(self.instrument)
    engine.add_data(historical_data)
    engine.add_strategy(strategy_config)
    
    # Run and get results
    engine.run()
    result = engine.get_result()
```

**When to use:**
- Learning how backtesting works internally
- Custom setups with specific requirements
- Fine-grained control over every aspect

### 2. Advanced BacktestNode (High-level API)

```python
# From main.py - Recommended approach
def run_advanced_backtest_node(self):
    # Configure everything in structured configs
    strategy_config = ImportableStrategyConfig(...)
    engine_config = BacktestEngineConfig(...)
    venue_config = BacktestVenueConfig(...)
    data_config = BacktestDataConfig(...)
    
    # Create run configuration
    run_config = BacktestRunConfig(
        engine=engine_config,
        venues=[venue_config],
        data=[data_config],
    )
    
    # Run with node
    node = BacktestNode(configs=[run_config])
    results = node.run()
```

**When to use:**
- Production backtesting
- Multiple strategies or venues
- Complex scenarios
- Batch processing

### 3. Bar Data Backtesting

```python
# From main.py - Bar data approach
def run_backtest_with_bars(self):
    # Use OHLC bar data instead of tick data
    bars = self.generate_sample_bars()  # Load your bar data
    engine.add_data(bars)
```

**When to use:**
- Strategy works with OHLC data
- Limited storage or bandwidth
- Faster backtesting with less granular data

## 📊 Key Configuration Components

### BacktestEngineConfig
```python
# From main.py
engine_config = BacktestEngineConfig(
    trader_id="BACKTEST-001",           # Unique identifier
    logging=LoggingConfig(log_level="INFO"),  # Logging configuration
    strategies=[strategy_config],        # List of strategies to test
)
```

### BacktestVenueConfig
```python
# From main.py  
venue_config = BacktestVenueConfig(
    name="SIM",                         # Venue name
    oms_type="HEDGING",                 # Order management system
    account_type="MARGIN",              # Account type
    base_currency="USD",                # Base currency
    starting_balances=["100_000 USD"],  # Starting capital
)
```

### BacktestDataConfig
```python
# From main.py
data_config = BacktestDataConfig(
    data_cls=QuoteTick,                 # Type of market data
    catalog_path="./data",              # Data storage path
    instrument_id="EUR/USD.SIM",        # Instrument to test
    start_time="2023-01-01",            # Backtest start date
    end_time="2023-01-31",              # Backtest end date
)
```

## 🚀 Running the Examples

### Quick Test - Tutorial (main.py)

Test the backtest tutorial setup:

```bash
# Run the comprehensive tutorial (all commands must use docker exec)
docker exec -it nautilus-trader bash -c "cd /workspace/bots/backtest && uv run python main.py"
```

You'll see detailed explanations of:
- Backtest engine setup and configuration
- Data types and sources
- Performance metrics and analysis
- Best practices and common pitfalls

### Real Backtest - Implementation (run_backtest.py)

Run an actual backtest with historical data:

```bash
# Run the real backtest implementation
docker exec -it nautilus-trader bash -c "cd /workspace/bots/backtest && uv run python run_backtest.py"
```

This will:
- Load historical market data
- Execute your strategy against the data
- Generate performance reports
- Show account, positions, and trade analysis

### Expected Output

**Tutorial (main.py):**
```
🤖 Nautilus Trader Backtest Tutorial
This comprehensive guide teaches you everything about backtesting!
� Initializing Backtest Tutorial...
🚀 Explaining Basic Backtest with BacktestEngine...
[... detailed educational content ...]
```

**Real Backtest (run_backtest.py):**
```
🤖 Nautilus Trader Real Backtest Runner
🚀 Initializing Real Backtest Runner...
� Running Basic Backtest with Real Data
⚙️ Step 1: Configuring backtest engine...
[... actual backtest execution and results ...]
```

This demonstrates both learning and practical application!

## 📈 Understanding Backtest Results

The `print_results()` function in `main.py` shows key metrics:

### Performance Metrics
```python
# From main.py results analysis
Total Return: 15.25%        # Overall percentage return
Max Drawdown: -5.30%        # Worst loss period
Sharpe Ratio: 1.85          # Risk-adjusted return
Total PnL: $15,250.00       # Absolute profit/loss
Total Trades: 127           # Number of trades executed
Win Rate: 67.50%            # Percentage of profitable trades
```

### What These Metrics Mean

- **Total Return**: Overall performance percentage
- **Max Drawdown**: Largest peak-to-trough loss (risk measure)
- **Sharpe Ratio**: Return per unit of risk (higher is better)
- **Total PnL**: Absolute profit or loss in currency
- **Win Rate**: Percentage of trades that were profitable

## 🎯 Best Practices for Backtesting

### 1. Data Quality
- Use high-quality, tick-by-tick data when possible
- Ensure data includes realistic spreads and slippage
- Avoid look-ahead bias and survivorship bias

### 2. Realistic Assumptions
- Include transaction costs and commissions
- Account for slippage on large orders
- Consider market impact of your trades

### 3. Out-of-Sample Testing
- Reserve data for validation (don't optimize on all data)
- Test on different market conditions
- Use walk-forward analysis

### 4. Risk Management
- Always include stop-losses in your strategy
- Test with different position sizes
- Monitor maximum drawdown carefully

## 🔄 Common Backtesting Patterns

Most successful backtesting follows this pattern:

1. **Strategy Development** - Create and test logic
2. **Data Preparation** - Clean and format historical data
3. **Initial Backtest** - Run on a subset of data
4. **Optimization** - Tune parameters carefully
5. **Validation** - Test on out-of-sample data
6. **Risk Analysis** - Analyze drawdowns and edge cases
7. **Live Testing** - Paper trade before real money

## 📚 Next Steps After This Tutorial

### 1. Get Real Market Data
```bash
# Example data sources to explore:
# - Historical data providers (Bloomberg, Reuters, etc.)
# - Cryptocurrency exchanges (Binance, Coinbase, etc.)  
# - Forex data (Dukascopy, TrueFX, etc.)
# - Stock data (Yahoo Finance, Alpha Vantage, etc.)
```

### 2. Advanced Backtesting Features
- **Multi-asset strategies**: Trade multiple instruments
- **Portfolio optimization**: Optimize across strategies
- **Risk models**: Add sophisticated risk management
- **Walk-forward analysis**: Continuous optimization

### 3. Integration with Live Trading
- **Paper trading**: Test with real market data
- **Risk checks**: Add position sizing limits
- **Monitoring**: Set up alerts and dashboards
- **Deployment**: Move to live trading environment

## 🛡️ Important Warnings

- **Past performance doesn't guarantee future results**
- **Backtest results can be misleading** - always validate
- **Overfitting is dangerous** - don't over-optimize
- **Market conditions change** - strategies may stop working
- **Start small** - never risk significant capital on unproven strategies

## 📚 Additional Resources

### Official Documentation
- [Nautilus Trader Backtesting Guide](https://nautilustrader.io/docs/latest/concepts/backtesting)
- [Strategy Development](https://nautilustrader.io/docs/latest/concepts/strategies)

### Community Examples
- [Official Examples Repository](https://github.com/nautechsystems/nautilus_trader/tree/main/examples/backtest)
- [Community Strategies](https://github.com/nautechsystems/nautilus_trader/discussions)

---

**Next**: After mastering backtesting, explore [live trading](../live-trading/) (coming soon) or [advanced strategies](../advanced-strategies/) (coming soon)!

**Remember**: The complete working examples are in `main.py` - study them, modify them, and experiment!

## 🎯 Real Backtest Implementation Details

### Based on Official Nautilus Trader Examples

The `run_backtest.py` file is built following official Nautilus Trader patterns from:
- `/examples/backtest/` directory
- Official documentation at docs.nautilustrader.io
- Production-ready backtest implementations

### Key Features Implemented

#### 1. **Low-Level BacktestEngine API**
Following the official pattern:
```python
# Engine configuration (official pattern)
engine_config = BacktestEngineConfig(
    trader_id=TraderId("BACKTESTER-001"),
    logging=LoggingConfig(log_level="INFO"),
    data_engine=DataEngineConfig(
        time_bars_interval_type="left-open",
        time_bars_timestamp_on_close=True,
        validate_data_sequence=True,
    ),
)

# Create engine
engine = BacktestEngine(config=engine_config)
```

#### 2. **Venue Configuration**
```python
# Add trading venue (margin account)
engine.add_venue(
    venue=Venue("SIM"),
    oms_type=OmsType.NETTING,
    account_type=AccountType.MARGIN,
    base_currency=USD,
    starting_balances=[Money(100_000, USD)],
    default_leverage=Decimal(1),
)
```

#### 3. **Data Management**
- Realistic bar data generation
- Proper timestamp handling (nanoseconds)
- OHLC price simulation following market patterns

#### 4. **Performance Reporting**
```python
# Official reporting methods
account_report = engine.trader.generate_account_report(venue)
fills_report = engine.trader.generate_order_fills_report()
positions_report = engine.trader.generate_positions_report()
```

### Customization Options

You can modify `run_backtest.py` to:
1. **Load Real Data**: Replace sample data with CSV/API data
2. **Multiple Instruments**: Add forex, crypto, stocks
3. **Different Strategies**: Import your own strategy classes
4. **Advanced Features**: Add risk management, portfolio analysis

### Data Sources Integration

The backtest runner supports:
- **CSV Files**: Historical OHLC data
- **API Integration**: Real-time and historical feeds
- **Test Data**: Built-in sample data for development
- **Custom Formats**: Implement your own data loaders

## ✅ Troubleshooting Guide

### Common Issues and Solutions

#### 1. **Import Errors**
```bash
ModuleNotFoundError: No module named 'nautilus_trader'
```
**Solution**: Ensure you're running inside Docker container:
```bash
docker exec -it nautilus-trader bash -c "cd /workspace/bots/backtest && uv run python run_backtest.py"
```

#### 2. **Data Loading Warnings**
```
⚠️ Warning: Could not load external data: Install the requests package to use the github FS
```
**Solution**: This is normal - the backtest uses generated sample data for demonstration.

#### 3. **Strategy Errors**
```
AttributeError: 'Portfolio' object has no attribute 'is_long'
```
**Solution**: Use the correct Nautilus Trader API patterns (already fixed in demo_strategy.py).

#### 4. **Performance Issues**
If backtest runs slowly:
- Reduce the number of bars in `_generate_sample_bars()`
- Use fewer strategy parameters
- Optimize EMA calculations

### 📊 Expected Results

A successful backtest run shows:
- ✅ Strategy loaded and running
- 📊 Historical data processed (1000 bars)
- 🤖 EMA crossover signals detected
- 📋 Performance reports generated
- 🧹 Clean resource disposal

### 🎯 Next Development Steps

1. **Load Real Data**:
   ```python
   # Replace _generate_sample_bars() with:
   # - CSV file loading
   # - API data fetching
   # - Database connections
   ```

2. **Advanced Strategies**:
   - Multiple timeframes
   - More indicators (RSI, MACD, etc.)
   - Risk management rules
   - Position sizing algorithms

3. **Portfolio Analysis**:
   - Multiple instruments
   - Correlation analysis
   - Risk-adjusted returns
   - Drawdown analysis

4. **Production Deployment**:
   - Paper trading integration
   - Live data feeds
   - Monitoring and alerting
   - Performance tracking
