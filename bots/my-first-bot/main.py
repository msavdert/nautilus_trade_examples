# main.py - My First Trading Bot

from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.objects import Quantity
from nautilus_trader.common.enums import LogColor

# For logging configuration examples, see logging_example.py


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
        self.log.info(f"📋 Configuration: MA Period = {self.config.ma_period}, Trade Size = {self.config.trade_size:,}")
        
        # Subscribe to 1-minute bars for our instrument
        # This means we'll get price updates every minute
        from nautilus_trader.model.data import BarType
        bar_type = BarType.from_str(f"{self.config.instrument_id}-1-MINUTE-MID-EXTERNAL")
        self.subscribe_bars(bar_type)
        
        self.log.info(f"📊 Subscribed to {bar_type}")
        self.log.debug("🔧 Debug logging enabled - detailed information will be logged")
    
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
        
        # Log detailed information at debug level
        self.log.debug(f"📈 Price History: {self.prices[-3:]}")  # Last 3 prices
        
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
            self.log.debug(f"🎯 Buy signal: Price {current_price:.5f} > MA {moving_average:.5f}")
            self.place_buy_order()
            
        # Strategy Rule 2: Sell when price is below moving average  
        elif current_price < moving_average and self.position_open:
            self.log.debug(f"🎯 Sell signal: Price {current_price:.5f} < MA {moving_average:.5f}")
            self.place_sell_order()
        else:
            # Log when no action is taken
            status = "position open" if self.position_open else "no position"
            trend = "above" if current_price > moving_average else "below"
            self.log.debug(f"⏸️ No action: Price {trend} MA, {status}")
    
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
            self.log.debug(f"🔍 Order details: {order}")
            
        except Exception as e:
            self.log.error(f"❌ Error placing buy order: {e}", color=LogColor.RED)
            # In production, you might want to add error handling like:
            # - Retry logic
            # - Alert notifications
            # - Position reconciliation
    
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
            self.log.debug(f"🔍 Order details: {order}")
            
        except Exception as e:
            self.log.error(f"❌ Error placing sell order: {e}", color=LogColor.RED)
            # In production, you might want to add error handling like:
            # - Retry logic
            # - Alert notifications
            # - Position reconciliation
    
    def on_stop(self):
        """
        This method is called when our bot stops.
        Clean up any resources here.
        """
        self.log.info("🛑 My First Bot is stopping...", color=LogColor.YELLOW)
        self.log.info(f"📊 Total bars processed: {self.bars_received}")
        self.log.info(f"📈 Final position status: {'OPEN' if self.position_open else 'CLOSED'}")
        
        # Log final statistics
        if self.prices:
            final_price = self.prices[-1]
            avg_price = sum(self.prices) / len(self.prices)
            self.log.info(f"💰 Final price: {final_price:.5f}, Average: {avg_price:.5f}")
        
        self.log.info("✅ Bot shutdown complete", color=LogColor.GREEN)


# Test our bot (this won't run any real trades)
if __name__ == "__main__":
    print("🤖 My First Trading Bot")
    print("This is just the strategy definition.")
    print("To run a backtest or live trading, we need additional setup.")
    print()
    print("📚 Next steps:")
    print("1. See 'logging_example.py' for complete logging configuration")
    print("2. See 'LOGGING.md' for comprehensive logging documentation")
    print("3. Configure data sources and venues for backtesting/live trading")
    print("4. Run using 'uv run logging_example.py' to test logging setup")
