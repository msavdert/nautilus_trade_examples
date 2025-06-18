#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
# Simple demo strategy for backtest testing
# -------------------------------------------------------------------------------------------------

from decimal import Decimal

from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import BarType, Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Quantity
from nautilus_trader.trading.strategy import Strategy


class DemoStrategyConfig(StrategyConfig, frozen=True):
    """Demo strategy configuration"""
    instrument_id: InstrumentId
    trade_size: Decimal = Decimal("100_000")
    fast_ema_period: int = 10
    slow_ema_period: int = 20


class DemoStrategy(Strategy):
    """
    Simple demo strategy for backtesting.
    
    This strategy uses EMA crossover logic:
    - Buy when fast EMA crosses above slow EMA
    - Sell when fast EMA crosses below slow EMA
    """
    
    def __init__(self, config: DemoStrategyConfig):
        super().__init__(config)
        
        # Strategy parameters
        self.instrument_id = config.instrument_id
        self.trade_size = Quantity.from_str(str(config.trade_size))
        
        # Moving averages (simple implementation)
        self.fast_ema_period = config.fast_ema_period
        self.slow_ema_period = config.slow_ema_period
        
        # Price history for EMA calculation
        self.prices = []
        self.fast_ema = None
        self.slow_ema = None
        
        # Bar type to subscribe to
        self.bar_type = BarType.from_str(f"{self.instrument_id}-1-MINUTE-LAST-EXTERNAL")
        
    def on_start(self):
        """Called when strategy starts"""
        self.log.info("Starting Demo Strategy")
        
        # Subscribe to bar data
        self.subscribe_bars(self.bar_type)
        
    def on_bar(self, bar: Bar):
        """Called when a new bar is received"""
        # Add new price to history
        self.prices.append(float(bar.close))
        
        # Calculate EMAs if we have enough data
        if len(self.prices) >= self.slow_ema_period:
            self._update_emas()
            self._check_signals()
            
    def _update_emas(self):
        """Update EMA values"""
        if len(self.prices) < self.fast_ema_period:
            return
            
        # Simple EMA calculation
        if self.fast_ema is None:
            self.fast_ema = sum(self.prices[-self.fast_ema_period:]) / self.fast_ema_period
        else:
            alpha = 2.0 / (self.fast_ema_period + 1)
            self.fast_ema = alpha * self.prices[-1] + (1 - alpha) * self.fast_ema
            
        if len(self.prices) >= self.slow_ema_period:
            if self.slow_ema is None:
                self.slow_ema = sum(self.prices[-self.slow_ema_period:]) / self.slow_ema_period
            else:
                alpha = 2.0 / (self.slow_ema_period + 1)
                self.slow_ema = alpha * self.prices[-1] + (1 - alpha) * self.slow_ema
    
    def _check_signals(self):
        """Check for trading signals"""
        if self.fast_ema is None or self.slow_ema is None:
            return
            
        # Get previous EMA values
        if len(self.prices) < 2:
            return
            
        # Simple crossover logic
        current_fast = self.fast_ema
        current_slow = self.slow_ema
        
        # Check current position using portfolio
        # Get all positions for this instrument
        positions = self.cache.positions_open(venue=None, instrument_id=self.instrument_id)
        
        # Check if we have an open position
        is_flat = len(positions) == 0
        is_long = any(p.side.name == "LONG" for p in positions) if positions else False
        is_short = any(p.side.name == "SHORT" for p in positions) if positions else False
        
        # Buy signal: fast EMA above slow EMA and we're not long
        if current_fast > current_slow and (is_flat or is_short):
            self._submit_market_order(OrderSide.BUY)
            
        # Sell signal: fast EMA below slow EMA and we're not short  
        elif current_fast < current_slow and (is_flat or is_long):
            self._submit_market_order(OrderSide.SELL)
    
    def _submit_market_order(self, side: OrderSide):
        """Submit a market order"""
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=side,
            quantity=self.trade_size,
        )
        
        self.submit_order(order)
        self.log.info(f"Submitted {side} order: {order}")
        
    def on_stop(self):
        """Called when strategy stops"""
        self.log.info("Stopping Demo Strategy")
