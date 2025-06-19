"""
Configuration Management Module
Handles loading and validation of bot configuration from YAML and environment variables.
"""

import os
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import logging


@dataclass
class ExchangeConfig:
    """Exchange configuration settings."""
    name: str = "BINANCE"
    account_type: str = "USDT_FUTURE"
    testnet: bool = True
    us: bool = False
    base_url_http: Optional[str] = None
    base_url_ws: Optional[str] = None


@dataclass
class TradingConfig:
    """Trading configuration settings."""
    max_coins: int = 50
    min_24h_volume_usdt: float = 1000000.0
    exclude_stablecoins: bool = True
    exclude_fiat_pairs: bool = True
    max_active_positions: int = 5
    max_position_size_percent: float = 2.0
    max_risk_per_trade_percent: float = 1.0
    primary_timeframe: str = "1-MINUTE"
    secondary_timeframe: str = "5-MINUTE"


@dataclass
class StrategyConfig:
    """Strategy configuration settings."""
    name: str = "VolatilityBreakoutWithVolumeConfirmation"
    atr_period: int = 14
    bollinger_period: int = 20
    bollinger_std: float = 2.0
    rsi_period: int = 14
    volume_period: int = 20
    volume_threshold_multiplier: float = 1.5
    rsi_min: float = 30.0
    rsi_max: float = 70.0
    volatility_threshold_atr: float = 0.5
    stop_loss_atr_multiplier: float = 2.0
    take_profit_atr_multiplier: float = 3.0
    trailing_stop_atr_multiplier: float = 1.5
    max_drawdown_percent: float = 10.0
    daily_loss_limit_percent: float = 5.0


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    file_format: str = "detailed"
    log_to_file: bool = True
    log_to_console: bool = True
    max_file_size_mb: int = 50
    backup_count: int = 5


@dataclass
class ExecutionConfig:
    """Execution configuration settings."""
    reconciliation: bool = True
    reconciliation_lookback_mins: int = 1440
    filter_position_reports: bool = True
    timeout_connection: float = 30.0
    timeout_reconciliation: float = 10.0
    timeout_portfolio: float = 10.0
    timeout_disconnection: float = 10.0
    timeout_post_stop: float = 5.0
    max_retries: int = 3
    retry_delay_initial_ms: int = 1000
    retry_delay_max_ms: int = 10000


@dataclass
class SafetyConfig:
    """Safety configuration settings."""
    enable_emergency_stop: bool = True
    emergency_stop_loss_percent: float = 15.0
    max_consecutive_losses: int = 5
    max_api_errors_per_minute: int = 10
    max_leverage: float = 1.0
    force_reduce_only: bool = False


@dataclass
class BotConfig:
    """Main bot configuration container."""
    exchange: ExchangeConfig
    trading: TradingConfig
    strategy: StrategyConfig
    logging: LoggingConfig
    execution: ExecutionConfig
    safety: SafetyConfig
    
    # Environment variables
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    initial_balance: float = 10000.0
    debug_mode: bool = False


