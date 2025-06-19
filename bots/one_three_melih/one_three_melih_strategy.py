#!/usr/bin/env python3
"""
One-Three-Melih: Advanced Step-Back Risk Management Trading Bot
===============================================================

A sophisticated EUR/USD trading bot that implements a dynamic step-back balance management
strategy using the Nautilus Trader framework. This bot manages balance progression through
profit steps and intelligently steps back upon losses, maintaining disciplined risk control.

Strategy Overview:
- Uses full available balance for each trade (no partial positions)
- +30% profit target increases balance for next trade
- Dynamic loss calculation to step back to previous balance level
- Always trades one position at a time
- No leverage, no martingale, no position scaling
- Comprehensive logging and balance tracking

Balance Management Logic:
- Trade 1: $100 → Win (+30%) → Next: $130
- Trade 2: $130 → Win (+30%) → Next: $169  
- Trade 3: $169 → Lose (calculated %) → Next: $130 (step back)
- Trade 4: $130 → Lose (calculated %) → Next: $100 (step back)

Author: Trading Team
License: MIT
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from nautilus_trader.common.enums import LogColor
from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.model.data import Bar, QuoteTick, TradeTick
from nautilus_trader.model.enums import OrderSide, OrderType, TimeInForce, TriggerType
from nautilus_trader.model.events import OrderFilled, PositionOpened, PositionClosed
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.orders import MarketOrder, StopMarketOrder, LimitOrder
from nautilus_trader.model.position import Position
from nautilus_trader.model.currencies import USD
from nautilus_trader.trading.strategy import Strategy


class OneThreeMelihConfig(StrategyConfig, frozen=True):
    """
    Configuration for the One-Three-Melih Step-Back Risk Management Trading Bot.
    
    This configuration defines all parameters for the advanced balance management
    strategy including profit targets, dynamic loss calculations, and step progression.
    """
    
    # Core trading parameters
    instrument_id: InstrumentId = InstrumentId.from_str("EUR/USD.SIM")
    
    # Balance management parameters
    initial_balance: Decimal = Decimal("100.00")  # Starting balance in USD
    profit_target_percentage: Decimal = Decimal("30.0")  # 30% profit target
    
    # Trading timing parameters
    trade_delay_seconds: int = 5  # Delay between trades
    
    # Risk management
    max_consecutive_losses: int = 10  # Maximum consecutive losses before pause
    
    # Logging and monitoring
    log_level: str = "INFO"
    enable_detailed_logging: bool = True


class BalanceTracker:
    """
    Tracks balance progression and calculates dynamic stop loss percentages
    for the step-back strategy.
    """
    
    def __init__(self, initial_balance: Decimal, profit_percentage: Decimal):
        self.initial_balance = initial_balance
        self.profit_percentage = profit_percentage
        self.balance_history: List[Decimal] = [initial_balance]
        self.current_balance = initial_balance
        self.trade_count = 0
        
    def get_current_balance(self) -> Decimal:
        """Get the current trading balance."""
        return self.current_balance
    
    def get_profit_target(self) -> Decimal:
        """Calculate profit target for current balance."""
        balance_decimal = Decimal(str(self.current_balance))
        return balance_decimal * (self.profit_percentage / Decimal("100"))
    
    def get_stop_loss_percentage(self) -> Decimal:
        """
        Calculate dynamic stop loss percentage to step back to previous balance level.
        If at initial balance, use fixed 30% loss.
        """
        if len(self.balance_history) <= 1:
            # At initial balance, use fixed percentage
            return self.profit_percentage
        
        previous_balance = self.balance_history[-2]
        current_balance = self.current_balance
        
        # Calculate percentage needed to return to previous balance
        loss_amount = current_balance - previous_balance
        loss_percentage = (loss_amount / current_balance) * Decimal("100")
        
        return loss_percentage.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def get_stop_loss_amount(self) -> Decimal:
        """Calculate stop loss amount in USD."""
        loss_percentage = self.get_stop_loss_percentage()
        balance_decimal = Decimal(str(self.current_balance))
        return balance_decimal * (loss_percentage / Decimal("100"))
    
    def record_profit(self) -> Decimal:
        """Record a profitable trade and update balance."""
        self.trade_count += 1
        balance_decimal = Decimal(str(self.current_balance))
        new_balance = balance_decimal * (Decimal("1") + self.profit_percentage / Decimal("100"))
        self.balance_history.append(balance_decimal)
        self.current_balance = new_balance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.current_balance
    
    def record_loss(self) -> Decimal:
        """Record a losing trade and step back to previous balance."""
        self.trade_count += 1
        
        if len(self.balance_history) > 1:
            # Step back to previous balance
            previous_balance = self.balance_history[-1]
            self.balance_history.pop()  # Remove current level
            self.current_balance = previous_balance
        else:
            # At initial balance, stay at initial balance
            self.current_balance = self.initial_balance
            
        return self.current_balance
    
    def get_position_size(self, price: Price) -> Quantity:
        """Calculate position size based on current balance and EUR/USD price."""
        # Convert balance to EUR equivalent for position sizing
        balance_decimal = Decimal(str(self.current_balance))
        eur_amount = balance_decimal / Decimal(str(price))
        # Use standard lot sizing (round to nearest 1000 units)
        lot_size = (eur_amount / Decimal("1000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * Decimal("1000")
        # Minimum position size
        min_size = Decimal("1000")
        return Quantity(max(lot_size, min_size), precision=0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current balance tracker statistics."""
        current_balance_decimal = Decimal(str(self.current_balance))
        initial_balance_decimal = Decimal(str(self.initial_balance))
        
        return {
            "current_balance": float(current_balance_decimal),
            "initial_balance": float(initial_balance_decimal),
            "balance_history": [float(b) for b in self.balance_history],
            "trade_count": self.trade_count,
            "current_step": len(self.balance_history),
            "total_return_pct": float(((current_balance_decimal - initial_balance_decimal) / initial_balance_decimal) * Decimal("100")),
        }


