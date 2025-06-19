#!/usr/bin/env python3
"""
Live Trading Runner for One-Three Risk Management Bot
===================================================

This script sets up and runs the One-Three trading bot in live trading mode.
It demonstrates how to:

1. Configure live trading environment
2. Connect to data feeds and execution venues
3. Implement proper risk management in live conditions
4. Monitor and log real-time trading activity
5. Handle connection issues and system recovery

⚠️ WARNING: This script is for educational purposes. Always test thoroughly
in a demo environment before using real capital.
"""

import asyncio
from decimal import Decimal
import signal
import sys
from typing import Optional

from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import TradingNodeConfig, LoggingConfig
from nautilus_trader.model.identifiers import TraderId

from one_three_strategy import OneThreeBot, OneThreeConfig


class LiveTradingManager:
    """
    Manages live trading operations for the One-Three bot.
    
    This class handles:
    - Trading node lifecycle
    - Connection management
    - Error handling and recovery
    - Safe shutdown procedures
    """
    
    def __init__(self):
        self.node: Optional[TradingNode] = None
        self.is_running = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n⚠️ Received signal {signum}. Initiating graceful shutdown...")
        self.is_running = False
        
        if self.node:
            asyncio.create_task(self.shutdown())
            
    async def create_trading_config(self) -> TradingNodeConfig:
        """
        Create configuration for live trading.
        
        Returns:
            TradingNodeConfig: Complete configuration for live trading
        """
        return TradingNodeConfig(
            trader_id=TraderId("ONE_THREE_LIVE"),
            
            # Logging configuration
            logging=LoggingConfig(
                log_level="INFO",
                log_level_file="DEBUG", 
                log_directory="logs",
                log_file_name="one_three_live.log",
                log_colors=True,
                bypass_logging=False,
            ),
            
            # Message bus and cache settings
            cache_database=None,  # Use Redis for production
            streaming=True,
            
            # Performance settings
            time_bars_build_with_ticks=True,
            time_bars_timestamp_on_close=True,
            
            # Risk management
            max_order_submit_rate="100/00:00:01",  # Max 100 orders per second
            max_order_modify_rate="100/00:00:01",
            
            # Data settings
            catalog=None,  # Use live data feeds
            
            # System settings
            snapshot_orders=True,
            snapshot_positions=True,
            save_state=True,
        )
        
    def create_strategy_config(self) -> OneThreeConfig:
        """
        Create strategy configuration for live trading.
        
        Returns:
            OneThreeConfig: Strategy configuration optimized for live trading
        """
        return OneThreeConfig(
            # Core settings
            instrument_id="EUR/USD.SIM",  # Change to your broker's symbol
            trade_size=Decimal("10_000"),  # Smaller size for live trading
            
            # Risk management (conservative for live trading)
            take_profit_pips=1.3,
            stop_loss_pips=1.3,
            
            # Trading limits
            max_daily_trades=10,  # Conservative limit for live trading
            entry_delay_seconds=300,  # 5 minutes between trades
            
            # Market timing
            enable_time_filter=True,
            trading_start_hour=8,   # 8 AM UTC
            trading_end_hour=18,    # 6 PM UTC (avoid overnight risk)
            
            # Advanced features for live trading
            enable_trailing_stop=False,  # Disable for simplicity
            use_tick_data=True,
            slippage_tolerance=0.5,  # 0.5 pips max slippage
        )
        
    async def setup_data_clients(self, config: TradingNodeConfig):
        """
        Configure data feed connections.
        
        ⚠️ You need to configure your actual data provider here.
        This example shows the structure but uses simulation.
        
        Args:
            config: Trading node configuration
        """
        print("📡 Setting up data connections...")
        
        # Example: Configure your data provider
        # For production, you would configure real data feeds like:
        # - Interactive Brokers
        # - OANDA
        # - MetaTrader
        # - Your broker's API
        
        # Example configuration (you need to replace with actual provider):
        """
        data_config = {
            "provider": "YOUR_DATA_PROVIDER",
            "api_key": "YOUR_API_KEY",
            "username": "YOUR_USERNAME", 
            "password": "YOUR_PASSWORD",
            "base_url": "wss://your-provider.com/stream",
            "instruments": ["EUR/USD"],
        }
        
        # Add data client to config
        config.data_clients = {
            "YOUR_PROVIDER": data_config
        }
        """
        
        print("⚠️ WARNING: Using simulated data - configure real data provider for live trading")
        
    async def setup_execution_clients(self, config: TradingNodeConfig):
        """
        Configure execution venue connections.
        
        ⚠️ You need to configure your actual broker here.
        This example shows the structure but uses simulation.
        
        Args:
            config: Trading node configuration
        """
        print("🔗 Setting up execution connections...")
        
        # Example: Configure your broker/execution venue
        # For production, you would configure real brokers like:
        # - Interactive Brokers
        # - OANDA 
        # - Your preferred forex broker
        
        # Example configuration (you need to replace with actual broker):
        """
        exec_config = {
            "provider": "YOUR_BROKER", 
            "account_id": "YOUR_ACCOUNT_ID",
            "api_key": "YOUR_API_KEY",
            "secret_key": "YOUR_SECRET_KEY",
            "base_url": "https://your-broker.com/api",
            "sandbox": False,  # Set to True for demo trading
        }
        
        # Add execution client to config
        config.exec_clients = {
            "YOUR_BROKER": exec_config
        }
        """
        
        print("⚠️ WARNING: Using simulated execution - configure real broker for live trading")
        
    async def initialize_node(self) -> TradingNode:
        """
        Initialize the trading node with full configuration.
        
        Returns:
            TradingNode: Fully configured trading node
        """
        print("🚀 Initializing live trading node...")
        
        # Create configuration
        config = await self.create_trading_config()
        
        # Setup connections
        await self.setup_data_clients(config)
        await self.setup_execution_clients(config)
        
        # Create trading node
        node = TradingNode(config=config)
        
        # Create and add strategy
        strategy_config = self.create_strategy_config()
        strategy = OneThreeBot(config=strategy_config)
        node.trader.add_strategy(strategy)
        
        print("✅ Trading node initialized")
        print(f"   • Strategy: One-Three Risk Management")
        print(f"   • Instrument: {strategy_config.instrument_id}")
        print(f"   • Trade Size: {strategy_config.trade_size:,} units")
        print(f"   • Risk Management: ±{strategy_config.take_profit_pips} pips")
        print(f"   • Daily Limit: {strategy_config.max_daily_trades} trades")
        
        return node
        
    async def start_trading(self):
        """
        Start live trading operations.
        
        This method:
        1. Initializes the trading node
        2. Starts all connections
        3. Begins strategy execution
        4. Monitors for shutdown signals
        """
        try:
            print("🎯 Starting One-Three Live Trading Bot")
            print("="*50)
            
            # Initialize trading node
            self.node = await self.initialize_node()
            
            # Start the node
            await self.node.start()
            self.is_running = True
            
            print(f"\n✅ Live trading started successfully!")
            print(f"🔄 Bot is now running...")
            print(f"📊 Monitor logs in: logs/one_three_live.log")
            print(f"⚠️ Press Ctrl+C to stop trading safely")
            
            # Keep running until shutdown signal
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Error starting live trading: {e}")
            raise
        finally:
            await self.shutdown()
            
    async def shutdown(self):
        """
        Gracefully shutdown live trading operations.
        
        This method:
        1. Stops accepting new trades
        2. Closes open positions (if configured)
        3. Disconnects from all venues
        4. Saves state and logs
        """
        if not self.node:
            return
            
        print(f"\n🛑 Shutting down live trading...")
        
        try:
            # Stop the trading node
            await self.node.stop()
            
            print(f"✅ Live trading stopped safely")
            print(f"📊 Final state saved to logs")
            
        except Exception as e:
            print(f"⚠️ Error during shutdown: {e}")
        finally:
            self.node = None
            self.is_running = False


