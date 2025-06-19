#!/usr/bin/env python3
"""
Binance Testnet Automated Trading Bot
Main entry point for the trading bot with multiple operation modes.
"""

import asyncio
import logging
import argparse
import signal
import sys
from typing import Optional, List
from datetime import datetime

from nautilus_trader.adapters.binance import BINANCE, BinanceAccountType
from nautilus_trader.adapters.binance import BinanceLiveDataClientFactory, BinanceLiveExecClientFactory
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.data import BarType
from nautilus_trader.model.identifiers import InstrumentId, TraderId

from config import get_config, get_nautilus_config
from strategy import VolatilityBreakoutStrategy, VolatilityBreakoutConfig
from coin_selector import CoinSelector
from risk_manager import RiskManager
from utils import LoggingUtils


class TradingBot:
    """
    Main trading bot class that orchestrates all components.
    
    Features:
    - Multi-mode operation (demo, live, backtest)
    - Top 50 volume coin selection
    - Real-time strategy execution
    - Comprehensive risk management
    - Emergency stop mechanisms
    """
    
    def __init__(self, mode: str = "demo"):
        """
        Initialize trading bot.
        
        Args:
            mode: Operation mode ('demo', 'live', 'backtest')
        """
        self.mode = mode
        self.config = get_config()
        self.logger = LoggingUtils.setup_logger(
            "TradingBot", 
            self.config.logging.level,
            "binance_testnet_bot.log" if self.config.logging.log_to_file else None
        )
        
        # Core components
        self.node: Optional[TradingNode] = None
        self.coin_selector = None
        self.risk_manager = RiskManager()
        
        # Selected trading instruments
        self.selected_coins: List[str] = []
        self.instrument_ids: List[InstrumentId] = []
        
        # Bot state
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"Trading bot initialized in {mode} mode")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating shutdown...")
        self.shutdown_event.set()
    
    async def initialize(self) -> bool:
        """
        Initialize bot components.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info("Initializing trading bot components...")
            
            # Initialize coin selector
            self.coin_selector = CoinSelector()
            
            # Select top volume coins
            await self._select_trading_coins()
            
            if not self.selected_coins:
                self.logger.error("No coins selected for trading")
                return False
            
            # Setup Nautilus trading node
            await self._setup_trading_node()
            
            self.logger.info("Bot initialization completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during bot initialization: {e}")
            return False
    
    async def _select_trading_coins(self) -> None:
        """Select top volume coins for trading."""
        self.logger.info("Selecting top volume coins...")
        
        async with self.coin_selector:
            coins = await self.coin_selector.get_top_volume_coins()
            
            if not coins:
                self.logger.error("Failed to fetch coin data")
                return
            
            # Extract symbols and create instrument IDs
            self.selected_coins = [coin.symbol for coin in coins]
            
            # Create instrument IDs based on account type
            venue_suffix = ".BINANCE"
            if self.config.exchange.account_type == "USDT_FUTURE":
                # Add -PERP suffix for futures
                self.instrument_ids = [
                    InstrumentId.from_str(f"{symbol}-PERP{venue_suffix}")
                    for symbol in self.selected_coins
                ]
            else:
                self.instrument_ids = [
                    InstrumentId.from_str(f"{symbol}{venue_suffix}")
                    for symbol in self.selected_coins
                ]
            
            self.logger.info(f"Selected {len(self.selected_coins)} coins for trading:")
            for i, coin in enumerate(coins[:10], 1):  # Log top 10
                self.logger.info(
                    f"{i:2d}. {coin.symbol} - Volume: ${coin.volume_24h_usdt:,.0f}"
                )
    
    async def _setup_trading_node(self) -> None:
        """Setup Nautilus trading node."""
        self.logger.info("Setting up Nautilus trading node...")
        
        # Get Nautilus configuration
        nautilus_config_dict = get_nautilus_config()
        
        # Create trading node configuration
        config_node = TradingNodeConfig(**nautilus_config_dict)
        
        # Initialize trading node
        self.node = TradingNode(config=config_node)
        
        # Create strategy configuration
        strategy_config = VolatilityBreakoutConfig(
            instrument_ids=self.instrument_ids,
            bar_type=BarType.from_str(f"{self.selected_coins[0]}-PERP.BINANCE-1-MINUTE-LAST-EXTERNAL"),
            
            # Technical indicator parameters
            atr_period=self.config.strategy.atr_period,
            bollinger_period=self.config.strategy.bollinger_period,
            bollinger_std=self.config.strategy.bollinger_std,
            rsi_period=self.config.strategy.rsi_period,
            volume_period=self.config.strategy.volume_period,
            
            # Entry conditions
            volume_threshold_multiplier=self.config.strategy.volume_threshold_multiplier,
            rsi_min=self.config.strategy.rsi_min,
            rsi_max=self.config.strategy.rsi_max,
            volatility_threshold_atr=self.config.strategy.volatility_threshold_atr,
            
            # Exit conditions
            stop_loss_atr_multiplier=self.config.strategy.stop_loss_atr_multiplier,
            take_profit_atr_multiplier=self.config.strategy.take_profit_atr_multiplier,
            trailing_stop_atr_multiplier=self.config.strategy.trailing_stop_atr_multiplier,
            
            # Risk management
            max_risk_per_trade=self.config.trading.max_risk_per_trade_percent / 100,
            max_position_size=self.config.trading.max_position_size_percent / 100
        )
        
        # Create and add strategy
        strategy = VolatilityBreakoutStrategy(config=strategy_config)
        self.node.trader.add_strategy(strategy)
        
        # Register client factories
        self.node.add_data_client_factory(BINANCE, BinanceLiveDataClientFactory)
        self.node.add_exec_client_factory(BINANCE, BinanceLiveExecClientFactory)
        
        # Build the node
        self.node.build()
        
        self.logger.info("Trading node setup completed")
    
    async def run_demo_mode(self) -> None:
        """Run bot in demo mode (paper trading)."""
        self.logger.info("Starting demo mode (paper trading)...")
        
        try:
            # Start the trading node
            if self.node:
                await self._run_trading_node()
            else:
                self.logger.error("Trading node not initialized")
                
        except Exception as e:
            self.logger.error(f"Error in demo mode: {e}")
    
    async def run_live_mode(self) -> None:
        """Run bot in live trading mode."""
        self.logger.warning("LIVE TRADING MODE - Real money at risk!")
        self.logger.warning("Ensure you have reviewed all settings and risk parameters")
        
        # Additional confirmation for live mode
        if self.config.exchange.testnet:
            self.logger.info("Running on Binance Testnet (safe)")
        else:
            self.logger.critical("Running on LIVE Binance - REAL MONEY AT RISK!")
        
        try:
            # Start the trading node
            if self.node:
                await self._run_trading_node()
            else:
                self.logger.error("Trading node not initialized")
                
        except Exception as e:
            self.logger.error(f"Error in live mode: {e}")
    
    async def _run_trading_node(self) -> None:
        """Run the trading node with monitoring."""
        self.is_running = True
        
        try:
            # Start monitoring task
            monitor_task = asyncio.create_task(self._monitor_bot())
            
            # Start trading node
            if self.node:
                self.logger.info("Starting trading node...")
                
                # Run node in background
                node_task = asyncio.create_task(
                    asyncio.to_thread(self.node.run)
                )
                
                # Wait for shutdown signal or node completion
                done, pending = await asyncio.wait(
                    [node_task, monitor_task, 
                     asyncio.create_task(self.shutdown_event.wait())],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                
                # Stop trading node
                self.node.stop()
                
        except Exception as e:
            self.logger.error(f"Error running trading node: {e}")
        finally:
            self.is_running = False
            self.logger.info("Trading node stopped")
    
    async def _monitor_bot(self) -> None:
        """Monitor bot performance and health."""
        self.logger.info("Starting bot monitoring...")
        
        last_report_time = datetime.now()
        report_interval = 300  # 5 minutes
        
        while self.is_running and not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                # Check emergency conditions
                if self.node and self.node.trader:
                    account = None
                    for account in self.node.trader.cache.accounts():
                        break  # Get first account
                    
                    if account and self.risk_manager.check_emergency_conditions(account.balance()):
                        self.logger.critical("EMERGENCY CONDITIONS DETECTED - STOPPING BOT")
                        self.risk_manager.trigger_emergency_stop()
                        self.shutdown_event.set()
                        break
                
                # Periodic performance report
                current_time = datetime.now()
                if (current_time - last_report_time).total_seconds() >= report_interval:
                    await self._log_performance_report()
                    last_report_time = current_time
                
            except Exception as e:
                self.logger.error(f"Error in bot monitoring: {e}")
                await asyncio.sleep(60)  # Longer delay on error
    
    async def _log_performance_report(self) -> None:
        """Log periodic performance report."""
        try:
            risk_summary = self.risk_manager.get_risk_summary()
            
            self.logger.info("=== PERFORMANCE REPORT ===")
            self.logger.info(f"Active Positions: {risk_summary['active_positions']}")
            self.logger.info(f"Daily PnL: ${risk_summary['daily_pnl']:.2f}")
            self.logger.info(f"Max Drawdown: {risk_summary['max_drawdown']:.2f}%")
            self.logger.info(f"Daily Trades: {risk_summary['daily_trades']}")
            self.logger.info(f"Total Exposure: ${risk_summary['total_exposure']:.2f}")
            self.logger.info(f"Emergency Stop: {risk_summary['emergency_stop']}")
            
            # Update coin selection periodically
            if self.coin_selector:
                async with self.coin_selector:
                    await self.coin_selector.update_coin_list()
            
        except Exception as e:
            self.logger.error(f"Error generating performance report: {e}")
    
    async def shutdown(self) -> None:
        """Gracefully shutdown the bot."""
        self.logger.info("Initiating bot shutdown...")
        
        self.is_running = False
        
        try:
            # Stop trading node
            if self.node:
                self.node.stop()
                self.node.dispose()
            
            # Final performance report
            await self._log_performance_report()
            
            self.logger.info("Bot shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Binance Testnet Trading Bot")
    parser.add_argument(
        "--mode", 
        choices=["demo", "live", "backtest"],
        default="demo",
        help="Operation mode (default: demo)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger("main")
    
    try:
        # Create and initialize bot
        bot = TradingBot(mode=args.mode)
        
        if not await bot.initialize():
            logger.error("Bot initialization failed")
            return 1
        
        # Run bot based on mode
        if args.mode == "demo":
            await bot.run_demo_mode()
        elif args.mode == "live":
            await bot.run_live_mode()
        elif args.mode == "backtest":
            logger.error("Backtest mode not implemented in main.py - use run_backtest.py")
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    finally:
        if 'bot' in locals():
            await bot.shutdown()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nBot stopped by user")
        sys.exit(0)
