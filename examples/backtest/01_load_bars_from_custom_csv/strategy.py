#!/usr/bin/env python3
"""
Simple Moving Average Crossover Strategy

This is a basic trading strategy that demonstrates:
- Using technical indicators
- Making trading decisions based on signal crossovers
- Basic position management

The strategy uses two moving averages:
- Fast MA (10 periods): Reacts quickly to price changes
- Slow MA (20 periods): Provides the trend direction

Trading logic:
- BUY when fast MA crosses above slow MA (bullish signal)
- SELL when fast MA crosses below slow MA (bearish signal)
"""

from decimal import Decimal

from nautilus_trader.common.enums import LogColor
from nautilus_trader.indicators.average.sma import SimpleMovingAverage
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.model.position import Position
from nautilus_trader.trading.strategy import Strategy


class SimpleStrategy(Strategy):
    """
    A simple moving average crossover strategy for learning purposes.
    
    This strategy demonstrates:
    - How to use indicators in NautilusTrader
    - Basic buy/sell logic
    - Position management
    - Logging and debugging
    """
    
    def __init__(
        self,
        bar_type: BarType,
        trade_size: Decimal,
        fast_ma_period: int = 10,
        slow_ma_period: int = 20,
    ):
        """
        Initialize the strategy.
        
        Parameters:
        -----------
        bar_type : BarType
            The bar type to subscribe to for price data
        trade_size : Decimal
            The size of each trade in base currency units
        fast_ma_period : int
            Period for the fast moving average (default: 10)
        slow_ma_period : int
            Period for the slow moving average (default: 20)
        """
        super().__init__()
        
        # Strategy parameters
        self.bar_type = bar_type
        self.instrument_id = bar_type.instrument_id
        self.trade_size = trade_size
        
        # Create indicators
        self.fast_ma = SimpleMovingAverage(fast_ma_period)
        self.slow_ma = SimpleMovingAverage(slow_ma_period)
        
        # Strategy state
        self.bars_processed = 0
        self.last_signal = None  # Track last signal to avoid repeated trades
        
        # Performance tracking
        self.trades_count = 0
        self.entry_price = None
        
    def on_start(self) -> None:
        """Called when the strategy is started."""
        self.log.info(f"Strategy started for {self.instrument_id}")
        self.log.info(f"Fast MA period: {self.fast_ma.period}")
        self.log.info(f"Slow MA period: {self.slow_ma.period}")
        self.log.info(f"Trade size: {self.trade_size}")
        
        # Subscribe to bar data
        self.subscribe_bars(self.bar_type)
        
    def on_bar(self, bar: Bar) -> None:
        """
        Called when a new bar is received.
        
        This is where the main trading logic happens.
        """
        self.bars_processed += 1
        
        # Update indicators with new price data
        self.fast_ma.update_raw(bar.close)
        self.slow_ma.update_raw(bar.close)
        
        # Skip if indicators are not yet initialized
        if not (self.fast_ma.initialized and self.slow_ma.initialized):
            return
        
        # Get current indicator values
        fast_value = self.fast_ma.value
        slow_value = self.slow_ma.value
        
        # Log indicator values (uncomment for debugging)
        # self.log.info(f"Bar {self.bars_processed}: Close={bar.close}, Fast MA={fast_value:.5f}, Slow MA={slow_value:.5f}")
        
        # Determine current signal
        current_signal = None
        if fast_value > slow_value:
            current_signal = "BUY"
        elif fast_value < slow_value:
            current_signal = "SELL"
        
        # Only act if signal has changed
        if current_signal != self.last_signal and current_signal is not None:
            self._execute_signal(current_signal, bar)
            self.last_signal = current_signal
            
    def _execute_signal(self, signal: str, bar: Bar) -> None:
        """
        Execute trading signal.
        
        Parameters:
        -----------
        signal : str
            "BUY" or "SELL"
        bar : Bar
            Current price bar
        """
        # Check current position for this instrument
        positions = self.cache.positions_open(instrument_id=self.instrument_id)
        position = positions[0] if positions else None
        
        if signal == "BUY":
            self._handle_buy_signal(position, bar)
        elif signal == "SELL":
            self._handle_sell_signal(position, bar)
            
    def _handle_buy_signal(self, position: Position | None, bar: Bar) -> None:
        """Handle bullish signal (fast MA crosses above slow MA)."""
        
        if position is None or position.is_closed:
            # No position or closed position - open new long position
            self._place_market_order(OrderSide.BUY, bar.close)
            self.log.info(
                f"🟢 BUY SIGNAL: Fast MA crossed above Slow MA at {bar.close}",
                color=LogColor.GREEN
            )
            
        elif position.is_short:
            # Close short position and open long
            self._close_position(position)
            self._place_market_order(OrderSide.BUY, bar.close)
            self.log.info(
                f"🔄 REVERSE to BUY: Closing short and going long at {bar.close}",
                color=LogColor.BLUE
            )
        # If already long, do nothing
        
    def _handle_sell_signal(self, position: Position | None, bar: Bar) -> None:
        """Handle bearish signal (fast MA crosses below slow MA)."""
        
        if position is None or position.is_closed:
            # No position or closed position - open new short position
            self._place_market_order(OrderSide.SELL, bar.close)
            self.log.info(
                f"🔴 SELL SIGNAL: Fast MA crossed below Slow MA at {bar.close}",
                color=LogColor.RED
            )
            
        elif position.is_long:
            # Close long position and open short
            self._close_position(position)
            self._place_market_order(OrderSide.SELL, bar.close)
            self.log.info(
                f"🔄 REVERSE to SELL: Closing long and going short at {bar.close}",
                color=LogColor.BLUE
            )
        # If already short, do nothing
        
    def _place_market_order(self, side: OrderSide, price: float) -> None:
        """Place a market order."""
        
        instrument = self.cache.instrument(self.instrument_id)
        
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=side,
            quantity=instrument.make_qty(self.trade_size),
        )
        
        self.submit_order(order)
        self.trades_count += 1
        
        if side == OrderSide.BUY:
            self.entry_price = price
        else:
            self.entry_price = price
            
    def _close_position(self, position: Position) -> None:
        """Close an existing position."""
        if position.is_open:
            self.close_position(position)
            
    def on_stop(self) -> None:
        """Called when the strategy is stopped."""
        self.log.info("Strategy stopped")
        self.log.info(f"Bars processed: {self.bars_processed}")
        self.log.info(f"Total trades executed: {self.trades_count}")
        
        # Close any remaining positions
        positions = self.cache.positions_open(instrument_id=self.instrument_id)
        if positions:
            position = positions[0]
            if position.is_open:
                self.close_position(position)
                self.log.info("Closed final position")
            
        # Log final indicator values
        if self.fast_ma.initialized and self.slow_ma.initialized:
            self.log.info(f"Final Fast MA: {self.fast_ma.value:.5f}")
            self.log.info(f"Final Slow MA: {self.slow_ma.value:.5f}")
        
        # Performance summary
        instrument = self.cache.instrument(self.instrument_id)
        if instrument:
            account = self.cache.account_for_venue(instrument.id.venue)
            if account:
                total_balance = account.balance_total(account.base_currency)
                self.log.info(f"Final account balance: {total_balance}", color=LogColor.CYAN)
