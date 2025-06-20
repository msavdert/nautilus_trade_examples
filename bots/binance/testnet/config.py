"""
Configuration management for Binance Futures Testnet Trading Bot.

This module handles all configuration aspects including:
- Environment variables and secrets
- Trading parameters
- Risk management settings
- Nautilus framework configuration
- US region-specific API endpoints

IMPORTANT: This bot is designed for Binance Futures Testnet ONLY.
Never use real API keys or mainnet endpoints.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, field
from decimal import Decimal

from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceExecClientConfig


@dataclass
class BinanceEndpoints:
    """
    Binance API endpoints configuration.
    
    CRITICAL: These are Testnet endpoints for US users.
    For production, these would need to be updated to mainnet URLs.
    """
    # Binance Futures Testnet endpoints (US region compatible)
    futures_base_url: str = "https://testnet.binancefuture.com"
    futures_ws_url: str = "wss://stream.binancefuture.com"
    
    # API endpoints
    futures_api_url: str = "https://testnet.binancefuture.com/fapi/v1"
    futures_ws_stream: str = "wss://stream.binancefuture.com/ws"
    
    def get_rest_api_url(self) -> str:
        """Get the REST API URL for Futures Testnet."""
        return self.futures_api_url
    
    def get_websocket_url(self) -> str:
        """Get the WebSocket URL for Futures Testnet."""
        return self.futures_ws_stream


@dataclass
class TradingConfig:
    """Trading strategy and execution parameters."""
    
    # Strategy parameters
    strategy_name: str = "RSI_MEAN_REVERSION"
    timeframe: str = "5m"  # 5-minute bars
    
    # RSI Mean Reversion Strategy Parameters
    rsi_period: int = 14
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    rsi_extreme_oversold: float = 20.0
    rsi_extreme_overbought: float = 80.0
    
    # Moving averages for trend filter
    ma_fast_period: int = 10
    ma_slow_period: int = 20
    
    # Volume confirmation
    volume_period: int = 20
    volume_threshold_multiplier: float = 1.2
    
    # Risk management
    max_position_size_pct: float = 0.05  # 5% of account per position
    min_position_size_usd: float = 10.0  # Minimum position size in USD
    max_position_size_usd: float = 1000.0  # Maximum position size in USD
    stop_loss_pct: float = 0.02  # 2% stop loss
    take_profit_pct: float = 0.04  # 4% take profit
    max_daily_loss_pct: float = 0.10  # 10% max daily loss
    max_open_positions: int = 3
    
    # Leverage (Futures specific)
    default_leverage: int = 5  # Conservative leverage for testnet
    max_leverage: int = 10
    
    # Coin selection
    top_coins_count: int = 50
    min_24h_volume_usdt: float = 10_000_000.0  # $10M minimum volume
    excluded_coins: List[str] = field(default_factory=lambda: ["USDCUSDT", "BUSDUSDT"])


@dataclass
class RiskConfig:
    """Risk management configuration."""
    
    # Account protection
    max_account_risk_pct: float = 0.15  # 15% max account risk
    emergency_stop_loss_pct: float = 0.20  # 20% emergency stop
    
    # Position sizing
    base_position_size_usd: float = 100.0  # Base position size in USD
    max_position_size_usd: float = 1000.0  # Max position size in USD
    
    # Drawdown protection
    max_drawdown_pct: float = 0.12  # 12% max drawdown
    daily_loss_limit_pct: float = 0.08  # 8% daily loss limit
    
    # Rate limiting
    max_orders_per_minute: int = 10
    max_api_calls_per_minute: int = 1200  # Binance limit is 1200/min


class ConfigManager:
    """
    Central configuration manager for the trading bot.
    
    Handles loading configuration from multiple sources:
    - Environment variables (.env file)
    - YAML configuration files
    - Default values
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = config_dir or Path(__file__).parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        # Load environment variables
        self._load_env_vars()
        
        # Initialize configuration objects
        self.endpoints = BinanceEndpoints()
        self.trading = TradingConfig()
        self.risk = RiskConfig()
    
    def _load_env_vars(self) -> None:
        """Load environment variables from .env file."""
        try:
            from dotenv import load_dotenv
            env_file = self.config_dir.parent / ".env"
            if env_file.exists():
                load_dotenv(env_file)
        except ImportError:
            pass
    
    def get_binance_credentials(self) -> Dict[str, str]:
        """
        Get Binance API credentials from environment variables.
        
        Returns:
            Dictionary containing API key and secret
            
        Raises:
            ValueError: If credentials are not found
        """
        api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError(
                "Binance Testnet API credentials not found. "
                "Please set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET "
                "environment variables."
            )
        
        return {
            "api_key": api_key,
            "api_secret": api_secret
        }
    
    def get_nautilus_config(self) -> TradingNodeConfig:
        """
        Create Nautilus framework configuration.
        
        Returns:
            TradingNodeConfig for Nautilus framework
        """
        credentials = self.get_binance_credentials()
        
        # Binance Futures Testnet configuration
        binance_config = {
            "account_type": BinanceAccountType.USDT_FUTURE,  # For USDT Futures
            "api_key": credentials["api_key"],
            "api_secret": credentials["api_secret"],
            "base_url_http": self.endpoints.futures_base_url,
            "base_url_ws": self.endpoints.futures_ws_url,
            "us": True,  # Important for US users
            "testnet": True,  # Explicitly mark as testnet
        }
        
        # Data client configuration
        data_client_config = BinanceDataClientConfig(
            **binance_config,
            handle_revised_bars=True,
        )
        
        # Execution client configuration
        exec_client_config = BinanceExecClientConfig(
            **binance_config,
            # No warn_gtd_to_gtc parameter in this version
        )
        
        # Trading node configuration  
        # Convert trader_id string to TraderId object
        from nautilus_trader.model.identifiers import TraderId
        
        trader_id_obj = TraderId("TESTNET-RSI-001")
        
        config = TradingNodeConfig(
            trader_id=trader_id_obj,
            data_clients={
                "BINANCE": data_client_config,
            },
            exec_clients={
                "BINANCE": exec_client_config,
            },
        )
        
        return config
    
    def save_config(self, filename: str = "config.yaml") -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            filename: Name of the configuration file
        """
        config_data = {
            "endpoints": {
                "futures_base_url": self.endpoints.futures_base_url,
                "futures_ws_url": self.endpoints.futures_ws_url,
                "futures_api_url": self.endpoints.futures_api_url,
                "futures_ws_stream": self.endpoints.futures_ws_stream,
            },
            "trading": {
                "strategy_name": self.trading.strategy_name,
                "timeframe": self.trading.timeframe,
                "rsi_period": self.trading.rsi_period,
                "rsi_oversold": self.trading.rsi_oversold,
                "rsi_overbought": self.trading.rsi_overbought,
                "max_position_size_pct": self.trading.max_position_size_pct,
                "stop_loss_pct": self.trading.stop_loss_pct,
                "take_profit_pct": self.trading.take_profit_pct,
                "default_leverage": self.trading.default_leverage,
                "top_coins_count": self.trading.top_coins_count,
            },
            "risk": {
                "max_account_risk_pct": self.risk.max_account_risk_pct,
                "emergency_stop_loss_pct": self.risk.emergency_stop_loss_pct,
                "max_drawdown_pct": self.risk.max_drawdown_pct,
                "daily_loss_limit_pct": self.risk.daily_loss_limit_pct,
            }
        }
        
        config_file = self.config_dir / filename
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, indent=2)
    
    def load_config(self, filename: str = "config.yaml") -> None:
        """
        Load configuration from YAML file.
        
        Args:
            filename: Name of the configuration file
        """
        config_file = self.config_dir / filename
        if not config_file.exists():
            return
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Update configuration objects
        if "trading" in config_data:
            for key, value in config_data["trading"].items():
                if hasattr(self.trading, key):
                    setattr(self.trading, key, value)
        
        if "risk" in config_data:
            for key, value in config_data["risk"].items():
                if hasattr(self.risk, key):
                    setattr(self.risk, key, value)


# Global configuration instance
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    return config_manager


def get_nautilus_config() -> TradingNodeConfig:
    """Get Nautilus framework configuration."""
    return config_manager.get_nautilus_config()
