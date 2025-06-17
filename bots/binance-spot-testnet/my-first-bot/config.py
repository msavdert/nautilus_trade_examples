#!/usr/bin/env python3

import os
from decimal import Decimal
from pathlib import Path
from dotenv import load_dotenv

from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.sandbox.config import SandboxExecutionClientConfig
from nautilus_trader.config import (
    CacheConfig,
    InstrumentProviderConfig,
    LiveExecEngineConfig,
    LoggingConfig,
    TradingNodeConfig,
)
from nautilus_trader.model.identifiers import TraderId, Venue


def create_config() -> TradingNodeConfig:
    """Create the trading node configuration."""
    # Load .env file from workspace root
    workspace_root = Path(__file__).parent.parent.parent.parent
    env_path = workspace_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    # Get environment variables
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_SECRET_KEY")
    
    if not api_key or not api_secret:
        raise ValueError("BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_SECRET_KEY must be set in environment")
    
    # Create the configuration
    return TradingNodeConfig(
        trader_id=TraderId("TESTER-001"),
        logging=LoggingConfig(
            log_level="INFO",
            log_level_file="DEBUG",  # File'da daha detaylı loglar
            log_colors=True,
            use_pyo3=True,
            log_file_format="json",  # JSON format için daha kolay parsing
            log_directory="/workspace/logs",
            log_file_name="nautilus_bot",  # Custom dosya adı
            log_file_max_size=50_000_000,  # 50MB rotation
            log_file_max_backup_count=10,  # 10 backup dosya tut
            clear_log_file=False,  # Başlangıçta dosyayı silme
            log_component_levels={
                "Portfolio": "INFO",
                "DataEngine": "INFO", 
                "RiskEngine": "WARNING",
                "ExecEngine": "INFO",
                "TestStrategy": "DEBUG",  # Strategy loglarını detaylı
            },
        ),
        exec_engine=LiveExecEngineConfig(
            reconciliation=True,
            reconciliation_lookback_mins=1440,
            filter_position_reports=True,
        ),
        cache=CacheConfig(
            timestamps_as_iso8601=True,
            flush_on_start=False,
        ),
        data_clients={
            "BINANCE": BinanceDataClientConfig(
                venue=Venue("BINANCE"),
                api_key=api_key,  # Explicitly set API key
                api_secret=api_secret,  # Explicitly set API secret
                account_type=BinanceAccountType.SPOT,
                base_url_http=None,  # Override with custom endpoint if needed
                base_url_ws=None,    # Override with custom endpoint if needed
                us=False,
                testnet=True,  # Enable testnet mode
                instrument_provider=InstrumentProviderConfig(load_all=True),
            ),
        },
        exec_clients={
            "BINANCE": SandboxExecutionClientConfig(
                venue="BINANCE",
                account_type="CASH",
                starting_balances=["1000 USDT", "0.01 BTC"],
            ),
        },
        timeout_connection=30.0,
        timeout_reconciliation=10.0,
        timeout_portfolio=10.0,
        timeout_disconnection=10.0,
        timeout_post_stop=5.0,
    )