class OneThreeMelihStrategy(Strategy):
    """
    One-Three-Melih: Advanced Step-Back Risk Management Trading Strategy
    
    This strategy implements a sophisticated balance management system where:
    1. Each trade uses the full available balance
    2. Profits increase the balance by 30% for the next trade
    3. Losses trigger a step-back to the previous balance level
    4. Dynamic stop loss calculations ensure precise balance stepping
    """
    
    def __init__(self, config: OneThreeMelihConfig) -> None:
        # Pass strategy name as string to the parent Strategy class
        super().__init__(config=config)
        
        # Configuration
        self.instrument_id = config.instrument_id
        self.trade_delay_seconds = config.trade_delay_seconds
        self.max_consecutive_losses = config.max_consecutive_losses
        
        # Balance management
        self.balance_tracker = BalanceTracker(
            config.initial_balance,
            config.profit_target_percentage
        )
        
        # Trading state
        self.current_position: Optional[Position] = None
        self.pending_orders = set()
        self.consecutive_losses = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Market data
        self.current_bid: Optional[Price] = None
        self.current_ask: Optional[Price] = None
        self.last_trade_time: Optional[datetime] = None
        
        # Logging setup
        self.setup_logging()
        
    def setup_logging(self) -> None:
        """Setup detailed logging for the strategy."""
        self.log.info("Initializing One-Three-Melih Strategy", LogColor.BLUE)
        self.log.info(f"Initial balance: ${self.balance_tracker.initial_balance}", LogColor.GREEN)
        self.log.info(f"Profit target: {self.balance_tracker.profit_percentage}%", LogColor.GREEN)
        self.log.info(f"Trading instrument: {self.instrument_id}", LogColor.GREEN)
    
    def on_start(self) -> None:
        """Called when strategy is started."""
        self.log.info("=== One-Three-Melih Strategy Started ===", LogColor.BLUE)
        
        # Subscribe to market data
        self.subscribe_quote_ticks(self.instrument_id)
        self.subscribe_trade_ticks(self.instrument_id)
        
        self.log.info("Subscribed to market data", LogColor.GREEN)
        self.log.info("Ready for trading signals...", LogColor.CYAN)
    
    def on_stop(self) -> None:
        """Called when strategy is stopped."""
        self.log.info("=== Strategy Stopped ===", LogColor.BLUE)
        self.print_final_statistics()
    
    def on_quote_tick(self, tick: QuoteTick) -> None:
        """Handle incoming quote tick data."""
        self.current_bid = tick.bid_price
        self.current_ask = tick.ask_price
        
        # Check for trading opportunity if no position exists
        if self.current_position is None and not self.pending_orders:
            self.evaluate_entry_signal()
    
    def on_trade_tick(self, tick: TradeTick) -> None:
        """Handle incoming trade tick data."""
        pass  # Not needed for this strategy
    
    def evaluate_entry_signal(self) -> None:
        """Evaluate whether to enter a new position."""
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.log.warning(f"Max consecutive losses ({self.max_consecutive_losses}) reached. Pausing trading.", LogColor.RED)
            return
        
        if self.current_ask is None:
            return
        
        # Check if enough time has passed since last trade
        if self.last_trade_time is not None:
            # Implementation would check time difference here
            pass
        
        # Enter a buy position (strategy always buys EUR/USD)
        self.enter_long_position()
    
    def enter_long_position(self) -> None:
        """Enter a long position with full balance allocation."""
        if self.current_ask is None:
            self.log.error("Cannot enter position: No current ask price", LogColor.RED)
            return
        
        # Calculate position size based on current balance
        position_size = self.balance_tracker.get_position_size(self.current_ask)
        
        # Calculate profit and stop loss levels
        profit_target_amount = self.balance_tracker.get_profit_target()
        stop_loss_amount = self.balance_tracker.get_stop_loss_amount()
        
        # Convert to price levels (simplified calculation for EUR/USD)
        entry_price = self.current_ask
        pip_value = Decimal("0.0001")  # Standard EUR/USD pip
        
        # Calculate price levels based on position size and amounts
        profit_pips = (profit_target_amount / position_size.as_decimal()) / pip_value
        stop_loss_pips = (stop_loss_amount / position_size.as_decimal()) / pip_value
        
        take_profit_price = Price(
            entry_price.as_decimal() + (profit_pips * pip_value),
            precision=entry_price.precision
        )
        stop_loss_price = Price(
            entry_price.as_decimal() - (stop_loss_pips * pip_value),
            precision=entry_price.precision
        )
        
        # Create market order
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=position_size,
            time_in_force=TimeInForce.GTC,
        )
        
        # Submit the order
        self.submit_order(order)
        self.pending_orders.add(order.client_order_id)
        
        # Log the trade entry
        balance_stats = self.balance_tracker.get_stats()
        self.log.info(f"=== ENTERING LONG POSITION ===", LogColor.CYAN)
        self.log.info(f"Entry Price: {entry_price}", LogColor.CYAN)
        self.log.info(f"Position Size: {position_size}", LogColor.CYAN)
        self.log.info(f"Current Balance: ${balance_stats['current_balance']:.2f}", LogColor.CYAN)
        self.log.info(f"Take Profit: {take_profit_price} (+${profit_target_amount:.2f})", LogColor.GREEN)
        self.log.info(f"Stop Loss: {stop_loss_price} (-${stop_loss_amount:.2f})", LogColor.YELLOW)
        self.log.info(f"Stop Loss %: {self.balance_tracker.get_stop_loss_percentage():.2f}%", LogColor.YELLOW)
        
    def on_order_filled(self, event: OrderFilled) -> None:
        """Handle order filled events."""
        if event.client_order_id in self.pending_orders:
            self.pending_orders.remove(event.client_order_id)
            
        self.log.info(f"Order filled: {event.order_side} {event.last_qty} @ {event.last_px}", LogColor.GREEN)
        
        # If this is an entry order, set up exit orders
        if event.order_side == OrderSide.BUY and self.current_position is None:
            self.setup_exit_orders(event.last_px)
    
    def setup_exit_orders(self, entry_price: Price) -> None:
        """Set up take profit and stop loss orders after position entry."""
        if self.current_position is None:
            return
        
        # Calculate exit levels
        profit_target_amount = self.balance_tracker.get_profit_target()
        stop_loss_amount = self.balance_tracker.get_stop_loss_amount()
        
        position_size = self.current_position.quantity
        pip_value = Decimal("0.0001")
        
        # Calculate price levels
        profit_pips = (profit_target_amount / position_size.as_decimal()) / pip_value
        stop_loss_pips = (stop_loss_amount / position_size.as_decimal()) / pip_value
        
        take_profit_price = Price(
            entry_price.as_decimal() + (profit_pips * pip_value),
            precision=entry_price.precision
        )
        stop_loss_price = Price(
            entry_price.as_decimal() - (stop_loss_pips * pip_value),
            precision=entry_price.precision
        )
        
        # Create take profit order
        tp_order = self.order_factory.limit(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=position_size,
            price=take_profit_price,
            time_in_force=TimeInForce.GTC,
        )
        
        # Create stop loss order
        sl_order = self.order_factory.stop_market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=position_size,
            trigger_price=stop_loss_price,
            time_in_force=TimeInForce.GTC,
        )
        
        # Submit exit orders
        self.submit_order(tp_order)
        self.submit_order(sl_order)
        
        self.log.info(f"Exit orders placed - TP: {take_profit_price}, SL: {stop_loss_price}", LogColor.BLUE)
    
    def on_position_opened(self, event: PositionOpened) -> None:
        """Handle position opened events."""
        self.current_position = self.cache.position(event.position_id)
        self.log.info(f"Position opened: {self.current_position}", LogColor.GREEN)
    
    def on_position_closed(self, event: PositionClosed) -> None:
        """Handle position closed events."""
        if self.current_position is None:
            return
        
        # Calculate trade result
        pnl = event.realized_pnl
        is_profit = pnl.as_decimal() > 0
        
        # Update statistics
        self.total_trades += 1
        self.last_trade_time = datetime.now()
        
        if is_profit:
            self.winning_trades += 1
            self.consecutive_losses = 0
            new_balance = self.balance_tracker.record_profit()
            self.log.info(f"=== PROFITABLE TRADE ===", LogColor.GREEN)
            self.log.info(f"Profit: {pnl}", LogColor.GREEN)
            self.log.info(f"New Balance: ${new_balance:.2f}", LogColor.GREEN)
        else:
            self.losing_trades += 1
            self.consecutive_losses += 1
            new_balance = self.balance_tracker.record_loss()
            self.log.info(f"=== LOSING TRADE ===", LogColor.RED)
            self.log.info(f"Loss: {pnl}", LogColor.RED)
            self.log.info(f"Stepped back to: ${new_balance:.2f}", LogColor.YELLOW)
            self.log.info(f"Consecutive losses: {self.consecutive_losses}", LogColor.RED)
        
        # Print balance statistics
        self.print_balance_statistics()
        
        # Reset position
        self.current_position = None
        
        # Cancel any remaining orders for this position
        self.cancel_all_orders(self.instrument_id)
        
        self.log.info("Position closed. Ready for next trade signal...", LogColor.CYAN)
    
    def print_balance_statistics(self) -> None:
        """Print current balance and trading statistics."""
        stats = self.balance_tracker.get_stats()
        
        self.log.info("=== BALANCE STATISTICS ===", LogColor.BLUE)
        self.log.info(f"Current Balance: ${stats['current_balance']:.2f}", LogColor.BLUE)
        self.log.info(f"Current Step: {stats['current_step']}", LogColor.BLUE)
        self.log.info(f"Total Return: {stats['total_return_pct']:.2f}%", LogColor.BLUE)
        self.log.info(f"Total Trades: {self.total_trades}", LogColor.BLUE)
        self.log.info(f"Win Rate: {(self.winning_trades/max(self.total_trades,1)*100):.1f}%", LogColor.BLUE)
        self.log.info(f"Balance History: {stats['balance_history']}", LogColor.BLUE)
    
    def print_final_statistics(self) -> None:
        """Print final strategy performance statistics."""
        stats = self.balance_tracker.get_stats()
        
        self.log.info("=== FINAL STRATEGY STATISTICS ===", LogColor.MAGENTA)
        self.log.info(f"Initial Balance: ${stats['initial_balance']:.2f}", LogColor.MAGENTA)
        self.log.info(f"Final Balance: ${stats['current_balance']:.2f}", LogColor.MAGENTA)
        self.log.info(f"Total Return: {stats['total_return_pct']:.2f}%", LogColor.MAGENTA)
        self.log.info(f"Total Trades: {self.total_trades}", LogColor.MAGENTA)
        self.log.info(f"Winning Trades: {self.winning_trades}", LogColor.MAGENTA)
        self.log.info(f"Losing Trades: {self.losing_trades}", LogColor.MAGENTA)
        self.log.info(f"Win Rate: {(self.winning_trades/max(self.total_trades,1)*100):.1f}%", LogColor.MAGENTA)
        self.log.info(f"Max Step Reached: {max(len(stats['balance_history']), 1)}", LogColor.MAGENTA)
        self.log.info(f"Final Step: {len(stats['balance_history'])}", LogColor.MAGENTA)
