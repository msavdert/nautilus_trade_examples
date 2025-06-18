# My First Bot - Complete Beginner's Guide to Nautilus Trader

Welcome to your first journey into algorithmic trading with Nautilus Trader! This guide will take you step-by-step through creating your very first trading bot, explaining everything from the ground up.

## 🎯 What We'll Build

We'll create a simple trading bot that:
- Monitors market data for EUR/USD
- Uses a basic moving average strategy
- Places buy/sell orders based on simple rules
- Runs entirely in a single `main.py` file

## 📚 Prerequisites

Before we start, make sure you have:
- Completed the [Quick Start setup](../../README.md#quick-start) 
- Docker and Nautilus Trader environment running
- Basic understanding of Python

## 🚀 Project Setup

**Important**: All commands must be run inside the Docker container using `docker exec`.

Start by creating a new project in the Docker environment:

```bash
# 1. Start the Docker environment (from project root)
docker-compose up -d

# 2. Create new project
docker exec -it nautilus-trader bash -c "cd /workspace/bots/ && uv init my-first-bot"

# 3. Add required dependencies
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv add nautilus_trader"
```

These commands will:
1. Create a new Python project structure with `pyproject.toml` and basic files
2. Add the `nautilus_trader` package to your dependencies

### 📝 Project Structure After Setup

```
my-first-bot/
├── pyproject.toml          # Project configuration and dependencies
├── README.md              # This documentation
├── main.py                # Your trading strategy (we'll create this)
└── uv.lock               # Dependency lock file
```

### 🔧 Dependencies in pyproject.toml

After running the setup commands, your `pyproject.toml` will include:

```toml
[project]
name = "my-first-bot"
version = "0.1.0"
description = "My first trading bot with Nautilus Trader"
requires-python = ">=3.13"
dependencies = [
    "nautilus-trader>=1.218.0",
]
```

The `nautilus-trader` dependency includes all the modules we use in `main.py`:
- `nautilus_trader.trading.strategy` - Base Strategy class
- `nautilus_trader.config` - Configuration classes
- `nautilus_trader.model.data` - Market data types (Bar, Quote, etc.)
- `nautilus_trader.model.enums` - Trading enums (OrderSide, etc.)
- `nautilus_trader.model.objects` - Trading objects (Quantity, Price, etc.)
- `nautilus_trader.common.enums` - Common enums (LogColor, etc.)

## 🧭 Understanding Nautilus Trader Basics

### What is a Trading Strategy?

In Nautilus Trader, a **Strategy** is a Python class that:
1. **Receives market data** (prices, volumes, etc.)
2. **Makes trading decisions** based on that data
3. **Places orders** to buy or sell instruments

### Key Components

- **Strategy**: Your trading logic (what we'll build)
- **Instruments**: What you trade (EUR/USD, BTC/USD, etc.)
- **Market Data**: Price information (quotes, trades, bars)
- **Orders**: Instructions to buy or sell
- **Portfolio**: Tracks your positions and money

## 🏗️ Step 1: Create Your First Strategy

Let's start by creating our main bot file. The `main.py` file contains our complete trading strategy implementation.

### 📄 Complete main.py Implementation

Here's our complete `main.py` file with detailed explanations:

```python
# This code is implemented in main.py
# See the complete implementation in the main.py file
```

**👆 The complete strategy implementation is in `main.py` - let's break down the key parts:**

## � Understanding the Code in main.py

Let's break down what each part does:

### 1. Configuration Class (`MyFirstBotConfig`)

```python
# From main.py lines 12-22
class MyFirstBotConfig(StrategyConfig, frozen=True):
    instrument_id: str = "EUR/USD.SIM"
    trade_size: int = 100_000
    ma_period: int = 10
```

**What it does:**
- **instrument_id**: What we want to trade (EUR/USD simulator)
- **trade_size**: How much to trade (100,000 units)
- **ma_period**: How many price bars to use for moving average (10 bars)
- **frozen=True**: Makes the config immutable (can't be changed after creation)

### 2. Strategy Class (`MyFirstBot`)

```python
# From main.py lines 25-35
class MyFirstBot(Strategy):
    def __init__(self, config: MyFirstBotConfig):
        super().__init__(config)
        self.config = config
        self.prices = []
        self.position_open = False
        self.bars_received = 0
        self.trade_quantity = Quantity.from_int(config.trade_size)
```

**What it does:**
- Inherits from Nautilus's `Strategy` base class
- Stores configuration and initializes tracking variables
- **prices**: List to store recent closing prices
- **position_open**: Boolean to track if we have an open trade
- **bars_received**: Counter for received price bars

### 3. Key Methods Explained

#### `on_start()` - Initialization
```python
# From main.py lines 37-49
def on_start(self):
    self.log.info("🚀 My First Bot is starting!", color=LogColor.GREEN)
    bar_type = BarType.from_str(f"{self.config.instrument_id}-1-MINUTE-MID-EXTERNAL")
    self.subscribe_bars(bar_type)
```

**What it does:**
- Called when the bot starts
- Subscribes to 1-minute price bars for EUR/USD
- Sets up data feed for our strategy

#### `on_bar()` - Main Trading Logic
```python
# From main.py lines 51-85
def on_bar(self, bar: Bar):
    # Get closing price and add to our list
    close_price = float(bar.close)
    self.prices.append(close_price)
    
    # Calculate moving average when we have enough data
    if len(self.prices) >= self.config.ma_period:
        moving_average = sum(self.prices) / len(self.prices)
        self.check_for_entry(close_price, moving_average)
```

**What it does:**
- Called every time we receive a new price bar (every minute)
- Stores the closing price
- Calculates simple moving average
- Makes trading decisions

#### Trading Decision Logic
```python
# From main.py lines 87-97
def check_for_entry(self, current_price: float, moving_average: float):
    # Buy when price is above moving average
    if current_price > moving_average and not self.position_open:
        self.place_buy_order()
    # Sell when price is below moving average
    elif current_price < moving_average and self.position_open:
        self.place_sell_order()
```

**What it does:**
- **Buy signal**: Price above moving average + no position open
- **Sell signal**: Price below moving average + position is open
- Simple trend-following strategy

### 4. Order Placement

```python
# From main.py lines 99-118
def place_buy_order(self):
    order = self.order_factory.market(
        instrument_id=self.config.instrument_id,
        order_side=OrderSide.BUY,
        quantity=self.trade_quantity,
    )
    self.submit_order(order)
```

**What it does:**
- Creates a market order (buy/sell immediately at current price)
- Uses the configured trade size
- Submits order to the trading system

## 🎯 Step 2: Key Nautilus Trader Concepts

### Strategy Lifecycle
The lifecycle of a Nautilus strategy follows this pattern:

1. **Initialize** (`__init__`) - Set up variables and configuration
2. **Start** (`on_start`) - Subscribe to data feeds
3. **Process Data** (`on_bar`, `on_quote_tick`, etc.) - Receive market data
4. **Make Decisions** - Your trading logic
5. **Place Orders** (`submit_order`) - Execute trades
6. **Stop** (`on_stop`) - Cleanup when done

### Market Data Types

- **Bar**: Price data over a time period (open, high, low, close) - **Used in our main.py**
- **Quote**: Best bid/ask prices
- **Trade**: Actual transactions

### Order Types in Nautilus

- **Market Order**: Buy/sell immediately at current price - **Used in our main.py**
- **Limit Order**: Buy/sell only at specific price or better

### Important Objects from main.py

- **`StrategyConfig`**: Base class for strategy configuration
- **`Strategy`**: Base class for all trading strategies
- **`Bar`**: Contains OHLC price data for a time period
- **`OrderSide`**: Enum for BUY or SELL
- **`Quantity`**: Represents trading quantities
- **`LogColor`**: For colored console output

## 🚀 Step 3: Testing Your Strategy

## 🚀 Step 3: Testing Your Strategy

### Quick Test - Verify main.py

First, let's test that our strategy is properly defined:

```bash
# Test the strategy definition (run inside Docker container)
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv run python main.py"
```

You should see:
```
🤖 My First Trading Bot
This is just the strategy definition.
To run a backtest or live trading, we need additional setup.
Check the next steps in the documentation!
```

This confirms that our strategy loads correctly!

### What's Next?

Now that you have your first strategy, you'll want to:

1. **Test it with a backtest** - Run it on historical data
2. **Add more sophisticated logic** - Better entry/exit rules
3. **Add risk management** - Stop losses, position sizing
4. **Test on testnet** - Practice with fake money

## 🔄 Common Patterns You've Learned

Most trading strategies follow this pattern:

1. **Subscribe to data** in `on_start` - like in our main.py
2. **Process data** in event handlers (`on_bar`, `on_quote_tick`)
3. **Calculate indicators** (moving averages, RSI, etc.) - like in our main.py
4. **Check trading conditions** (your strategy rules) - like in our main.py
5. **Manage positions** (entry, exit, risk management)

## 🎓 What You've Learned

Congratulations! You've just created your first trading bot. You now understand:

- ✅ How to create a Nautilus Strategy class
- ✅ How to configure your bot with settings
- ✅ How to receive and process market data
- ✅ How to implement basic trading logic
- ✅ How to place buy and sell orders
- ✅ The structure of a complete trading bot
- ✅ The important dependencies needed in pyproject.toml

## 🛡️ Important Notes

- **This is educational**: This simple strategy is for learning only
- **No real money**: Always test thoroughly before risking real capital
- **Risk management**: Real strategies need stop losses and position sizing
- **Market conditions**: No strategy works in all market conditions

## 📚 Next Steps

**Next**: Learn how to backtest your strategy with historical data at [../backtest/](../backtest/)!

This will teach you how to:
- Test your strategy on historical data
- Measure performance and profitability
- Validate your trading logic
- Optimize parameters

---

**Remember**: The complete working code is in `main.py` - study it, modify it, and experiment with it!
