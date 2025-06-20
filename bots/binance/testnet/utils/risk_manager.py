"""
Risk Management System for Binance Futures Testnet Bot

This module provides comprehensive risk management capabilities including:
- Position sizing based on account balance and volatility
- Stop loss and take profit management
- Daily and overall drawdown protection  
- Emergency stop mechanisms
- Leverage management
- Portfolio heat monitoring

The risk manager is designed to be conservative for testnet trading
while providing realistic risk management that could be used in production.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import asyncio

from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.position import Position
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.portfolio.portfolio import Portfolio

from config import get_config


@dataclass
class RiskMetrics:
    """Risk metrics for monitoring."""
    total_exposure: float
    daily_pnl: float
    unrealized_pnl: float
    realized_pnl: float
    drawdown_pct: float
    max_drawdown_pct: float
    active_positions: int
    risk_score: float  # 0-100 scale


@dataclass
class PositionRisk:
    """Risk assessment for a single position."""
    instrument_id: InstrumentId
    position_size_usd: float
    leverage: int
    stop_loss_pct: float
    take_profit_pct: float
    unrealized_pnl: float
    risk_amount_usd: float
    heat_level: str  # LOW, MEDIUM, HIGH, CRITICAL


class RiskManager:
    """
    Comprehensive risk management system.
    
    Features:
    - Real-time position monitoring
    - Automatic stop loss/take profit calculation
    - Drawdown protection
    - Emergency stop mechanisms
    - Portfolio heat management
    - Leverage optimization
    """
    
    def __init__(self, config_manager):
        """
        Initialize risk manager.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Risk tracking
        self.daily_start_balance: float = 0.0
        self.session_start_balance: float = 0.0
        self.peak_balance: float = 0.0
        self.daily_trades: int = 0
        self.daily_realized_pnl: float = 0.0
        
        # Emergency flags
        self.emergency_stop_active: bool = False
        self.daily_limit_reached: bool = False
        self.drawdown_limit_reached: bool = False
        
        # Position tracking
        self.position_risks: Dict[InstrumentId, PositionRisk] = {}
        
        # Risk limits from config
        self.max_account_risk_pct = self.config.risk.max_account_risk_pct
        self.max_drawdown_pct = self.config.risk.max_drawdown_pct
        self.daily_loss_limit_pct = self.config.risk.daily_loss_limit_pct
        self.emergency_stop_loss_pct = self.config.risk.emergency_stop_loss_pct
        
        self.logger.info("Risk Manager initialized")
        self.logger.info(f"Max account risk: {self.max_account_risk_pct:.1%}")
        self.logger.info(f"Max drawdown: {self.max_drawdown_pct:.1%}")
        self.logger.info(f"Daily loss limit: {self.daily_loss_limit_pct:.1%}")
    
    def initialize_session(self, portfolio: Portfolio) -> None:
        """
        Initialize risk manager for a new trading session.
        
        Args:
            portfolio: Nautilus portfolio instance
        """
        # Get account balance
        accounts = portfolio.accounts()
        if accounts:
            account = list(accounts.values())[0]
            current_balance = account.balance().as_double()
            
            self.session_start_balance = current_balance
            self.peak_balance = current_balance
            
            # Reset daily tracking if new day
            now = datetime.now(timezone.utc)
            if not hasattr(self, '_last_reset_date') or self._last_reset_date.date() != now.date():
                self.daily_start_balance = current_balance
                self.daily_trades = 0
                self.daily_realized_pnl = 0.0
                self.daily_limit_reached = False
                self._last_reset_date = now
                
                self.logger.info(f"New trading day initialized - Balance: ${current_balance:.2f}")
        
        self.logger.info("Risk management session initialized")
    
    def can_open_position(self, 
                         portfolio: Portfolio,
                         instrument_id: InstrumentId,
                         side: OrderSide,
                         position_size_usd: float) -> Tuple[bool, str]:
        """
        Check if a new position can be opened based on risk limits.
        
        Args:
            portfolio: Nautilus portfolio instance
            instrument_id: Instrument to trade
            side: Order side (BUY/SELL)
            position_size_usd: Proposed position size in USD
            
        Returns:
            Tuple of (can_open, reason)
        """
        # Check emergency stop
        if self.emergency_stop_active:
            return False, "Emergency stop is active"
        
        # Check daily limits
        if self.daily_limit_reached:
            return False, "Daily loss limit reached"
        
        if self.drawdown_limit_reached:
            return False, "Maximum drawdown limit reached"
        
        # Check maximum positions
        open_positions = len([p for p in portfolio.positions_open()])
        max_positions = self.config.trading.max_open_positions
        
        if open_positions >= max_positions:
            return False, f"Maximum positions limit reached ({max_positions})"
        
        # Check total exposure
        current_exposure = self._calculate_total_exposure(portfolio)
        new_exposure = current_exposure + position_size_usd
        
        accounts = portfolio.accounts()
        if not accounts:
            return False, "No account found"
        
        account = list(accounts.values())[0]
        balance = account.balance().as_double()
        
        exposure_pct = new_exposure / balance
        if exposure_pct > self.max_account_risk_pct:
            return False, f"Total exposure would exceed limit ({exposure_pct:.1%} > {self.max_account_risk_pct:.1%})"
        
        # Check position size limits
        max_position_size = self.config.risk.max_position_size_usd
        if position_size_usd > max_position_size:
            return False, f"Position size exceeds maximum (${position_size_usd:.0f} > ${max_position_size:.0f})"
        
        # Check minimum position size
        min_position_size = self.config.trading.min_position_size_usd
        if position_size_usd < min_position_size:
            return False, f"Position size below minimum (${position_size_usd:.0f} < ${min_position_size:.0f})"
        
        # Check if already have position in same instrument
        existing_position = portfolio.position_for_instrument(instrument_id)
        if existing_position and existing_position.is_open:
            return False, f"Already have open position in {instrument_id}"
        
        return True, "Position approved"
    
    def calculate_position_size(self,
                              portfolio: Portfolio,
                              instrument: Instrument,
                              price: Price,
                              volatility: float = 0.02) -> Quantity:
        """
        Calculate optimal position size based on risk management rules.
        
        Args:
            portfolio: Nautilus portfolio instance
            instrument: Trading instrument
            price: Current price
            volatility: Estimated volatility (default 2%)
            
        Returns:
            Recommended position size
        """
        try:
            # Get account balance
            accounts = portfolio.accounts()
            if not accounts:
                return Quantity.zero(instrument.size_precision)
            
            account = list(accounts.values())[0]
            balance = account.balance().as_double()
            
            # Base position size from config
            position_pct = self.config.trading.max_position_size_pct
            base_size_usd = balance * position_pct
            
            # Adjust for volatility (higher volatility = smaller position)
            volatility_multiplier = max(0.5, 1.0 - (volatility - 0.02) * 10)
            adjusted_size_usd = base_size_usd * volatility_multiplier
            
            # Apply leverage
            leverage = self.config.trading.default_leverage
            leveraged_size_usd = adjusted_size_usd * leverage
            
            # Ensure within limits
            max_size = self.config.risk.max_position_size_usd
            min_size = self.config.trading.min_position_size_usd
            
            final_size_usd = max(min_size, min(leveraged_size_usd, max_size))
            
            # Convert to quantity
            price_value = price.as_double()
            quantity_raw = final_size_usd / price_value
            
            # Round to instrument precision
            quantity = Quantity.from_str(
                f"{quantity_raw:.{instrument.size_precision}f}"
            )
            
            self.logger.info(
                f"Position size calculation for {instrument.id}: "
                f"balance=${balance:.2f}, "
                f"base=${base_size_usd:.2f}, "
                f"volatility_adj={volatility_multiplier:.3f}, "
                f"leveraged=${leveraged_size_usd:.2f}, "
                f"final=${final_size_usd:.2f}, "
                f"quantity={quantity}"
            )
            
            return quantity
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return Quantity.zero(instrument.size_precision)
    
    def calculate_stop_loss_take_profit(self,
                                      entry_price: float,
                                      side: OrderSide,
                                      volatility: float = 0.02) -> Tuple[float, float]:
        """
        Calculate stop loss and take profit levels.
        
        Args:
            entry_price: Entry price
            side: Position side
            volatility: Estimated volatility
            
        Returns:
            Tuple of (stop_loss_price, take_profit_price)
        """
        # Base stop loss and take profit from config
        base_stop_pct = self.config.trading.stop_loss_pct
        base_profit_pct = self.config.trading.take_profit_pct
        
        # Adjust for volatility
        volatility_multiplier = max(0.5, min(2.0, volatility / 0.02))
        
        stop_pct = base_stop_pct * volatility_multiplier
        profit_pct = base_profit_pct * volatility_multiplier
        
        if side == OrderSide.BUY:
            # Long position
            stop_loss = entry_price * (1 - stop_pct)
            take_profit = entry_price * (1 + profit_pct)
        else:
            # Short position
            stop_loss = entry_price * (1 + stop_pct)
            take_profit = entry_price * (1 - profit_pct)
        
        self.logger.info(
            f"Stop/profit calculation: entry=${entry_price:.4f}, "
            f"volatility={volatility:.3f}, "
            f"stop=${stop_loss:.4f}, "
            f"profit=${take_profit:.4f}"
        )
        
        return stop_loss, take_profit
    
    def update_position_risk(self, position: Position) -> None:
        """
        Update risk metrics for a position.
        
        Args:
            position: Position to update
        """
        try:
            instrument_id = position.instrument_id
            
            # Calculate position value
            position_size_usd = abs(position.quantity.as_double() * position.avg_px_open.as_double())
            
            # Estimate risk amount (stop loss distance)
            entry_price = position.avg_px_open.as_double()
            stop_loss_pct = self.config.trading.stop_loss_pct
            risk_amount_usd = position_size_usd * stop_loss_pct
            
            # Get unrealized PnL
            unrealized_pnl = position.unrealized_pnl.as_double() if position.unrealized_pnl else 0.0
            
            # Calculate heat level
            heat_level = self._calculate_heat_level(risk_amount_usd, unrealized_pnl)
            
            # Create or update position risk
            position_risk = PositionRisk(
                instrument_id=instrument_id,
                position_size_usd=position_size_usd,
                leverage=self.config.trading.default_leverage,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=self.config.trading.take_profit_pct,
                unrealized_pnl=unrealized_pnl,
                risk_amount_usd=risk_amount_usd,
                heat_level=heat_level
            )
            
            self.position_risks[instrument_id] = position_risk
            
        except Exception as e:
            self.logger.error(f"Error updating position risk: {e}")
    
    def get_risk_metrics(self, portfolio: Portfolio) -> RiskMetrics:
        """
        Calculate comprehensive risk metrics.
        
        Args:
            portfolio: Nautilus portfolio instance
            
        Returns:
            Risk metrics object
        """
        try:
            # Get account info
            accounts = portfolio.accounts()
            if not accounts:
                return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 0)
            
            account = list(accounts.values())[0]
            current_balance = account.balance().as_double()
            
            # Calculate exposure
            total_exposure = self._calculate_total_exposure(portfolio)
            
            # Calculate PnL
            unrealized_pnl = sum(
                pos.unrealized_pnl.as_double() if pos.unrealized_pnl else 0.0
                for pos in portfolio.positions_open()
            )
            
            realized_pnl = current_balance - self.session_start_balance
            
            # Update peak balance
            if current_balance > self.peak_balance:
                self.peak_balance = current_balance
            
            # Calculate drawdown
            drawdown_pct = (self.peak_balance - current_balance) / self.peak_balance if self.peak_balance > 0 else 0.0
            max_drawdown_pct = self.max_drawdown_pct
            
            # Count active positions
            active_positions = len([p for p in portfolio.positions_open()])
            
            # Calculate risk score (0-100)
            risk_score = self._calculate_risk_score(
                total_exposure / current_balance if current_balance > 0 else 0,
                drawdown_pct,
                active_positions
            )
            
            return RiskMetrics(
                total_exposure=total_exposure,
                daily_pnl=self.daily_realized_pnl,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl,
                drawdown_pct=drawdown_pct,
                max_drawdown_pct=max_drawdown_pct,
                active_positions=active_positions,
                risk_score=risk_score
            )
            
        except Exception as e:
            self.logger.error(f"Error calculating risk metrics: {e}")
            return RiskMetrics(0, 0, 0, 0, 0, 0, 0, 100)  # High risk score on error
    
    def check_risk_limits(self, portfolio: Portfolio) -> List[str]:
        """
        Check all risk limits and return any violations.
        
        Args:
            portfolio: Nautilus portfolio instance
            
        Returns:
            List of risk violation messages
        """
        violations = []
        
        try:
            metrics = self.get_risk_metrics(portfolio)
            
            # Check drawdown limit
            if metrics.drawdown_pct > self.max_drawdown_pct:
                violations.append(f"Drawdown limit exceeded: {metrics.drawdown_pct:.1%}")
                self.drawdown_limit_reached = True
            
            # Check daily loss limit
            accounts = portfolio.accounts()
            if accounts:
                account = list(accounts.values())[0]
                current_balance = account.balance().as_double()
                daily_loss_pct = (self.daily_start_balance - current_balance) / self.daily_start_balance
                
                if daily_loss_pct > self.daily_loss_limit_pct:
                    violations.append(f"Daily loss limit exceeded: {daily_loss_pct:.1%}")
                    self.daily_limit_reached = True
            
            # Check emergency stop level
            if metrics.drawdown_pct > self.emergency_stop_loss_pct:
                violations.append(f"EMERGENCY: Stop loss triggered at {metrics.drawdown_pct:.1%}")
                self.emergency_stop_active = True
            
            # Check total exposure
            if metrics.total_exposure > 0:
                accounts = portfolio.accounts()
                if accounts:
                    account = list(accounts.values())[0]
                    balance = account.balance().as_double()
                    exposure_pct = metrics.total_exposure / balance
                    
                    if exposure_pct > self.max_account_risk_pct:
                        violations.append(f"Total exposure limit exceeded: {exposure_pct:.1%}")
            
            # Log violations
            for violation in violations:
                self.logger.warning(f"RISK VIOLATION: {violation}")
            
        except Exception as e:
            self.logger.error(f"Error checking risk limits: {e}")
            violations.append("Error checking risk limits")
        
        return violations
    
    def _calculate_total_exposure(self, portfolio: Portfolio) -> float:
        """Calculate total portfolio exposure in USD."""
        total_exposure = 0.0
        
        for position in portfolio.positions_open():
            try:
                if position.quantity and position.avg_px_open:
                    position_value = abs(position.quantity.as_double() * position.avg_px_open.as_double())
                    total_exposure += position_value
            except Exception as e:
                self.logger.warning(f"Error calculating exposure for {position.instrument_id}: {e}")
        
        return total_exposure
    
    def _calculate_heat_level(self, risk_amount_usd: float, unrealized_pnl: float) -> str:
        """Calculate heat level for a position."""
        if unrealized_pnl < -risk_amount_usd * 0.8:
            return "CRITICAL"
        elif unrealized_pnl < -risk_amount_usd * 0.5:
            return "HIGH"
        elif unrealized_pnl < -risk_amount_usd * 0.2:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_risk_score(self, exposure_pct: float, drawdown_pct: float, positions: int) -> float:
        """Calculate overall risk score (0-100)."""
        # Exposure component (0-40 points)
        exposure_score = min(40, exposure_pct * 200)  # 20% exposure = 40 points
        
        # Drawdown component (0-40 points)
        drawdown_score = min(40, drawdown_pct * 400)  # 10% drawdown = 40 points
        
        # Position count component (0-20 points)
        max_positions = self.config.trading.max_open_positions
        position_score = min(20, (positions / max_positions) * 20)
        
        total_score = exposure_score + drawdown_score + position_score
        return min(100, total_score)
    
    def emergency_stop(self) -> None:
        """Activate emergency stop."""
        self.emergency_stop_active = True
        self.logger.critical("EMERGENCY STOP ACTIVATED")
    
    def reset_emergency_stop(self) -> None:
        """Reset emergency stop (manual intervention)."""
        self.emergency_stop_active = False
        self.daily_limit_reached = False
        self.drawdown_limit_reached = False
        self.logger.info("Emergency stop reset")
    
    def log_risk_summary(self, portfolio: Portfolio) -> None:
        """Log a comprehensive risk summary."""
        try:
            metrics = self.get_risk_metrics(portfolio)
            
            self.logger.info("=== RISK SUMMARY ===")
            self.logger.info(f"Total Exposure: ${metrics.total_exposure:,.2f}")
            self.logger.info(f"Daily PnL: ${metrics.daily_pnl:,.2f}")
            self.logger.info(f"Unrealized PnL: ${metrics.unrealized_pnl:,.2f}")
            self.logger.info(f"Drawdown: {metrics.drawdown_pct:.1%}")
            self.logger.info(f"Active Positions: {metrics.active_positions}")
            self.logger.info(f"Risk Score: {metrics.risk_score:.0f}/100")
            self.logger.info(f"Emergency Stop: {self.emergency_stop_active}")
            
        except Exception as e:
            self.logger.error(f"Error logging risk summary: {e}")
