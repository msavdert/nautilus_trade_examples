"""
Configuration management for Binance Spot Trading Client
Handles environment variables and settings validation
"""
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseSettings, Field, validator
from pydantic_settings import SettingsConfigDict


class Config(BaseSettings):
    """Main configuration class using Pydantic for validation"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # API Credentials
    binance_api_key: str = Field(..., description="Binance API Key")
    binance_secret_key: str = Field(..., description="Binance Secret Key")
    
    # Environment Settings
    environment: str = Field(default="sandbox", description="Environment: sandbox, testnet, live")
    testnet: bool = Field(default=True, description="Use testnet endpoints")
    
    # Client Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Rate Limiting
    rate_limit_requests_per_minute: int = Field(default=1200, description="Request rate limit")
    rate_limit_weight_per_minute: int = Field(default=6000, description="Weight rate limit")
    
    # WebSocket Configuration
    ws_ping_interval: int = Field(default=20, description="WebSocket ping interval")
    ws_ping_timeout: int = Field(default=10, description="WebSocket ping timeout")
    ws_max_reconnect_attempts: int = Field(default=5, description="Max reconnection attempts")
    
    # Market Data
    default_symbols: str = Field(default="BTCUSDT,ETHUSDT,ADAUSDT", description="Default trading symbols")
    default_intervals: str = Field(default="1m,5m,1h", description="Default kline intervals")
    
    # Strategy Configuration
    strategy_enabled: bool = Field(default=False, description="Enable trading strategy")
    strategy_name: str = Field(default="simple_buy_hold", description="Strategy name")
    strategy_parameters: str = Field(default="{}", description="Strategy parameters as JSON string")
    
    # Risk Management
    max_position_size_percent: float = Field(default=10.0, description="Max position size as % of balance")
    max_daily_loss_percent: float = Field(default=5.0, description="Max daily loss as % of balance")
    stop_loss_percent: float = Field(default=2.0, description="Stop loss percentage")
    take_profit_percent: float = Field(default=5.0, description="Take profit percentage")
    
    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v):
        valid_envs = ["sandbox", "testnet", "live"]
        if v.lower() not in valid_envs:
            raise ValueError(f"environment must be one of {valid_envs}")
        return v.lower()
    
    @property
    def base_url(self) -> str:
        """Get the appropriate Binance API base URL"""
        if self.testnet or self.environment == "testnet":
            return "https://testnet.binance.vision"
        return "https://api.binance.com"
    
    @property
    def ws_base_url(self) -> str:
        """Get the appropriate Binance WebSocket base URL"""
        if self.testnet or self.environment == "testnet":
            return "wss://testnet.binance.vision"
        return "wss://stream.binance.com:9443"
    
    @property
    def symbols_list(self) -> List[str]:
        """Get default symbols as a list"""
        return [s.strip().upper() for s in self.default_symbols.split(",")]
    
    @property
    def intervals_list(self) -> List[str]:
        """Get default intervals as a list"""
        return [i.strip() for i in self.default_intervals.split(",")]
    
    @property
    def strategy_params_dict(self) -> Dict[str, Any]:
        """Parse strategy parameters from JSON string"""
        import json
        try:
            return json.loads(self.strategy_parameters)
        except json.JSONDecodeError:
            return {}
    
    def get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests"""
        return {
            "X-MBX-APIKEY": self.binance_api_key,
            "Content-Type": "application/json"
        }


# Global config instance
_config: Optional[Config] = None

def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
