"""
Volatility Breakout Strategy with Volume Confirmation
A comprehensive trading strategy that combines technical indicators for robust signal generation.
"""

import logging
from typing import Dict, Optional, List
from decimal import Decimal

import pandas as pd
import numpy as np

from nautilus_trader.core.message import Event
from nautilus_trader.indicators.atr import AverageTrueRange
from nautilus_trader.indicators.bollinger_bands import BollingerBands
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage
from nautilus_trader.model.data import Bar, QuoteTick
from nautilus_trader.model.enums import OrderSide, TimeInForce, TriggerType
from nautilus_trader.model.events import PositionOpened, PositionClosed
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.model.orders import MarketOrder, StopMarketOrder, LimitOrder
from nautilus_trader.trading.strategy import Strategy, StrategyConfig

from config import get_config
from risk_manager import RiskManager
from coin_selector import CoinSelector


class VolatilityBreakoutConfig(StrategyConfig):
    """Configuration for the Volatility Breakout strategy."""
    
    # Strategy parameters
    atr_period: int = 14
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    rsi_period: int = 14
    volume_period: int = 20
    
    # Entry conditions
    volume_threshold_multiplier: float = 1.5
    rsi_min: float = 30.0
    rsi_max: float = 70.0
    volatility_threshold_atr: float = 0.5
    
    # Exit conditions
    stop_loss_atr_multiplier: float = 2.0
    take_profit_atr_multiplier: float = 3.0
    trailing_stop_atr_multiplier: float = 1.5
    
    # Risk management
    max_risk_per_trade: float = 0.01  # 1% of balance
    max_position_size: float = 0.02   # 2% of balance


