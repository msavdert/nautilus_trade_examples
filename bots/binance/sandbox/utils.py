"""
Utility Functions Module
Common helper functions and utilities for the trading bot.
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
import pandas as pd
import numpy as np

from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.data import Bar
from nautilus_trader.model.identifiers import InstrumentId


class DataProcessor:
    """Data processing utilities for market data."""
    
    @staticmethod
    def calculate_atr(high: List[float], low: List[float], close: List[float], period: int = 14) -> float:
        """
        Calculate Average True Range (ATR).
        
        Args:
            high: List of high prices
            low: List of low prices
            close: List of close prices
            period: ATR period
            
        Returns:
            ATR value
        """
        if len(high) < period + 1:
            return 0.0
        
        try:
            df = pd.DataFrame({
                'high': high,
                'low': low,
                'close': close
            })
            
            # Calculate True Range
            df['prev_close'] = df['close'].shift(1)
            df['tr1'] = df['high'] - df['low']
            df['tr2'] = abs(df['high'] - df['prev_close'])
            df['tr3'] = abs(df['low'] - df['prev_close'])
            df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
            
            # Calculate ATR
            atr = df['tr'].rolling(window=period).mean().iloc[-1]
            return float(atr) if not pd.isna(atr) else 0.0
            
        except Exception as e:
            logging.error(f"Error calculating ATR: {e}")
            return 0.0
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """
        Calculate Bollinger Bands.
        
        Args:
            prices: List of prices
            period: Moving average period
            std_dev: Standard deviation multiplier
            
        Returns:
            Dictionary with upper, middle, lower bands
        """
        if len(prices) < period:
            return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}
        
        try:
            df = pd.DataFrame({'price': prices})
            df['sma'] = df['price'].rolling(window=period).mean()
            df['std'] = df['price'].rolling(window=period).std()
            
            latest_sma = df['sma'].iloc[-1]
            latest_std = df['std'].iloc[-1]
            
            if pd.isna(latest_sma) or pd.isna(latest_std):
                return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}
            
            return {
                'upper': latest_sma + (std_dev * latest_std),
                'middle': latest_sma,
                'lower': latest_sma - (std_dev * latest_std)
            }
            
        except Exception as e:
            logging.error(f"Error calculating Bollinger Bands: {e}")
            return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            prices: List of prices
            period: RSI period
            
        Returns:
            RSI value
        """
        if len(prices) < period + 1:
            return 50.0  # Neutral RSI
        
        try:
            df = pd.DataFrame({'price': prices})
            df['change'] = df['price'].diff()
            df['gain'] = df['change'].where(df['change'] > 0, 0)
            df['loss'] = -df['change'].where(df['change'] < 0, 0)
            
            avg_gain = df['gain'].rolling(window=period).mean().iloc[-1]
            avg_loss = df['loss'].rolling(window=period).mean().iloc[-1]
            
            if pd.isna(avg_gain) or pd.isna(avg_loss) or avg_loss == 0:
                return 50.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return float(rsi)
            
        except Exception as e:
            logging.error(f"Error calculating RSI: {e}")
            return 50.0
    
    @staticmethod
    def calculate_volume_sma(volumes: List[float], period: int = 20) -> float:
        """
        Calculate Simple Moving Average of volume.
        
        Args:
            volumes: List of volume values
            period: SMA period
            
        Returns:
            Volume SMA
        """
        if len(volumes) < period:
            return sum(volumes) / len(volumes) if volumes else 0.0
        
        try:
            recent_volumes = volumes[-period:]
            return sum(recent_volumes) / len(recent_volumes)
        except Exception as e:
            logging.error(f"Error calculating volume SMA: {e}")
            return 0.0