def check_prerequisites():
    """
    Check that all prerequisites are met for live trading.
    
    Returns:
        bool: True if all prerequisites are met
    """
    print("🔍 Checking prerequisites for live trading...")
    
    prerequisites = [
        "✅ Python 3.11+ installed",
        "✅ Nautilus Trader installed", 
        "⚠️ Data provider configured (REQUIRED for live trading)",
        "⚠️ Broker/execution venue configured (REQUIRED for live trading)",
        "⚠️ API credentials configured (REQUIRED for live trading)",
        "⚠️ Demo account tested (HIGHLY RECOMMENDED)",
        "⚠️ Risk limits configured (REQUIRED for live trading)",
    ]
    
    for req in prerequisites:
        print(f"   {req}")
        
    print(f"\n⚠️ IMPORTANT NOTICES:")
    print(f"   • This example uses simulated data/execution")
    print(f"   • You MUST configure real data and execution providers")
    print(f"   • Test thoroughly in demo mode before live trading")
    print(f"   • Never risk more than you can afford to lose")
    print(f"   • Monitor positions and system health continuously")
    
    return False  # Return False since this is just an example


async def main():
    """
    Main entry point for live trading.
    """
    try:
        # Check prerequisites
        if not check_prerequisites():
            print(f"\n❌ Prerequisites not met.")
            print(f"📚 Please configure your data provider and execution venue.")
            print(f"🔧 See README files for detailed setup instructions.")
            return
            
        # Get user confirmation
        print(f"\n⚠️ You are about to start LIVE TRADING.")
        print(f"📋 Please review the configuration above carefully.")
        
        response = input(f"\nType 'START' to begin live trading (or anything else to exit): ")
        
        if response.upper() != 'START':
            print(f"🚫 Live trading cancelled by user")
            return
            
        # Start live trading
        manager = LiveTradingManager()
        await manager.start_trading()
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Live trading interrupted by user")
    except Exception as e:
        print(f"\n❌ Live trading failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"\n👋 Live trading session ended")


if __name__ == "__main__":
    # Display warning banner
    print("⚠️" * 20)
    print("⚠️  LIVE TRADING WARNING  ⚠️")
    print("⚠️" * 20)
    print()
    print("This script connects to LIVE markets and can place REAL trades.")
    print("Ensure you have:")
    print("• Configured your broker/data provider correctly")
    print("• Tested thoroughly in demo mode")
    print("• Set appropriate risk limits")
    print("• Understand the strategy completely")
    print()
    print("NEVER risk more than you can afford to lose!")
    print()
    
    # Run the live trading system
    asyncio.run(main())
