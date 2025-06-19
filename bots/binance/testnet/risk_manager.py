"""
Risk Management Module
Implements comprehensive risk management and position sizing for the trading bot.
"""

import logging
from typing import Dict, Optional, List, Tuple
from decimal import Decimal, ROUND_DOWN
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque

from nautilus_trader.model.data import Bar, QuoteTick
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.position import Position
from nautilus_trader.model.enums import OrderSide, PositionSide
from nautilus_trader.model.objects import Price, Quantity, Money

from config import get_config


@dataclass
class RiskMetrics:
    """Risk metrics for a position or portfolio."""
    exposure: float
    risk: float
    reward: float
    risk_reward_ratio: float
    position_size: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    max_loss: float


@dataclass
class PortfolioRisk:
    """Portfolio-level risk metrics."""
    total_exposure: float
    total_risk: float
    daily_pnl: float
    max_drawdown: float
    active_positions: int
    risk_utilization: float  # Percentage of available risk used


class RiskManager:
    """
    Comprehensive risk management system for the trading bot.
    
    Features:
    - Position sizing based on ATR and account balance
    - Portfolio-level risk limits
    - Drawdown protection
    - Daily loss limits
    - Emergency stop mechanisms
    """
    
    def __init__(self):
        """Initialize risk manager."""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        
        # Risk tracking
        self.daily_pnl = 0.0
        self.max_drawdown = 0.0
        self.peak_equity = 0.0
        self.consecutive_losses = 0
        self.last_reset_date = datetime.now().date()
        
        # Position tracking
        self.active_positions: Dict[InstrumentId, Position] = {}
        self.position_risks: Dict[InstrumentId, RiskMetrics] = {}
        
        # Performance tracking
        self.trade_history: deque = deque(maxlen=1000)
        self.daily_trades = 0
        self.api_error_count = 0
        self.last_api_error_time = datetime.now()
        
        # Emergency stop flag
        self.emergency_stop_triggered = False
        
    def calculate_position_size(self, 
                               instrument: Instrument,
                               entry_price: Price,
                               stop_loss: Price,
                               atr_value: float,
                               account_balance: Money) -> Quantity:
        """
        Calculate position size based on risk management rules.
        
        Args:
            instrument: Trading instrument
            entry_price: Planned entry price
            stop_loss: Stop loss price
            atr_value: Average True Range value
            account_balance: Account balance
            
        Returns:
            Calculated position size
        """
        try:
            # Calculate risk per trade in account currency
            risk_amount = float(account_balance.as_double()) * (
                self.config.strategy.max_risk_per_trade_percent / 100.0
            )
            
            # Calculate price difference (risk per unit)
            price_diff = abs(float(entry_price.as_double()) - float(stop_loss.as_double()))
            
            if price_diff <= 0:
                self.logger.warning("Invalid price difference for position sizing")
                return Quantity.zero(instrument.size_precision)
            
            # Calculate raw position size
            raw_size = risk_amount / price_diff
            
            # Apply maximum position size limit
            max_position_value = float(account_balance.as_double()) * (
                self.config.trading.max_position_size_percent / 100.0
            )
            max_size_by_value = max_position_value / float(entry_price.as_double())
            
            # Take the smaller of the two limits
            final_size = min(raw_size, max_size_by_value)
            
            # Round down to instrument precision
            size_decimal = Decimal(str(final_size)).quantize(
                Decimal('0.' + '0' * instrument.size_precision),
                rounding=ROUND_DOWN
            )
            
            # Ensure minimum size
            min_size = Decimal(str(instrument.min_quantity.as_double()))
            if size_decimal < min_size:
                size_decimal = min_size
            
            position_size = Quantity(size_decimal, instrument.size_precision)
            
            self.logger.info(
                f"Position size calculated for {instrument.id.symbol}: "
                f"{position_size} (risk: ${risk_amount:.2f}, "
                f"price_diff: ${price_diff:.4f})"
            )
            
            return position_size
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return Quantity.zero(instrument.size_precision)
    
    def calculate_stop_loss(self, 
                           entry_price: Price, 
                           atr_value: float, 
                           side: OrderSide) -> Price:
        """
        Calculate stop loss price based on ATR.
        
        Args:
            entry_price: Entry price
            atr_value: Average True Range value
            side: Order side (BUY/SELL)
            
        Returns:
            Stop loss price
        """
        try:
            entry_value = float(entry_price.as_double())
            stop_distance = atr_value * self.config.strategy.stop_loss_atr_multiplier
            
            if side == OrderSide.BUY:
                stop_price = entry_value - stop_distance
            else:  # SELL
                stop_price = entry_value + stop_distance
            
            # Ensure stop price is positive
            stop_price = max(stop_price, 0.0001)
            
            return Price(stop_price, entry_price.precision)
            
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {e}")
            return entry_price  # Fallback to entry price
    
    def calculate_take_profit(self, 
                             entry_price: Price, 
                             atr_value: float, 
                             side: OrderSide) -> Price:
        """
        Calculate take profit price based on ATR.
        
        Args:
            entry_price: Entry price
            atr_value: Average True Range value
            side: Order side (BUY/SELL)
            
        Returns:
            Take profit price
        """
        try:
            entry_value = float(entry_price.as_double())
            profit_distance = atr_value * self.config.strategy.take_profit_atr_multiplier
            
            if side == OrderSide.BUY:
                profit_price = entry_value + profit_distance
            else:  # SELL
                profit_price = entry_value - profit_distance
            
            # Ensure profit price is positive
            profit_price = max(profit_price, 0.0001)
            
            return Price(profit_price, entry_price.precision)
            
        except Exception as e:
            self.logger.error(f"Error calculating take profit: {e}")
            return entry_price  # Fallback to entry price
    
    def calculate_trailing_stop(self, 
                               current_price: Price, 
                               position: Position, 
                               atr_value: float) -> Optional[Price]:
        """
        Calculate trailing stop price.
        
        Args:
            current_price: Current market price
            position: Active position
            atr_value: Average True Range value
            
        Returns:
            New trailing stop price or None if no update needed
        """
        try:
            current_value = float(current_price.as_double())
            trailing_distance = atr_value * self.config.strategy.trailing_stop_atr_multiplier
            
            if position.side == PositionSide.LONG:
                new_stop = current_value - trailing_distance
                # Only update if new stop is higher (favorable)
                if position.closing_last_px and new_stop > float(position.closing_last_px.as_double()):
                    return Price(new_stop, current_price.precision)
            else:  # SHORT
                new_stop = current_value + trailing_distance
                # Only update if new stop is lower (favorable)
                if position.closing_last_px and new_stop < float(position.closing_last_px.as_double()):
                    return Price(new_stop, current_price.precision)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error calculating trailing stop: {e}")
            return None
    
    def validate_trade_entry(self, 
                           instrument_id: InstrumentId, 
                           side: OrderSide, 
                           quantity: Quantity,
                           price: Price) -> Tuple[bool, str]:
        """
        Validate if a new trade entry is allowed.
        
        Args:
            instrument_id: Instrument identifier
            side: Order side
            quantity: Order quantity
            price: Order price
            
        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            # Check emergency stop
            if self.emergency_stop_triggered:
                return False, "Emergency stop is active"
            
            # Check daily loss limit
            if self.daily_pnl <= -self.config.strategy.daily_loss_limit_percent:
                return False, "Daily loss limit exceeded"
            
            # Check maximum drawdown
            if self.max_drawdown >= self.config.strategy.max_drawdown_percent:
                return False, "Maximum drawdown exceeded"
            
            # Check consecutive losses
            if self.consecutive_losses >= self.config.safety.max_consecutive_losses:
                return False, "Maximum consecutive losses exceeded"
            
            # Check maximum active positions
            if len(self.active_positions) >= self.config.trading.max_active_positions:
                return False, "Maximum active positions reached"
            
            # Check if position already exists for this instrument
            if instrument_id in self.active_positions:
                return False, f"Position already exists for {instrument_id.symbol}"
            
            # Check minimum trade size
            if quantity.as_double() <= 0:
                return False, "Invalid quantity"
            
            # All checks passed
            return True, "Trade validated"
            
        except Exception as e:
            self.logger.error(f"Error validating trade entry: {e}")
            return False, f"Validation error: {e}"
    
    def update_position_risk(self, 
                           instrument_id: InstrumentId, 
                           position: Position,
                           current_price: Price,
                           atr_value: float) -> RiskMetrics:
        """
        Update risk metrics for a position.
        
        Args:
            instrument_id: Instrument identifier
            position: Current position
            current_price: Current market price
            atr_value: Average True Range value
            
        Returns:
            Updated risk metrics
        """
        try:
            current_value = float(current_price.as_double())
            position_value = float(position.quantity.as_double()) * current_value
            
            # Calculate unrealized PnL
            unrealized_pnl = float(position.unrealized_pnl(current_price).as_double()) if position.unrealized_pnl(current_price) else 0.0
            
            # Calculate stop loss and take profit if not set
            stop_loss_price = None
            take_profit_price = None
            
            if position.side == PositionSide.LONG:
                stop_loss_price = current_value - (atr_value * self.config.strategy.stop_loss_atr_multiplier)
                take_profit_price = current_value + (atr_value * self.config.strategy.take_profit_atr_multiplier)
            else:
                stop_loss_price = current_value + (atr_value * self.config.strategy.stop_loss_atr_multiplier)
                take_profit_price = current_value - (atr_value * self.config.strategy.take_profit_atr_multiplier)
            
            # Calculate max loss (risk)
            if stop_loss_price:
                max_loss = abs(position_value - (float(position.quantity.as_double()) * stop_loss_price))
            else:
                max_loss = position_value * 0.02  # 2% fallback
            
            # Calculate reward potential
            if take_profit_price:
                max_reward = abs((float(position.quantity.as_double()) * take_profit_price) - position_value)
            else:
                max_reward = position_value * 0.03  # 3% fallback
            
            risk_metrics = RiskMetrics(
                exposure=position_value,
                risk=max_loss,
                reward=max_reward,
                risk_reward_ratio=max_reward / max_loss if max_loss > 0 else 0,
                position_size=float(position.quantity.as_double()),
                stop_loss=stop_loss_price,
                take_profit=take_profit_price,
                max_loss=max_loss
            )
            
            self.position_risks[instrument_id] = risk_metrics
            return risk_metrics
            
        except Exception as e:
            self.logger.error(f"Error updating position risk for {instrument_id}: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, None, None, 0)
    
    def calculate_portfolio_risk(self, account_balance: Money) -> PortfolioRisk:
        """
        Calculate portfolio-level risk metrics.
        
        Args:
            account_balance: Current account balance
            
        Returns:
            Portfolio risk metrics
        """
        try:
            total_exposure = sum(risk.exposure for risk in self.position_risks.values())
            total_risk = sum(risk.risk for risk in self.position_risks.values())
            
            balance_value = float(account_balance.as_double())
            risk_utilization = (total_risk / balance_value * 100) if balance_value > 0 else 0
            
            portfolio_risk = PortfolioRisk(
                total_exposure=total_exposure,
                total_risk=total_risk,
                daily_pnl=self.daily_pnl,
                max_drawdown=self.max_drawdown,
                active_positions=len(self.active_positions),
                risk_utilization=risk_utilization
            )
            
            return portfolio_risk
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio risk: {e}")
            return PortfolioRisk(0, 0, 0, 0, 0, 0)
    
    def update_daily_pnl(self, pnl_change: float) -> None:
        """
        Update daily PnL tracking.
        
        Args:
            pnl_change: Change in PnL
        """
        # Reset daily tracking if new day
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_pnl = 0.0
            self.daily_trades = 0
            self.last_reset_date = current_date
            self.logger.info("Daily PnL tracking reset for new day")
        
        self.daily_pnl += pnl_change
        
        # Update drawdown tracking
        if self.daily_pnl > self.peak_equity:
            self.peak_equity = self.daily_pnl
        
        current_drawdown = ((self.peak_equity - self.daily_pnl) / 
                           max(abs(self.peak_equity), 1.0)) * 100
        
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
            self.logger.warning(f"New maximum drawdown: {self.max_drawdown:.2f}%")
    
    def record_trade_result(self, pnl: float, is_win: bool) -> None:
        """
        Record trade result for performance tracking.
        
        Args:
            pnl: Trade PnL
            is_win: Whether trade was profitable
        """
        self.trade_history.append({
            'timestamp': datetime.now(),
            'pnl': pnl,
            'is_win': is_win
        })
        
        self.daily_trades += 1
        
        # Update consecutive losses
        if is_win:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
        
        # Update daily PnL
        self.update_daily_pnl(pnl)
        
        self.logger.info(
            f"Trade recorded: PnL=${pnl:.2f}, "
            f"Win={is_win}, "
            f"Consecutive losses={self.consecutive_losses}"
        )
    
    def check_emergency_conditions(self, account_balance: Money) -> bool:
        """
        Check if emergency stop conditions are met.
        
        Args:
            account_balance: Current account balance
            
        Returns:
            True if emergency stop should be triggered
        """
        if not self.config.safety.enable_emergency_stop:
            return False
        
        try:
            # Check emergency loss threshold
            balance_value = float(account_balance.as_double())
            emergency_threshold = self.config.safety.emergency_stop_loss_percent
            
            if self.daily_pnl <= -(balance_value * emergency_threshold / 100):
                self.logger.critical("EMERGENCY STOP: Daily loss threshold exceeded")
                return True
            
            # Check maximum drawdown
            if self.max_drawdown >= emergency_threshold:
                self.logger.critical("EMERGENCY STOP: Maximum drawdown exceeded")
                return True
            
            # Check API error rate
            if self._check_api_error_rate():
                self.logger.critical("EMERGENCY STOP: High API error rate")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking emergency conditions: {e}")
            return False
    
    def _check_api_error_rate(self) -> bool:
        """Check if API error rate is too high."""
        current_time = datetime.now()
        time_diff = (current_time - self.last_api_error_time).total_seconds()
        
        # Reset counter if more than a minute has passed
        if time_diff > 60:
            self.api_error_count = 0
            self.last_api_error_time = current_time
            return False
        
        return self.api_error_count >= self.config.safety.max_api_errors_per_minute
    
    def trigger_emergency_stop(self) -> None:
        """Trigger emergency stop."""
        self.emergency_stop_triggered = True
        self.logger.critical("EMERGENCY STOP TRIGGERED - All trading halted")
    
    def reset_emergency_stop(self) -> None:
        """Reset emergency stop (manual intervention required)."""
        self.emergency_stop_triggered = False
        self.consecutive_losses = 0
        self.api_error_count = 0
        self.logger.warning("Emergency stop reset - Trading can resume")
    
    def get_risk_summary(self) -> Dict[str, float]:
        """
        Get summary of current risk metrics.
        
        Returns:
            Dictionary of risk metrics
        """
        return {
            'daily_pnl': self.daily_pnl,
            'max_drawdown': self.max_drawdown,
            'active_positions': len(self.active_positions),
            'consecutive_losses': self.consecutive_losses,
            'daily_trades': self.daily_trades,
            'emergency_stop': self.emergency_stop_triggered,
            'total_exposure': sum(risk.exposure for risk in self.position_risks.values()),
            'total_risk': sum(risk.risk for risk in self.position_risks.values())
        }