class PriceUtils:
    """Price manipulation and formatting utilities."""
    
    @staticmethod
    def round_to_tick_size(price: float, tick_size: float) -> float:
        """
        Round price to nearest tick size.
        
        Args:
            price: Price to round
            tick_size: Minimum price increment
            
        Returns:
            Rounded price
        """
        if tick_size <= 0:
            return price
        
        return round(price / tick_size) * tick_size
    
    @staticmethod
    def round_to_lot_size(quantity: float, lot_size: float) -> float:
        """
        Round quantity to nearest lot size.
        
        Args:
            quantity: Quantity to round
            lot_size: Minimum quantity increment
            
        Returns:
            Rounded quantity
        """
        if lot_size <= 0:
            return quantity
        
        return round(quantity / lot_size) * lot_size
    
    @staticmethod
    def format_price(price: Union[float, Price], precision: int = 4) -> str:
        """
        Format price for display.
        
        Args:
            price: Price to format
            precision: Decimal precision
            
        Returns:
            Formatted price string
        """
        if isinstance(price, Price):
            price = price.as_double()
        
        return f"{price:.{precision}f}"
    
    @staticmethod
    def format_quantity(quantity: Union[float, Quantity], precision: int = 6) -> str:
        """
        Format quantity for display.
        
        Args:
            quantity: Quantity to format
            precision: Decimal precision
            
        Returns:
            Formatted quantity string
        """
        if isinstance(quantity, Quantity):
            quantity = quantity.as_double()
        
        return f"{quantity:.{precision}f}"
    
    @staticmethod
    def calculate_notional_value(price: float, quantity: float) -> float:
        """
        Calculate notional value of a position.
        
        Args:
            price: Asset price
            quantity: Position quantity
            
        Returns:
            Notional value
        """
        return price * quantity
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """
        Calculate percentage change between two values.
        
        Args:
            old_value: Original value
            new_value: New value
            
        Returns:
            Percentage change
        """
        if old_value == 0:
            return 0.0
        
        return ((new_value - old_value) / old_value) * 100


