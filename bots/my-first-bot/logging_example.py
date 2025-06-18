# logging_example.py - Complete Logging Configuration Example for My First Bot

"""
This example demonstrates best-practice logging configuration for Nautilus Trader.
It shows how to set up comprehensive logging for both development and production use.
"""

import os
from pathlib import Path
from nautilus_trader.config import LoggingConfig, TradingNodeConfig
from nautilus_trader.live.node import TradingNode

# Import our bot
from main import MyFirstBot, MyFirstBotConfig


def create_logging_config(environment: str = "development") -> LoggingConfig:
    """
    Create a logging configuration based on the environment.
    
    Args:
        environment: Either "development" or "production"
    
    Returns:
        LoggingConfig: Configured logging setup
    """
    
    # Determine log directory - use logs/ under the bot directory
    bot_dir = Path(__file__).parent
    log_dir = bot_dir / "logs"
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True)
    
    if environment == "development":
        return LoggingConfig(
            # Console logging
            log_level="DEBUG",              # Show everything in console during development
            log_colors=True,               # Pretty colors for terminal output
            
            # File logging
            log_level_file="DEBUG",        # Log everything to file for debugging
            log_directory=str(log_dir),    # Store logs under bot/logs/
            log_file_format="json",        # JSON format for better parsing
            
            # Log rotation
            log_file_max_size=10,          # 10MB max file size
            log_file_max_backup_count=5,   # Keep 5 backup files
            
            # Component filtering (optional - uncomment to filter)
            # log_component_levels={
            #     "Portfolio": "INFO",       # Less verbose portfolio logging
            #     "OrderEmulator": "WARN",   # Only warnings from order emulator
            # },
            
            # Performance settings
            use_pyo3=True,                 # Include Rust component logs (slower but complete)
        )
    
    else:  # production
        return LoggingConfig(
            # Console logging - minimal in production
            log_level="INFO",              # Only important info in console
            log_colors=False,              # No colors in production logs
            
            # File logging - comprehensive
            log_level_file="INFO",         # INFO level for production files
            log_directory=str(log_dir),    # Store logs under bot/logs/
            log_file_format="json",        # JSON for log analysis tools
            
            # Log rotation - more aggressive in production
            log_file_max_size=50,          # 50MB max file size
            log_file_max_backup_count=10,  # Keep 10 backup files
            
            # Component filtering for production
            log_component_levels={
                "DataEngine": "INFO",       # Reduce data engine verbosity
                "RiskEngine": "INFO",       # Keep risk engine info
                "ExecutionEngine": "INFO",  # Keep execution engine info
                "Portfolio": "WARN",        # Only warnings from portfolio
            },
            
            # Performance settings for production
            use_pyo3=False,                # Disable Rust logs for performance
        )


def create_bot_config() -> MyFirstBotConfig:
    """Create configuration for our first bot."""
    return MyFirstBotConfig(
        instrument_id="EUR/USD.SIM",
        trade_size=100_000,
        ma_period=10,
    )


def main():
    """
    Main function to run our bot with proper logging configuration.
    """
    print("🤖 My First Bot with Comprehensive Logging")
    print("=" * 50)
    
    # Determine environment from environment variable
    environment = os.getenv("TRADING_ENV", "development")
    print(f"Environment: {environment}")
    
    # Create logging configuration
    logging_config = create_logging_config(environment)
    print(f"Log directory: {logging_config.log_directory}")
    print(f"Log level (console): {logging_config.log_level}")
    print(f"Log level (file): {logging_config.log_level_file}")
    
    # Create bot configuration
    bot_config = create_bot_config()
    
    # Create trading node configuration
    node_config = TradingNodeConfig(
        trader_id="MY-FIRST-BOT-001",
        logging=logging_config,
        # Add other configurations as needed
    )
    
    try:
        # Create and start the trading node
        print("\n🚀 Starting trading node...")
        
        # Note: This is a demonstration of configuration.
        # For actual backtesting or live trading, you would need:
        # 1. Data configuration (for backtesting)
        # 2. Venue configuration (for live trading)
        # 3. Strategy configuration
        
        print("✅ Logging configuration created successfully!")
        print("\nNext steps:")
        print("1. Add data configuration for backtesting")
        print("2. Add venue configuration for live trading")
        print("3. Add strategy to the node configuration")
        print("4. Run the complete trading node")
        
        # Log some example messages to demonstrate logging
        # (This would normally be done by the actual trading node)
        print(f"\nExample log files will be created in: {logging_config.log_directory}")
        
    except Exception as e:
        print(f"❌ Error starting trading node: {e}")
        print("Check the logs for more details.")


if __name__ == "__main__":
    main()