class ConfigManager:
    """Configuration manager for loading and validating bot settings."""
    
    def __init__(self, config_path: str = "config.yaml", env_path: str = ".env"):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
            env_path: Path to environment variables file
        """
        self.config_path = config_path
        self.env_path = env_path
        self.logger = logging.getLogger(__name__)
        
        # Load environment variables
        load_dotenv(env_path)
        
        # Load configuration
        self.config = self._load_config()
        
    def _load_config(self) -> BotConfig:
        """Load configuration from YAML file and environment variables."""
        try:
            # Load YAML configuration
            with open(self.config_path, 'r') as file:
                yaml_config = yaml.safe_load(file)
            
            # Create configuration objects
            exchange_config = ExchangeConfig(**yaml_config.get('exchange', {}))
            trading_config = TradingConfig(**yaml_config.get('trading', {}))
            strategy_config = StrategyConfig(**yaml_config.get('strategy', {}))
            logging_config = LoggingConfig(**yaml_config.get('logging', {}))
            execution_config = ExecutionConfig(**yaml_config.get('execution', {}))
            safety_config = SafetyConfig(**yaml_config.get('safety', {}))
            
            # Load environment variables
            api_key = os.getenv('BINANCE_TESTNET_API_KEY')
            api_secret = os.getenv('BINANCE_TESTNET_API_SECRET')
            initial_balance = float(os.getenv('INITIAL_BALANCE', '10000.0'))
            debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
            
            # Validate required environment variables
            if not api_key or not api_secret:
                raise ValueError(
                    "BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET "
                    "must be set in environment variables"
                )
            
            return BotConfig(
                exchange=exchange_config,
                trading=trading_config,
                strategy=strategy_config,
                logging=logging_config,
                execution=execution_config,
                safety=safety_config,
                api_key=api_key,
                api_secret=api_secret,
                initial_balance=initial_balance,
                debug_mode=debug_mode
            )
            
        except FileNotFoundError:
            self.logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            raise
    
    def get_config(self) -> BotConfig:
        """Get the loaded configuration."""
        return self.config
    
    def validate_config(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate trading settings
            if self.config.trading.max_position_size_percent <= 0 or self.config.trading.max_position_size_percent > 100:
                raise ValueError("max_position_size_percent must be between 0 and 100")
            
            if self.config.trading.max_risk_per_trade_percent <= 0 or self.config.trading.max_risk_per_trade_percent > 10:
                raise ValueError("max_risk_per_trade_percent must be between 0 and 10")
            
            # Validate strategy settings
            if self.config.strategy.atr_period <= 0:
                raise ValueError("atr_period must be positive")
            
            if self.config.strategy.bollinger_period <= 0:
                raise ValueError("bollinger_period must be positive")
            
            if self.config.strategy.rsi_min >= self.config.strategy.rsi_max:
                raise ValueError("rsi_min must be less than rsi_max")
            
            # Validate safety settings
            if self.config.safety.max_leverage <= 0:
                raise ValueError("max_leverage must be positive")
            
            self.logger.info("Configuration validation successful")
            return True
            
        except ValueError as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    def save_config(self, output_path: str = None) -> None:
        """
        Save current configuration to YAML file.
        
        Args:
            output_path: Path to save configuration file
        """
        output_path = output_path or f"{self.config_path}.backup"
        
        try:
            config_dict = {
                'exchange': asdict(self.config.exchange),
                'trading': asdict(self.config.trading),
                'strategy': asdict(self.config.strategy),
                'logging': asdict(self.config.logging),
                'execution': asdict(self.config.execution),
                'safety': asdict(self.config.safety)
            }
            
            with open(output_path, 'w') as file:
                yaml.dump(config_dict, file, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            raise
    
    def update_config(self, section: str, updates: Dict[str, Any]) -> None:
        """
        Update configuration section.
        
        Args:
            section: Configuration section name
            updates: Dictionary of updates to apply
        """
        try:
            config_section = getattr(self.config, section)
            
            for key, value in updates.items():
                if hasattr(config_section, key):
                    setattr(config_section, key, value)
                    self.logger.info(f"Updated {section}.{key} = {value}")
                else:
                    self.logger.warning(f"Unknown configuration key: {section}.{key}")
            
        except AttributeError:
            self.logger.error(f"Unknown configuration section: {section}")
            raise
    
    def get_nautilus_config(self) -> Dict[str, Any]:
        """
        Convert bot configuration to Nautilus-compatible format.
        
        Returns:
            Dictionary formatted for Nautilus TradingNodeConfig
        """
        from nautilus_trader.adapters.binance import BINANCE, BinanceAccountType
        from nautilus_trader.adapters.binance import BinanceDataClientConfig, BinanceExecClientConfig
        from nautilus_trader.config import InstrumentProviderConfig, LiveExecEngineConfig, LoggingConfig, TradingNodeConfig
        from nautilus_trader.model.identifiers import TraderId
        
        # Map account types
        account_type_map = {
            "SPOT": BinanceAccountType.SPOT,
            "USDT_FUTURE": BinanceAccountType.USDT_FUTURE,
            "COIN_FUTURE": BinanceAccountType.COIN_FUTURE,
            "MARGIN": BinanceAccountType.MARGIN,
            "ISOLATED_MARGIN": BinanceAccountType.ISOLATED_MARGIN
        }
        
        account_type = account_type_map.get(
            self.config.exchange.account_type, 
            BinanceAccountType.USDT_FUTURE
        )
        
        return {
            "trader_id": TraderId("TESTNET-VOL-001"),
            "logging": LoggingConfig(
                log_level=self.config.logging.level,
                log_level_file=self.config.logging.level,
                use_pyo3=True
            ),
            "exec_engine": LiveExecEngineConfig(
                reconciliation=self.config.execution.reconciliation,
                reconciliation_lookback_mins=self.config.execution.reconciliation_lookback_mins,
                filter_position_reports=self.config.execution.filter_position_reports,
            ),
            "data_clients": {
                BINANCE: BinanceDataClientConfig(
                    api_key=self.config.api_key,
                    api_secret=self.config.api_secret,
                    account_type=account_type,
                    base_url_http=self.config.exchange.base_url_http,
                    base_url_ws=self.config.exchange.base_url_ws,
                    us=self.config.exchange.us,
                    testnet=self.config.exchange.testnet,
                    instrument_provider=InstrumentProviderConfig(load_all=True),
                )
            },
            "exec_clients": {
                BINANCE: BinanceExecClientConfig(
                    api_key=self.config.api_key,
                    api_secret=self.config.api_secret,
                    account_type=account_type,
                    base_url_http=self.config.exchange.base_url_http,
                    base_url_ws=self.config.exchange.base_url_ws,
                    us=self.config.exchange.us,
                    testnet=self.config.exchange.testnet,
                    instrument_provider=InstrumentProviderConfig(load_all=True),
                    max_retries=self.config.execution.max_retries,
                    retry_delay_initial_ms=self.config.execution.retry_delay_initial_ms,
                    retry_delay_max_ms=self.config.execution.retry_delay_max_ms,
                )
            },
            "timeout_connection": self.config.execution.timeout_connection,
            "timeout_reconciliation": self.config.execution.timeout_reconciliation,
            "timeout_portfolio": self.config.execution.timeout_portfolio,
            "timeout_disconnection": self.config.execution.timeout_disconnection,
            "timeout_post_stop": self.config.execution.timeout_post_stop,
        }


# Global configuration instance
config_manager = ConfigManager()

def get_config() -> BotConfig:
    """Get global configuration instance."""
    return config_manager.get_config()

def get_nautilus_config() -> Dict[str, Any]:
    """Get Nautilus-compatible configuration."""
    return config_manager.get_nautilus_config()