class TimeUtils:
    """Time and date utilities."""
    
    @staticmethod
    def get_market_hours(timezone: str = "UTC") -> Dict[str, str]:
        """
        Get market hours for different regions.
        
        Args:
            timezone: Timezone string
            
        Returns:
            Dictionary of market hours
        """
        # Binance operates 24/7, but here are traditional market hours
        return {
            "crypto": "24/7",
            "us_stocks": "09:30-16:00 EST",
            "forex": "24/5",
            "london": "08:00-16:30 GMT",
            "tokyo": "09:00-15:00 JST"
        }
    
    @staticmethod
    def is_market_open(market: str = "crypto") -> bool:
        """
        Check if market is currently open.
        
        Args:
            market: Market type
            
        Returns:
            True if market is open
        """
        if market.lower() == "crypto":
            return True  # Crypto markets are always open
        
        # Add logic for other markets if needed
        return True
    
    @staticmethod
    def format_timestamp(timestamp: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Format timestamp for display.
        
        Args:
            timestamp: Datetime object
            format_str: Format string
            
        Returns:
            Formatted timestamp string
        """
        return timestamp.strftime(format_str)
    
    @staticmethod
    def get_trading_session(timestamp: datetime) -> str:
        """
        Determine trading session based on timestamp.
        
        Args:
            timestamp: Datetime object
            
        Returns:
            Trading session name
        """
        hour = timestamp.hour
        
        if 0 <= hour < 6:
            return "ASIAN_LATE"
        elif 6 <= hour < 12:
            return "EUROPEAN"
        elif 12 <= hour < 18:
            return "AMERICAN"
        else:
            return "ASIAN_EARLY"


class ValidationUtils:
    """Data validation utilities."""
    
    @staticmethod
    def validate_price(price: float, min_price: float = 0.0, max_price: float = float('inf')) -> bool:
        """
        Validate price value.
        
        Args:
            price: Price to validate
            min_price: Minimum allowed price
            max_price: Maximum allowed price
            
        Returns:
            True if price is valid
        """
        return (isinstance(price, (int, float)) and
                not np.isnan(price) and
                not np.isinf(price) and
                min_price <= price <= max_price)
    
    @staticmethod
    def validate_quantity(quantity: float, min_qty: float = 0.0) -> bool:
        """
        Validate quantity value.
        
        Args:
            quantity: Quantity to validate
            min_qty: Minimum allowed quantity
            
        Returns:
            True if quantity is valid
        """
        return (isinstance(quantity, (int, float)) and
                not np.isnan(quantity) and
                not np.isinf(quantity) and
                quantity >= min_qty)
    
    @staticmethod
    def validate_instrument_id(instrument_id: InstrumentId) -> bool:
        """
        Validate instrument ID.
        
        Args:
            instrument_id: Instrument ID to validate
            
        Returns:
            True if instrument ID is valid
        """
        return (instrument_id is not None and
                hasattr(instrument_id, 'symbol') and
                hasattr(instrument_id, 'venue'))
    
    @staticmethod
    def sanitize_symbol(symbol: str) -> str:
        """
        Sanitize trading symbol.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Sanitized symbol
        """
        return symbol.upper().strip()


class LoggingUtils:
    """Logging and monitoring utilities."""
    
    @staticmethod
    def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
        """
        Setup logger with specified configuration.
        
        Args:
            name: Logger name
            level: Logging level
            log_file: Optional log file path
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    @staticmethod
    def log_trade_summary(logger: logging.Logger, 
                         symbol: str, 
                         side: str, 
                         quantity: float, 
                         price: float, 
                         pnl: Optional[float] = None) -> None:
        """
        Log trade summary.
        
        Args:
            logger: Logger instance
            symbol: Trading symbol
            side: Order side
            quantity: Trade quantity
            price: Trade price
            pnl: Profit/Loss (optional)
        """
        pnl_str = f", PnL: ${pnl:.2f}" if pnl is not None else ""
        
        logger.info(
            f"TRADE: {side} {quantity:.6f} {symbol} @ ${price:.4f}{pnl_str}"
        )
    
    @staticmethod
    def log_performance_metrics(logger: logging.Logger, metrics: Dict[str, Any]) -> None:
        """
        Log performance metrics.
        
        Args:
            logger: Logger instance
            metrics: Performance metrics dictionary
        """
        logger.info("=== PERFORMANCE METRICS ===")
        for key, value in metrics.items():
            if isinstance(value, float):
                logger.info(f"{key}: {value:.4f}")
            else:
                logger.info(f"{key}: {value}")


class MathUtils:
    """Mathematical utilities and calculations."""
    
    @staticmethod
    def calculate_compound_growth_rate(initial: float, final: float, periods: int) -> float:
        """
        Calculate compound annual growth rate.
        
        Args:
            initial: Initial value
            final: Final value
            periods: Number of periods
            
        Returns:
            Compound growth rate
        """
        if initial <= 0 or periods <= 0:
            return 0.0
        
        return (pow(final / initial, 1 / periods) - 1) * 100
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            returns: List of returns
            risk_free_rate: Risk-free rate
            
        Returns:
            Sharpe ratio
        """
        if not returns:
            return 0.0
        
        try:
            returns_array = np.array(returns)
            excess_returns = returns_array - risk_free_rate
            
            if np.std(excess_returns) == 0:
                return 0.0
            
            return np.mean(excess_returns) / np.std(excess_returns)
            
        except Exception as e:
            logging.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: List[float]) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            Maximum drawdown percentage
        """
        if not equity_curve:
            return 0.0
        
        try:
            equity_array = np.array(equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - peak) / peak * 100
            
            return abs(np.min(drawdown))
            
        except Exception as e:
            logging.error(f"Error calculating max drawdown: {e}")
            return 0.0
    
    @staticmethod
    def calculate_win_rate(trades: List[bool]) -> float:
        """
        Calculate win rate from list of trade results.
        
        Args:
            trades: List of trade results (True for win, False for loss)
            
        Returns:
            Win rate percentage
        """
        if not trades:
            return 0.0
        
        wins = sum(trades)
        return (wins / len(trades)) * 100


class APIUtils:
    """API interaction utilities."""
    
    @staticmethod
    async def fetch_with_retry(session: aiohttp.ClientSession,
                              url: str,
                              params: Optional[Dict] = None,
                              max_retries: int = 3,
                              delay: float = 1.0) -> Optional[Dict]:
        """
        Fetch data from API with retry logic.
        
        Args:
            session: aiohttp session
            url: API endpoint URL
            params: Query parameters
            max_retries: Maximum retry attempts
            delay: Delay between retries
            
        Returns:
            API response data or None if failed
        """
        for attempt in range(max_retries):
            try:
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                logging.warning(f"API request failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                else:
                    logging.error(f"API request failed after {max_retries} attempts")
                    return None
                    
            except Exception as e:
                logging.error(f"Unexpected error in API request: {e}")
                return None
    
    @staticmethod
    def format_binance_symbol(base: str, quote: str, market_type: str = "spot") -> str:
        """
        Format symbol for Binance API.
        
        Args:
            base: Base asset
            quote: Quote asset
            market_type: Market type (spot, futures)
            
        Returns:
            Formatted symbol
        """
        symbol = f"{base.upper()}{quote.upper()}"
        
        if market_type.lower() == "futures":
            # Add perpetual suffix for futures
            if not symbol.endswith("PERP"):
                symbol += "-PERP"
        
        return symbol


def format_number(value: Union[int, float], precision: int = 2, use_thousands_separator: bool = True) -> str:
    """
    Format number for display.
    
    Args:
        value: Number to format
        precision: Decimal precision
        use_thousands_separator: Whether to use thousands separator
        
    Returns:
        Formatted number string
    """
    if use_thousands_separator:
        return f"{value:,.{precision}f}"
    else:
        return f"{value:.{precision}f}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division by zero
        
    Returns:
        Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between minimum and maximum.
    
    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))
