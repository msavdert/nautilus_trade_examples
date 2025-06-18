# My First Bot - Beginner's Guide to Nautilus Trader

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
- Your bot project created: `my-first-bot`
- Basic understanding of Python

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

Let's start by creating our main bot file. Navigate to your bot directory and create the main file:

```bash
# Make sure you're in the right directory
cd /workspace/bots/my-first-bot
```

Create `main.py`:

```python
# main.py - My First Trading Bot

from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.objects import Quantity
from nautilus_trader.common.enums import LogColor


class MyFirstBotConfig(StrategyConfig, frozen=True):
    """
    Configuration for our first trading bot.
    This defines what settings our bot needs.
    """
    # The instrument we want to trade (like EUR/USD)
    instrument_id: str = "EUR/USD.SIM"
    
    # How much to trade each time
    trade_size: int = 100_000  # 100,000 units
    
    # Moving average period (how many bars to look back)
    ma_period: int = 10


class MyFirstBot(Strategy):
    """
    My First Trading Bot - A Simple Moving Average Strategy
    
    This bot will:
    1. Calculate a simple moving average of closing prices
    2. Buy when price is above the moving average
    3. Sell when price is below the moving average
    """
    
    def __init__(self, config: MyFirstBotConfig):
        # Always call the parent class constructor first
        super().__init__(config)
        
        # Store our configuration
        self.config = config
        
        # Initialize our trading variables
        self.prices = []  # Store recent closing prices
        self.position_open = False  # Track if we have an open position
        self.bars_received = 0  # Count how many price bars we've seen
        
        # Convert trade size to Nautilus Quantity object
        self.trade_quantity = Quantity.from_int(config.trade_size)
    
    def on_start(self):
        """
        This method is called when our bot starts.
        Here we tell Nautilus what data we want to receive.
        """
        self.log.info("🚀 My First Bot is starting!", color=LogColor.GREEN)
        
        # Subscribe to 1-minute bars for our instrument
        # This means we'll get price updates every minute
        from nautilus_trader.model.data import BarType
        bar_type = BarType.from_str(f"{self.config.instrument_id}-1-MINUTE-MID-EXTERNAL")
        self.subscribe_bars(bar_type)
        
        self.log.info(f"📊 Subscribed to {bar_type}")
    
    def on_bar(self, bar: Bar):
        """
        This method is called every time we receive a new price bar.
        This is where our main trading logic lives.
        """
        self.bars_received += 1
        
        # Get the closing price of this bar
        close_price = float(bar.close)
        
        # Add the new price to our list
        self.prices.append(close_price)
        
        # Keep only the last 'ma_period' prices
        if len(self.prices) > self.config.ma_period:
            self.prices.pop(0)  # Remove the oldest price
        
        self.log.info(
            f"📈 Bar #{self.bars_received}: Price = {close_price:.5f}",
            color=LogColor.BLUE
        )
        
        # Only start trading after we have enough data
        if len(self.prices) < self.config.ma_period:
            self.log.info(f"⏳ Waiting for more data... ({len(self.prices)}/{self.config.ma_period})")
            return
        
        # Calculate Simple Moving Average
        moving_average = sum(self.prices) / len(self.prices)
        
        self.log.info(
            f"📊 Current Price: {close_price:.5f}, Moving Average: {moving_average:.5f}",
            color=LogColor.CYAN
        )
        
        # Trading Logic
        self.check_for_entry(close_price, moving_average)
    
    def check_for_entry(self, current_price: float, moving_average: float):
        """
        Check if we should buy or sell based on our strategy.
        """
        
        # Strategy Rule 1: Buy when price is above moving average
        if current_price > moving_average and not self.position_open:
            self.place_buy_order()
            
        # Strategy Rule 2: Sell when price is below moving average  
        elif current_price < moving_average and self.position_open:
            self.place_sell_order()
    
    def place_buy_order(self):
        """
        Place a buy order (go long).
        """
        try:
            # Create a market order to buy
            order = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.trade_quantity,
            )
            
            # Submit the order
            self.submit_order(order)
            self.position_open = True
            
            self.log.info("🟢 BUY ORDER PLACED!", color=LogColor.GREEN)
            
        except Exception as e:
            self.log.error(f"❌ Error placing buy order: {e}")
    
    def place_sell_order(self):
        """
        Place a sell order (close position).
        """
        try:
            # Create a market order to sell
            order = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.SELL,
                quantity=self.trade_quantity,
            )
            
            # Submit the order
            self.submit_order(order)
            self.position_open = False
            
            self.log.info("🔴 SELL ORDER PLACED!", color=LogColor.RED)
            
        except Exception as e:
            self.log.error(f"❌ Error placing sell order: {e}")
    
    def on_stop(self):
        """
        This method is called when our bot stops.
        Clean up any resources here.
        """
        self.log.info("🛑 My First Bot is stopping...", color=LogColor.YELLOW)
        self.log.info(f"📊 Total bars processed: {self.bars_received}")


# Test our bot (this won't run any real trades)
if __name__ == "__main__":
    print("🤖 My First Trading Bot")
    print("This is just the strategy definition.")
    print("To run a backtest or live trading, we need additional setup.")
    print("Check the next steps in the documentation!")
```

