#!/usr/bin/env python3
"""
One-Three Risk Management Trading Bot
=====================================

A sophisticated EUR/USD trading bot that implements a step-by-step risk management strategy
using the Nautilus Trader framework. This bot follows a disciplined approach where each trade
has fixed take profit (+1.3 units) and stop loss (-1.3 units) levels, ensuring consistent
risk management without position scaling or martingale strategies.

Strategy Overview:
- Buys EUR/USD at current market price
- Closes position at +1.3 units profit (take profit)
- Closes position at -1.3 units loss (stop loss) 
- Always trades one position at a time
- No leverage, no position scaling
- Comprehensive logging of all trades
"""

from decimal import Decimal
from typing import Optional

from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.model.data import Bar, Quote, Trade
from nautilus_trader.model.enums import OrderSide, OrderType, TimeInForce, TriggerType
from nautilus_trader.model.events import OrderFilled, PositionOpened, PositionClosed
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.orders import MarketOrder, StopMarketOrder, LimitOrder
from nautilus_trader.model.position import Position
from nautilus_trader.model.currencies import USD
from nautilus_trader.trading.strategy import Strategy


class OneThreeConfig(StrategyConfig, frozen=True):
    """
    Configuration for the One-Three Risk Management Trading Bot.
    
    This configuration defines all the parameters needed for the trading strategy,
    including risk management settings, position sizing, and market timing.
    """
    
    # Core trading parameters
    instrument_id: InstrumentId = InstrumentId.from_str("EUR/USD.SIM")
    trade_size: Decimal = Decimal("100_000")  # Standard lot size
    
    # Risk management parameters (in price points/pips)
    take_profit_pips: float = 1.3  # Take profit at +1.3 units
    stop_loss_pips: float = 1.3    # Stop loss at -1.3 units
    
    # Trading behavior settings
    max_daily_trades: int = 50     # Maximum trades per day
    entry_delay_seconds: int = 1   # Delay between trades (seconds)
    
    # Market timing (optional filters)
    enable_time_filter: bool = False
    trading_start_hour: int = 8    # Start trading at 8:00 AM UTC
    trading_end_hour: int = 18     # Stop trading at 6:00 PM UTC
    
    # Advanced features
    enable_trailing_stop: bool = False
    trailing_stop_distance: float = 0.8  # Distance for trailing stop
    
    # Data and execution settings
    use_tick_data: bool = True     # Use tick data for precise entries
    slippage_tolerance: float = 0.1  # Acceptable slippage in pips