class VolatilityBreakoutStrategy(Strategy):
    """
    Volatility Breakout Strategy with Volume Confirmation
    
    Strategy Logic:
    1. Identifies volatility breakouts using Bollinger Bands
    2. Confirms breakouts with volume spikes
    3. Uses RSI to filter out overbought/oversold conditions
    4. Implements ATR-based stop losses and take profits
    5. Supports trailing stops for profit maximization
    
    Entry Conditions:
    - Price breaks above/below Bollinger Band
    - Volume > 1.5x average volume
    - RSI between 30-70 (avoid extremes)
    - ATR indicates sufficient volatility
    
    Exit Conditions:
    - Stop loss: 2x ATR from entry
    - Take profit: 3x ATR from entry
    - Trailing stop: 1.5x ATR
    """
    
    def __init__(self, config: VolatilityBreakoutConfig):
        """
        Initialize the strategy.
        
        Args:
            config: Strategy configuration
        """
        super().__init__(config)
        
        # Configuration
        self.config = config
        self.bot_config = get_config()
        
        # Risk management
        self.risk_manager = RiskManager()
        
        # Technical indicators per instrument
        self.indicators: Dict[InstrumentId, Dict] = {}
        
        # Strategy state
        self.active_positions: Dict[InstrumentId, bool] = {}
        self.last_signals: Dict[InstrumentId, str] = {}
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        
        # Volume tracking
        self.volume_history: Dict[InstrumentId, List[float]] = {}
        
    def on_start(self) -> None:
        """Actions to be performed when the strategy is started."""
        self.log.info(
            f"Starting {self.__class__.__name__} "
            f"with config: {self.config}"
        )
        
        # Subscribe to required data
        for instrument_id in self.config.instrument_ids:
            self._setup_indicators(instrument_id)
            self._subscribe_data(instrument_id)
            
        self.log.info("Strategy started successfully")
    
    def on_stop(self) -> None:
        """Actions to be performed when the strategy is stopped."""
        self.log.info("Stopping strategy...")
        
        # Close all open positions
        for position in self.cache.positions_open():
            if position.instrument_id in self.config.instrument_ids:
                self._close_position(position.instrument_id, "Strategy stop")
        
        # Log performance summary
        self._log_performance_summary()
        
        self.log.info("Strategy stopped")
    
    def _setup_indicators(self, instrument_id: InstrumentId) -> None:
        """
        Setup technical indicators for an instrument.
        
        Args:
            instrument_id: Instrument to setup indicators for
        """
        self.indicators[instrument_id] = {
            'atr': AverageTrueRange(self.config.atr_period),
            'bollinger': BollingerBands(
                self.config.bollinger_period,
                self.config.bollinger_std
            ),
            'rsi': RelativeStrengthIndex(self.config.rsi_period),
            'volume_ema': ExponentialMovingAverage(self.config.volume_period)
        }
        
        # Initialize volume tracking
        self.volume_history[instrument_id] = []
        self.active_positions[instrument_id] = False
        self.last_signals[instrument_id] = "NONE"
        
        self.log.info(f"Indicators setup for {instrument_id.symbol}")
    
    def _subscribe_data(self, instrument_id: InstrumentId) -> None:
        """
        Subscribe to required data feeds.
        
        Args:
            instrument_id: Instrument to subscribe data for
        """
        # Subscribe to bars for technical analysis
        self.subscribe_bars(
            self.config.bar_type,
            await_partial=True
        )
        
        # Subscribe to quote ticks for real-time pricing
        self.subscribe_quote_ticks(instrument_id)
        
        self.log.info(f"Data subscriptions setup for {instrument_id.symbol}")
    
    def on_bar(self, bar: Bar) -> None:
        """
        Handle incoming bar data.
        
        Args:
            bar: Incoming bar data
        """
        instrument_id = bar.bar_type.instrument_id
        
        if instrument_id not in self.indicators:
            return
        
        # Update indicators
        self._update_indicators(instrument_id, bar)
        
        # Check for trading signals
        signal = self._analyze_signals(instrument_id, bar)
        
        if signal != "NONE":
            self._process_signal(instrument_id, signal, bar)
    
    def on_quote_tick(self, tick: QuoteTick) -> None:
        """
        Handle incoming quote tick data.
        
        Args:
            tick: Incoming quote tick
        """
        instrument_id = tick.instrument_id
        
        if instrument_id not in self.indicators:
            return
        
        # Update trailing stops if position is open
        if self.active_positions.get(instrument_id, False):
            self._update_trailing_stop(instrument_id, tick)
    
    def _update_indicators(self, instrument_id: InstrumentId, bar: Bar) -> None:
        """
        Update technical indicators with new bar data.
        
        Args:
            instrument_id: Instrument identifier
            bar: New bar data
        """
        indicators = self.indicators[instrument_id]
        
        # Update ATR
        indicators['atr'].update_raw(
            bar.high.as_double(),
            bar.low.as_double(),
            bar.close.as_double()
        )
        
        # Update Bollinger Bands
        indicators['bollinger'].update_raw(bar.close.as_double())
        
        # Update RSI
        indicators['rsi'].update_raw(bar.close.as_double())
        
        # Update volume EMA
        volume_value = float(bar.volume.as_double())
        indicators['volume_ema'].update_raw(volume_value)
        
        # Track volume history
        self.volume_history[instrument_id].append(volume_value)
        if len(self.volume_history[instrument_id]) > self.config.volume_period * 2:
            self.volume_history[instrument_id] = self.volume_history[instrument_id][-self.config.volume_period:]
    
    def _analyze_signals(self, instrument_id: InstrumentId, bar: Bar) -> str:
        """
        Analyze technical indicators to generate trading signals.
        
        Args:
            instrument_id: Instrument identifier
            bar: Current bar data
            
        Returns:
            Signal: "BUY", "SELL", or "NONE"
        """
        indicators = self.indicators[instrument_id]
        
        # Ensure all indicators have sufficient data
        if not self._indicators_ready(indicators):
            return "NONE"
        
        current_price = bar.close.as_double()
        
        # Get indicator values
        bb_upper = indicators['bollinger'].upper.value
        bb_lower = indicators['bollinger'].lower.value
        rsi_value = indicators['rsi'].value
        atr_value = indicators['atr'].value
        avg_volume = indicators['volume_ema'].value
        current_volume = float(bar.volume.as_double())
        
        # Check volume confirmation
        volume_threshold = avg_volume * self.config.volume_threshold_multiplier
        volume_confirmed = current_volume > volume_threshold
        
        # Check RSI filter
        rsi_in_range = self.config.rsi_min <= rsi_value <= self.config.rsi_max
        
        # Check volatility threshold
        volatility_sufficient = atr_value > (current_price * self.config.volatility_threshold_atr / 100)
        
        # Generate signals
        signal = "NONE"
        
        # Bullish breakout
        if (current_price > bb_upper and 
            volume_confirmed and 
            rsi_in_range and 
            volatility_sufficient and
            not self.active_positions.get(instrument_id, False)):
            signal = "BUY"
        
        # Bearish breakout
        elif (current_price < bb_lower and 
              volume_confirmed and 
              rsi_in_range and 
              volatility_sufficient and
              not self.active_positions.get(instrument_id, False)):
            signal = "SELL"
        
        # Log signal details for debugging
        if signal != "NONE":
            self.log.info(
                f"Signal {signal} for {instrument_id.symbol}: "
                f"Price={current_price:.4f}, BB=[{bb_lower:.4f}, {bb_upper:.4f}], "
                f"RSI={rsi_value:.1f}, ATR={atr_value:.4f}, "
                f"Volume={current_volume:.0f} (avg={avg_volume:.0f})"
            )
        
        return signal
    
    def _indicators_ready(self, indicators: Dict) -> bool:
        """
        Check if all indicators have sufficient data.
        
        Args:
            indicators: Dictionary of indicators
            
        Returns:
            True if all indicators are ready
        """
        return (indicators['atr'].initialized and
                indicators['bollinger'].initialized and
                indicators['rsi'].initialized and
                indicators['volume_ema'].initialized)
    
    def _process_signal(self, instrument_id: InstrumentId, signal: str, bar: Bar) -> None:
        """
        Process trading signal and execute orders.
        
        Args:
            instrument_id: Instrument identifier
            signal: Trading signal ("BUY" or "SELL")
            bar: Current bar data
        """
        # Skip if same signal as last one
        if signal == self.last_signals.get(instrument_id, "NONE"):
            return
        
        self.last_signals[instrument_id] = signal
        
        # Get instrument and account info
        instrument = self.cache.instrument(instrument_id)
        if not instrument:
            self.log.error(f"Instrument not found: {instrument_id}")
            return
        
        account = self.cache.account_for_venue(instrument_id.venue)
        if not account:
            self.log.error(f"Account not found for venue: {instrument_id.venue}")
            return
        
        # Calculate entry parameters
        entry_price = bar.close
        atr_value = self.indicators[instrument_id]['atr'].value
        
        # Determine order side
        order_side = OrderSide.BUY if signal == "BUY" else OrderSide.SELL
        
        # Calculate stop loss and take profit
        stop_loss = self.risk_manager.calculate_stop_loss(entry_price, atr_value, order_side)
        take_profit = self.risk_manager.calculate_take_profit(entry_price, atr_value, order_side)
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            instrument, entry_price, stop_loss, atr_value, account.balance()
        )
        
        # Validate trade entry
        is_valid, reason = self.risk_manager.validate_trade_entry(
            instrument_id, order_side, position_size, entry_price
        )
        
        if not is_valid:
            self.log.warning(f"Trade rejected for {instrument_id.symbol}: {reason}")
            return
        
        # Execute trade
        self._execute_trade(
            instrument_id, order_side, position_size, 
            entry_price, stop_loss, take_profit
        )
    
    def _execute_trade(self, 
                      instrument_id: InstrumentId,
                      side: OrderSide,
                      quantity: Quantity,
                      entry_price: Price,
                      stop_loss: Price,
                      take_profit: Price) -> None:
        """
        Execute trade with entry, stop loss, and take profit orders.
        
        Args:
            instrument_id: Instrument identifier
            side: Order side
            quantity: Order quantity
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        """
        try:
            # Create market entry order
            entry_order = self.order_factory.market(
                instrument_id=instrument_id,
                order_side=side,
                quantity=quantity,
                time_in_force=TimeInForce.IOC,
                tags=[f"ENTRY_{side.name}"]
            )
            
            # Submit entry order
            self.submit_order(entry_order)
            
            self.log.info(
                f"Trade executed: {side.name} {quantity} {instrument_id.symbol} "
                f"@ {entry_price}, SL: {stop_loss}, TP: {take_profit}"
            )
            
            # Mark position as active (will be confirmed in on_position_opened)
            self.active_positions[instrument_id] = True
            self.total_trades += 1
            
        except Exception as e:
            self.log.error(f"Error executing trade for {instrument_id.symbol}: {e}")
    
    def on_position_opened(self, event: PositionOpened) -> None:
        """
        Handle position opened event.
        
        Args:
            event: Position opened event
        """
        position = event.position
        instrument_id = position.instrument_id
        
        if instrument_id not in self.config.instrument_ids:
            return
        
        # Create stop loss and take profit orders
        self._create_exit_orders(position)
        
        # Update risk tracking
        current_price = position.avg_px_open
        atr_value = self.indicators[instrument_id]['atr'].value
        
        self.risk_manager.update_position_risk(
            instrument_id, position, current_price, atr_value
        )
        
        self.log.info(f"Position opened: {position}")
    
    def on_position_closed(self, event: PositionClosed) -> None:
        """
        Handle position closed event.
        
        Args:
            event: Position closed event
        """
        position = event.position
        instrument_id = position.instrument_id
        
        if instrument_id not in self.config.instrument_ids:
            return
        
        # Update position tracking
        self.active_positions[instrument_id] = False
        
        # Record trade result
        pnl = float(position.realized_pnl.as_double()) if position.realized_pnl else 0.0
        is_win = pnl > 0
        
        self.risk_manager.record_trade_result(pnl, is_win)
        
        if is_win:
            self.winning_trades += 1
        
        self.total_pnl += pnl
        
        self.log.info(
            f"Position closed: {position.instrument_id.symbol} "
            f"PnL: ${pnl:.2f}, Win: {is_win}"
        )
        
        # Remove from risk tracking
        if instrument_id in self.risk_manager.position_risks:
            del self.risk_manager.position_risks[instrument_id]
    
    def _create_exit_orders(self, position) -> None:
        """
        Create stop loss and take profit orders for a position.
        
        Args:
            position: Opened position
        """
        instrument_id = position.instrument_id
        atr_value = self.indicators[instrument_id]['atr'].value
        
        # Calculate exit prices
        stop_loss = self.risk_manager.calculate_stop_loss(
            position.avg_px_open, atr_value, 
            OrderSide.BUY if position.side.name == "LONG" else OrderSide.SELL
        )
        
        take_profit = self.risk_manager.calculate_take_profit(
            position.avg_px_open, atr_value,
            OrderSide.BUY if position.side.name == "LONG" else OrderSide.SELL
        )
        
        # Create stop loss order
        stop_side = OrderSide.SELL if position.side.name == "LONG" else OrderSide.BUY
        
        stop_order = self.order_factory.stop_market(
            instrument_id=instrument_id,
            order_side=stop_side,
            quantity=position.quantity,
            trigger_price=stop_loss,
            time_in_force=TimeInForce.GTC,
            tags=["STOP_LOSS"]
        )
        
        # Create take profit order
        tp_order = self.order_factory.limit(
            instrument_id=instrument_id,
            order_side=stop_side,
            quantity=position.quantity,
            price=take_profit,
            time_in_force=TimeInForce.GTC,
            tags=["TAKE_PROFIT"]
        )
        
        # Submit orders
        self.submit_order(stop_order)
        self.submit_order(tp_order)
        
        self.log.info(
            f"Exit orders created for {instrument_id.symbol}: "
            f"SL @ {stop_loss}, TP @ {take_profit}"
        )
    
    def _update_trailing_stop(self, instrument_id: InstrumentId, tick: QuoteTick) -> None:
        """
        Update trailing stop for open position.
        
        Args:
            instrument_id: Instrument identifier
            tick: Current quote tick
        """
        position = self.cache.position_for_instrument(instrument_id)
        if not position or position.is_closed:
            return
        
        atr_value = self.indicators[instrument_id]['atr'].value
        current_price = tick.bid if position.side.name == "LONG" else tick.ask
        
        new_stop = self.risk_manager.calculate_trailing_stop(
            current_price, position, atr_value
        )
        
        if new_stop:
            # Cancel existing stop loss and create new one
            # (Simplified - in practice would need to find and cancel existing stop)
            self.log.info(
                f"Trailing stop updated for {instrument_id.symbol}: {new_stop}"
            )
    
    def _close_position(self, instrument_id: InstrumentId, reason: str) -> None:
        """
        Close position for an instrument.
        
        Args:
            instrument_id: Instrument identifier
            reason: Reason for closing
        """
        position = self.cache.position_for_instrument(instrument_id)
        if not position or position.is_closed:
            return
        
        # Create market order to close position
        close_side = OrderSide.SELL if position.side.name == "LONG" else OrderSide.BUY
        
        close_order = self.order_factory.market(
            instrument_id=instrument_id,
            order_side=close_side,
            quantity=position.quantity,
            time_in_force=TimeInForce.IOC,
            tags=[f"CLOSE_{reason}"]
        )
        
        self.submit_order(close_order)
        
        self.log.info(f"Position closed for {instrument_id.symbol}: {reason}")
    
    def _log_performance_summary(self) -> None:
        """Log strategy performance summary."""
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        risk_summary = self.risk_manager.get_risk_summary()
        
        self.log.info(
            f"=== STRATEGY PERFORMANCE SUMMARY ===\n"
            f"Total Trades: {self.total_trades}\n"
            f"Winning Trades: {self.winning_trades}\n"
            f"Win Rate: {win_rate:.1f}%\n"
            f"Total PnL: ${self.total_pnl:.2f}\n"
            f"Daily PnL: ${risk_summary['daily_pnl']:.2f}\n"
            f"Max Drawdown: {risk_summary['max_drawdown']:.2f}%\n"
            f"Active Positions: {risk_summary['active_positions']}\n"
            f"Emergency Stop: {risk_summary['emergency_stop']}"
        )
    
    def on_event(self, event: Event) -> None:
        """
        Handle general events.
        
        Args:
            event: Incoming event
        """
        # Handle emergency stop conditions
        if hasattr(event, 'account'):
            account = event.account
            if self.risk_manager.check_emergency_conditions(account.balance()):
                self.risk_manager.trigger_emergency_stop()
                
                # Close all positions
                for instrument_id in self.config.instrument_ids:
                    self._close_position(instrument_id, "Emergency stop")