## 📖 Understanding the Code

Let's break down what each part does:

### 1. Configuration Class (`MyFirstBotConfig`)
```python
class MyFirstBotConfig(StrategyConfig, frozen=True):
    instrument_id: str = "EUR/USD.SIM"
    trade_size: int = 100_000
    ma_period: int = 10
```

This defines the settings for our bot:
- **instrument_id**: What we want to trade
- **trade_size**: How much to trade
- **ma_period**: How many price bars to use for moving average

### 2. Strategy Class (`MyFirstBot`)
```python
class MyFirstBot(Strategy):
```

This is our main bot that inherits from Nautilus's `Strategy` class.

### 3. Key Methods

- **`__init__`**: Sets up our bot when it's created
- **`on_start`**: Called when bot starts - we subscribe to data here
- **`on_bar`**: Called for each new price bar - our main logic
- **`on_stop`**: Called when bot stops - cleanup code

### 4. Trading Logic Flow

1. **Receive price data** in `on_bar`
2. **Store prices** in a list
3. **Calculate moving average** when we have enough data
4. **Compare current price to moving average**
5. **Place orders** based on our rules

## 🎯 Step 2: Understanding Key Concepts

### Market Data Types

- **Bar**: Price data over a time period (open, high, low, close)
- **Quote**: Best bid/ask prices
- **Trade**: Actual transactions

### Order Types

- **Market Order**: Buy/sell immediately at current price
- **Limit Order**: Buy/sell only at specific price or better

### Strategy Lifecycle

1. **Initialize** (`__init__`)
2. **Start** (`on_start`) - Subscribe to data
3. **Process Data** (`on_bar`, `on_quote_tick`, etc.)
4. **Make Decisions** (your trading logic)
5. **Place Orders** (`submit_order`)
6. **Stop** (`on_stop`) - Cleanup

## 🚀 Step 3: Next Steps

Now that you have your first strategy, you'll want to:

1. **Test it with a backtest** - Run it on historical data
2. **Add more sophisticated logic** - Better entry/exit rules
3. **Add risk management** - Stop losses, position sizing
4. **Test on testnet** - Practice with fake money

### Quick Test

Save the code above to `main.py` and run:

```bash
uv run python main.py
```

You should see:
```
🤖 My First Trading Bot
This is just the strategy definition.
To run a backtest or live trading, we need additional setup.
Check the next steps in the documentation!
```

## 🎓 What You've Learned

Congratulations! You've just created your first trading bot. You now understand:

- ✅ How to create a Nautilus Strategy class
- ✅ How to configure your bot with settings
- ✅ How to receive and process market data
- ✅ How to implement basic trading logic
- ✅ How to place buy and sell orders
- ✅ The structure of a complete trading bot

## 🔄 Common Patterns in Nautilus

Most trading strategies follow this pattern:

1. **Subscribe to data** in `on_start`
2. **Process data** in event handlers (`on_bar`, `on_quote_tick`)
3. **Calculate indicators** (moving averages, RSI, etc.)
4. **Check trading conditions** (your strategy rules)
5. **Manage positions** (entry, exit, risk management)

## 🛡️ Important Notes

- **This is educational**: This simple strategy is for learning only
- **No real money**: Always test thoroughly before risking real capital
- **Risk management**: Real strategies need stop losses and position sizing
- **Market conditions**: No strategy works in all market conditions

## 📚 Further Reading

- [Trading Fundamentals](../trading-fundamentals.md)
- [Risk Management](../risk-management.md)
- [Nautilus Strategy Documentation](https://nautilustrader.io/docs/latest/concepts/strategies)

---

**Next**: Learn how to backtest your strategy with historical data!

## 🔗 Related Guides

- [Turkish Version (Türkçe)](my-first-bot.tr.md)
- [Advanced Strategy Patterns](advanced-patterns.md) *(Coming Soon)*
- [Backtesting Your Strategy](backtesting-guide.md) *(Coming Soon)*