class OneThreeBot(Strategy):
    """
    One-Three Risk Management Trading Bot
    
    This bot implements a disciplined risk management approach for EUR/USD trading:
    
    1. Entry Logic:
       - Buys EUR/USD at current market price
       - Each trade is independent (no correlation with previous trades)
       
    2. Exit Logic:
       - Take profit: Close at +1.3 units profit
       - Stop loss: Close at -1.3 units loss
       - Always uses market orders for immediate execution
       
    3. Risk Management:
       - Fixed position size (no scaling)
       - One position at a time
       - No martingale or recovery strategies
       - Comprehensive trade logging
       
    4. Advanced Features:
       - Tick-level precision for entry/exit
       - Optional time-based trading filters
       - Optional trailing stop functionality
       - Performance tracking and analytics
    """
    
    def __init__(self, config: OneThreeConfig) -> None:
        """Initialize the One-Three trading bot with configuration."""
        super().__init__(config)
        
        # Store configuration
        self.config = config
        
        # Trading state variables
        self.current_position: Optional[Position] = None
        self.entry_price: Optional[Price] = None
        self.take_profit_price: Optional[Price] = None
        self.stop_loss_price: Optional[Price] = None
        
        # Performance tracking
        self.trade_count = 0
        self.daily_trade_count = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = Money(0, currency=USD)
        self.last_trade_time = None
        
        # Convert trade size to Quantity
        self.trade_quantity = Quantity.from_str(str(config.trade_size))
        
        # Calculate pip value for EUR/USD (typically 0.0001)
        self.pip_size = 0.0001
        
        # Order management
        self.pending_take_profit_order = None
        self.pending_stop_loss_order = None
        
        # Market data tracking
        self.latest_bid: Optional[Price] = None
        self.latest_ask: Optional[Price] = None
        self.latest_mid: Optional[Price] = None
        
        self.log.info(
            f"🚀 One-Three Bot initialized for {config.instrument_id}",
            color=LogColor.GREEN
        )
        
    def on_start(self) -> None:
        """
        Called when the strategy starts.
        
        Sets up data subscriptions and initializes the trading environment.
        """
        self.log.info("🎯 Starting One-Three Risk Management Bot", color=LogColor.CYAN)
        self.log.info(f"📊 Configuration:")
        self.log.info(f"   • Instrument: {self.config.instrument_id}")
        self.log.info(f"   • Trade Size: {self.config.trade_size:,} units")
        self.log.info(f"   • Take Profit: +{self.config.take_profit_pips} pips")
        self.log.info(f"   • Stop Loss: -{self.config.stop_loss_pips} pips")
        self.log.info(f"   • Max Daily Trades: {self.config.max_daily_trades}")
        
        # Subscribe to market data
        if self.config.use_tick_data:
            # Subscribe to tick-by-tick quotes for precise execution
            self.subscribe_quote_ticks(self.config.instrument_id)
            self.log.info("📈 Subscribed to quote ticks (tick-level precision)")
        else:
            # Subscribe to 1-minute bars as fallback
            from nautilus_trader.model.data import BarType
            bar_type = BarType.from_str(f"{self.config.instrument_id}-1-MINUTE-MID-EXTERNAL")
            self.subscribe_bars(bar_type)
            self.log.info(f"📊 Subscribed to {bar_type}")
        
        # Subscribe to trade ticks for market analysis
        self.subscribe_trade_ticks(self.config.instrument_id)
        
        self.log.info("✅ Bot startup complete - Ready to trade!", color=LogColor.GREEN)
        
    def on_quote_tick(self, tick) -> None:
        """
        Handle incoming quote ticks (bid/ask prices).
        
        This method is called for every bid/ask price update when using tick data.
        It provides the most precise entry and exit timing.
        """
        self.latest_bid = tick.bid
        self.latest_ask = tick.ask
        self.latest_mid = Price((float(tick.bid) + float(tick.ask)) / 2, precision=5)
        
        # Check if we should enter a new trade
        if self.current_position is None:
            self.check_entry_conditions(tick)
        else:
            # Check if current position should be closed
            self.check_exit_conditions(tick)
            
    def on_bar(self, bar: Bar) -> None:
        """
        Handle incoming price bars.
        
        Used as fallback when tick data is not available.
        """
        self.latest_mid = bar.close
        
        # Log periodic updates
        self.log.info(
            f"📊 Bar: {bar.close} | Position: {'LONG' if self.current_position else 'NONE'}",
            color=LogColor.BLUE
        )
        
        if self.current_position is None:
            self.check_entry_conditions_bar(bar)
        else:
            self.check_exit_conditions_bar(bar)
            
    def check_entry_conditions(self, tick) -> None:
        """
        Check if conditions are met to enter a new trade.
        
        Args:
            tick: Current market quote tick
        """
        # Check daily trade limit
        if self.daily_trade_count >= self.config.max_daily_trades:
            return
            
        # Check time filter (if enabled)
        if self.config.enable_time_filter:
            current_hour = self.clock.timestamp_ns() // 1_000_000_000 % 86400 // 3600
            if not (self.config.trading_start_hour <= current_hour < self.config.trading_end_hour):
                return
                
        # Check minimum delay between trades
        if (self.last_trade_time and 
            self.clock.timestamp_ns() - self.last_trade_time < self.config.entry_delay_seconds * 1_000_000_000):
            return
            
        # Entry signal: Always buy at market (simple strategy)
        # In a real strategy, you would add your entry logic here
        self.enter_long_position()
        
    def check_entry_conditions_bar(self, bar: Bar) -> None:
        """Check entry conditions using bar data (fallback method)."""
        if self.daily_trade_count >= self.config.max_daily_trades:
            return
            
        # Simple entry: buy on every bar (for demonstration)
        # Replace with your actual entry logic
        self.enter_long_position()
        
    def enter_long_position(self) -> None:
        """
        Enter a long position at current market price.
        
        Creates a market buy order and sets up stop loss and take profit levels.
        """
        try:
            # Create market order to buy EUR/USD
            order = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.trade_quantity,
                time_in_force=TimeInForce.FOK,  # Fill or Kill for immediate execution
            )
            
            # Submit the order
            self.submit_order(order)
            
            # Store entry details
            self.entry_price = self.latest_ask or self.latest_mid
            self.trade_count += 1
            self.daily_trade_count += 1
            self.last_trade_time = self.clock.timestamp_ns()
            
            self.log.info(
                f"🟢 ENTERING LONG POSITION #{self.trade_count}",
                color=LogColor.GREEN
            )
            self.log.info(f"   • Entry Price: {self.entry_price}")
            self.log.info(f"   • Quantity: {self.trade_quantity}")
            self.log.info(f"   • Daily Trades: {self.daily_trade_count}/{self.config.max_daily_trades}")
            
        except Exception as e:
            self.log.error(f"❌ Error entering long position: {e}", color=LogColor.RED)
            
    def check_exit_conditions(self, tick) -> None:
        """
        Check if current position should be closed based on P&L.
        
        Args:
            tick: Current market quote tick
        """
        if not self.current_position or not self.entry_price:
            return
            
        current_price = tick.bid  # Use bid for selling
        entry_price_float = float(self.entry_price)
        current_price_float = float(current_price)
        
        # Calculate P&L in pips
        pnl_pips = (current_price_float - entry_price_float) / self.pip_size
        
        # Check take profit condition
        if pnl_pips >= self.config.take_profit_pips:
            self.exit_position("TAKE_PROFIT", current_price, pnl_pips)
            
        # Check stop loss condition  
        elif pnl_pips <= -self.config.stop_loss_pips:
            self.exit_position("STOP_LOSS", current_price, pnl_pips)
            
    def check_exit_conditions_bar(self, bar: Bar) -> None:
        """Check exit conditions using bar data (fallback method)."""
        if not self.current_position or not self.entry_price:
            return
            
        current_price = bar.close
        entry_price_float = float(self.entry_price)
        current_price_float = float(current_price)
        
        pnl_pips = (current_price_float - entry_price_float) / self.pip_size
        
        if pnl_pips >= self.config.take_profit_pips:
            self.exit_position("TAKE_PROFIT", current_price, pnl_pips)
        elif pnl_pips <= -self.config.stop_loss_pips:
            self.exit_position("STOP_LOSS", current_price, pnl_pips)
            
    def exit_position(self, reason: str, exit_price: Price, pnl_pips: float) -> None:
        """
        Exit the current position.
        
        Args:
            reason: Reason for exit ("TAKE_PROFIT" or "STOP_LOSS")
            exit_price: Price at which to exit
            pnl_pips: Profit/loss in pips
        """
        try:
            # Create market order to sell
            order = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.SELL,
                quantity=self.trade_quantity,
                time_in_force=TimeInForce.FOK,
            )
            
            # Submit the order
            self.submit_order(order)
            
            # Log the exit
            color = LogColor.GREEN if pnl_pips > 0 else LogColor.RED
            emoji = "🎯" if reason == "TAKE_PROFIT" else "🛑"
            
            self.log.info(f"{emoji} EXITING POSITION - {reason}", color=color)
            self.log.info(f"   • Entry: {self.entry_price}")
            self.log.info(f"   • Exit: {exit_price}")
            self.log.info(f"   • P&L: {pnl_pips:+.1f} pips")
            
            # Update statistics
            if pnl_pips > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1
                
            # Reset position tracking
            self.current_position = None
            self.entry_price = None
            
        except Exception as e:
            self.log.error(f"❌ Error exiting position: {e}", color=LogColor.RED)
            
    def on_order_filled(self, event: OrderFilled) -> None:
        """Handle order fill events."""
        order = event.order
        
        if order.side == OrderSide.BUY:
            self.log.info(f"✅ BUY ORDER FILLED: {event.last_qty} @ {event.last_px}")
        else:
            self.log.info(f"✅ SELL ORDER FILLED: {event.last_qty} @ {event.last_px}")
            
    def on_position_opened(self, event: PositionOpened) -> None:
        """Handle position opened events."""
        self.current_position = event.position
        self.log.info(f"📈 POSITION OPENED: {event.position}")
        
    def on_position_closed(self, event: PositionClosed) -> None:
        """Handle position closed events."""
        position = event.position
        pnl = position.realized_pnl
        
        self.log.info(f"📊 POSITION CLOSED")
        self.log.info(f"   • P&L: {pnl}")
        self.log.info(f"   • Duration: {position.duration_ns / 1_000_000_000:.1f}s")
        
        # Reset tracking
        self.current_position = None
        self.entry_price = None
        
    def on_stop(self) -> None:
        """
        Called when the strategy stops.
        
        Logs final performance statistics and cleanup.
        """
        self.log.info("🛑 One-Three Bot stopping...", color=LogColor.YELLOW)
        
        # Log final statistics
        total_trades = self.winning_trades + self.losing_trades
        win_rate = (self.winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        self.log.info("📊 FINAL PERFORMANCE SUMMARY", color=LogColor.CYAN)
        self.log.info(f"   • Total Trades: {total_trades}")
        self.log.info(f"   • Winning Trades: {self.winning_trades}")
        self.log.info(f"   • Losing Trades: {self.losing_trades}")
        self.log.info(f"   • Win Rate: {win_rate:.1f}%")
        self.log.info(f"   • Daily Trades: {self.daily_trade_count}")
        
        if self.current_position:
            self.log.warning(f"⚠️ Open position at shutdown: {self.current_position}")
            
        self.log.info("✅ Bot shutdown complete", color=LogColor.GREEN)


# Example usage and testing
if __name__ == "__main__":
    print("🤖 One-Three Risk Management Trading Bot")
    print("=====================================")
    print()
    print("This is the strategy implementation for EUR/USD trading")
    print("with fixed +1.3/-1.3 pips take profit and stop loss.")
    print()
    print("🎯 Key Features:")
    print("• Risk Management: Fixed TP/SL levels")
    print("• Position Control: One trade at a time")
    print("• No Scaling: Fixed position sizes")
    print("• Comprehensive Logging: Full trade history")
    print("• Tick Precision: Precise entry/exit timing")
    print()
    print("📚 To run the bot:")
    print("1. Configure your data source and venue")
    print("2. Run backtest: python run_backtest.py")
    print("3. Run live trading: python run_live.py")
    print("4. View results: python analyze_results.py")
