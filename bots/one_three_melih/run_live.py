#!/usr/bin/env python3
"""
Live trading runner for One-Three-Melih Trading Bot
===================================================

This module provides live trading capabilities with real market data.
Currently configured for demo/simulation mode until proper broker integration.

IMPORTANT: This is a template for live trading. Proper broker integration
and risk management systems must be implemented before using with real money.
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal

from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import TradingNodeConfig, LoggingConfig
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.objects import Money

from one_three_melih_strategy import OneThreeMelihStrategy, OneThreeMelihConfig


class LiveTradingRunner:
    """
    Live trading runner for the One-Three-Melih strategy.
    
    WARNING: This is a template implementation. Proper broker integration,
    risk management, and safety checks must be implemented before live trading.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.setup_logging()
        self.node: Optional[TradingNode] = None
        self.is_running = False
        self.config_file = config_file
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self) -> None:
        """Setup logging for live trading."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'live_trading_{datetime.now().strftime("%Y%m%d")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.logger.info(f"Received signal {signum}. Initiating graceful shutdown...")
        self.is_running = False
    
    async def run_live_trading(
        self,
        initial_balance: float = 100.0,
        profit_percentage: float = 30.0,
        demo_mode: bool = True
    ) -> None:
        """
        Run live trading with real or simulated market data.
        
        Args:
            initial_balance: Starting balance
            profit_percentage: Profit target percentage
            demo_mode: Whether to use demo/simulation mode
        """
        if not demo_mode:
            # Safety check for live trading
            confirmation = input(
                "⚠️  WARNING: You are about to start LIVE trading with real money!\n"
                "This bot is for educational purposes and may result in significant losses.\n"
                "Are you absolutely sure you want to continue? (type 'CONFIRM' to proceed): "
            )
            
            if confirmation != "CONFIRM":
                self.logger.info("Live trading cancelled by user.")
                return
        
        self.logger.info("=== STARTING LIVE TRADING ===")
        self.logger.info(f"Mode: {'DEMO' if demo_mode else 'LIVE'}")
        self.logger.info(f"Initial Balance: ${initial_balance}")
        self.logger.info(f"Profit Target: {profit_percentage}%")
        
        try:
            # Create trading node configuration
            config = self.create_trading_config(initial_balance, demo_mode)
            
            # Create trading node
            self.node = TradingNode(config)
            
            # Add strategy
            strategy_config = OneThreeMelihConfig(
                initial_balance=Decimal(str(initial_balance)),
                profit_target_percentage=Decimal(str(profit_percentage)),
            )
            strategy = OneThreeMelihStrategy(strategy_config)
            self.node.trader.add_strategy(strategy)
            
            # Start trading
            self.is_running = True
            await self.node.start_async()
            
            self.logger.info("Live trading started successfully!")
            self.logger.info("Press Ctrl+C to stop trading...")
            
            # Keep running until stopped
            while self.is_running:
                await asyncio.sleep(1)
            
        except Exception as e:
            self.logger.error(f"Error in live trading: {e}")
            raise
        
        finally:
            await self.cleanup()
    
    def create_trading_config(self, initial_balance: float, demo_mode: bool) -> TradingNodeConfig:
        """
        Create trading node configuration.
        
        Args:
            initial_balance: Starting balance
            demo_mode: Whether to use demo mode
            
        Returns:
            TradingNodeConfig instance
        """
        # This is a template configuration
        # Real implementation would require proper broker configuration
        
        config = TradingNodeConfig(
            trader_id=TraderId("LIVE-TRADER-001"),
            logging=LoggingConfig(
                log_level="INFO",
                log_file_format="%Y-%m-%d",
                log_component_level={
                    "Portfolio": "DEBUG",
                    "OrderManager": "DEBUG",
                    "RiskManager": "DEBUG",
                }
            ),
            # Note: Real broker configuration would go here
            # For now, this is a placeholder
        )
        
        return config
    
    async def cleanup(self) -> None:
        """Cleanup resources and stop trading."""
        self.logger.info("Cleaning up and stopping trading...")
        
        if self.node:
            try:
                await self.node.stop_async()
                self.logger.info("Trading node stopped successfully")
            except Exception as e:
                self.logger.error(f"Error stopping trading node: {e}")
        
        self.logger.info("Cleanup completed")
    
    def print_live_trading_disclaimer(self) -> None:
        """Print important disclaimer for live trading."""
        print("\n" + "="*80)
        print("IMPORTANT LIVE TRADING DISCLAIMER")
        print("="*80)
        print("⚠️  This trading bot is provided for educational purposes only!")
        print("⚠️  Trading involves substantial risk of loss!")
        print("⚠️  You could lose all of your invested capital!")
        print("")
        print("Before live trading, ensure you have:")
        print("✓ Thoroughly tested the strategy")
        print("✓ Understood the risks involved")
        print("✓ Configured proper risk management")
        print("✓ Set up proper broker integration")
        print("✓ Implemented safety checks and monitoring")
        print("✓ Only allocated money you can afford to lose")
        print("")
        print("The authors are not responsible for any losses incurred.")
        print("="*80 + "\n")


async def main():
    """Main entry point for live trading."""
    import argparse
    
    parser = argparse.ArgumentParser(description="One-Three-Melih Live Trading")
    parser.add_argument("--initial-balance", type=float, default=100.0,
                       help="Initial balance in USD")
    parser.add_argument("--profit-percentage", type=float, default=30.0,
                       help="Profit target percentage")
    parser.add_argument("--demo", action="store_true", default=True,
                       help="Run in demo mode (default)")
    parser.add_argument("--live", action="store_true",
                       help="Run in live trading mode (DANGEROUS)")
    parser.add_argument("--config", type=str,
                       help="Configuration file path")
    
    args = parser.parse_args()
    
    # Determine mode
    demo_mode = not args.live
    
    runner = LiveTradingRunner(args.config)
    
    # Show disclaimer
    runner.print_live_trading_disclaimer()
    
    if not demo_mode:
        print("LIVE TRADING MODE SELECTED!")
        print("This will use real money and real markets!")
        confirmation = input("Are you sure you want to continue? (yes/no): ")
        if confirmation.lower() != "yes":
            print("Live trading cancelled.")
            return
    
    try:
        await runner.run_live_trading(
            initial_balance=args.initial_balance,
            profit_percentage=args.profit_percentage,
            demo_mode=demo_mode
        )
    except KeyboardInterrupt:
        print("\nTrading stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Print warning for live trading
    print("⚠️  LIVE TRADING MODULE - USE WITH EXTREME CAUTION ⚠️")
    print("This module is a template and requires proper broker integration")
    print("before it can be used for actual live trading.\n")
    
    asyncio.run(main())
