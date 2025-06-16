"""
Main application entry point for Binance Spot Trading Client
"""
import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Any

from config import Config, get_config
from client import BinanceClient
from strategy import create_strategy, MarketData


# Configure logging
def setup_logging(config: Config):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/trading_client.log')
        ]
    )


class TradingApplication:
    """Main trading application"""
    
    def __init__(self):
        self.config = get_config()
        self.client: BinanceClient = None
        self.strategy = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def start(self):
        """Start the trading application"""
        self.logger.info("Starting Binance Spot Trading Client")
        self.logger.info(f"Environment: {self.config.environment}")
        self.logger.info(f"Testnet: {self.config.testnet}")
        
        try:
            # Initialize client
            self.client = BinanceClient(self.config)
            await self.client.start()
            
            # Test connection
            await self._test_connection()
            
            # Initialize strategy if enabled
            if self.config.strategy_enabled:
                self.strategy = create_strategy(
                    self.config.strategy_name,
                    self.config,
                    self.client
                )
                await self.strategy.start()
            
            # Start market data subscription
            await self._start_market_data()
            
            # Main application loop
            await self._run_main_loop()
            
        except Exception as e:
            self.logger.error(f"Error in main application: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _test_connection(self):
        """Test Binance API connection"""
        try:
            server_time = await self.client.get_server_time()
            self.logger.info(f"Connected to Binance API. Server time: {server_time}")
            
            # Test account access if not in demo mode
            if self.config.testnet:
                account_info = await self.client.get_account_info()
                self.logger.info(f"Account type: {account_info.get('accountType', 'unknown')}")
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            raise
    
    async def _start_market_data(self):
        """Start market data subscriptions"""
        symbols = self.config.symbols_list
        self.logger.info(f"Subscribing to market data for: {symbols}")
        
        # Subscribe to ticker data
        asyncio.create_task(
            self.client.subscribe_ticker(symbols, self._handle_ticker_data)
        )
        
        # Subscribe to kline data for the first interval
        if self.config.intervals_list:
            interval = self.config.intervals_list[0]
            asyncio.create_task(
                self.client.subscribe_klines(symbols, interval, self._handle_kline_data)
            )
    
    async def _handle_ticker_data(self, data: Dict[str, Any]):
        """Handle incoming ticker data"""
        try:
            # Extract ticker information
            symbol = data.get('s')
            price = float(data.get('c', 0))
            volume = float(data.get('v', 0))
            
            if symbol and price > 0:
                market_data = MarketData(
                    symbol=symbol,
                    price=price,
                    volume=volume,
                    timestamp=datetime.now(),
                    additional_data=data
                )
                
                # Log market data (debug level to avoid spam)
                self.logger.debug(f"Ticker: {symbol} = {price:.8f}")
                
                # Send to strategy if enabled
                if self.strategy:
                    await self.strategy.on_market_data(market_data)
                    
        except Exception as e:
            self.logger.error(f"Error handling ticker data: {e}")
    
    async def _handle_kline_data(self, data: Dict[str, Any]):
        """Handle incoming kline/candlestick data"""
        try:
            kline = data.get('k', {})
            if kline.get('x'):  # Only process closed klines
                symbol = kline.get('s')
                close_price = float(kline.get('c', 0))
                volume = float(kline.get('v', 0))
                
                self.logger.debug(f"Kline closed: {symbol} = {close_price:.8f}")
                
                # You can add kline-specific strategy logic here
                
        except Exception as e:
            self.logger.error(f"Error handling kline data: {e}")
    
    async def _run_main_loop(self):
        """Main application loop"""
        self.running = True
        self.logger.info("Trading client is running...")
        
        while self.running:
            try:
                # Heartbeat and status logging
                await asyncio.sleep(60)  # 1-minute intervals
                self.logger.info("Trading client heartbeat")
                
                # Log strategy status if enabled
                if self.strategy and hasattr(self.strategy, 'positions'):
                    position_count = len(self.strategy.positions)
                    self.logger.info(f"Active positions: {position_count}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Brief pause before retrying
    
    async def _cleanup(self):
        """Cleanup resources"""
        self.logger.info("Cleaning up...")
        
        if self.strategy:
            await self.strategy.stop()
        
        if self.client:
            await self.client.stop()
        
        self.logger.info("Cleanup completed")


async def main():
    """Main entry point"""
    # Setup configuration and logging
    config = get_config()
    setup_logging(config)
    
    # Create and run application
    app = TradingApplication()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)
