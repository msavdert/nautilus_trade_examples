"""
Base strategy interface and simple example strategies
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

from .client import BinanceClient
from .config import Config


@dataclass
class MarketData:
    """Market data container"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    additional_data: Optional[Dict[str, Any]] = None


@dataclass
class Position:
    """Position container"""
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float
    timestamp: datetime


class BaseStrategy(ABC):
    """Base strategy interface"""
    
    def __init__(self, config: Config, client: BinanceClient):
        self.config = config
        self.client = client
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.positions: Dict[str, Position] = {}
        self.is_running = False
        
    @abstractmethod
    async def on_market_data(self, data: MarketData):
        """Handle incoming market data"""
        pass
    
    @abstractmethod
    async def on_order_update(self, order_data: Dict[str, Any]):
        """Handle order status updates"""
        pass
    
    async def start(self):
        """Start the strategy"""
        self.is_running = True
        self.logger.info(f"Starting strategy: {self.__class__.__name__}")
        
    async def stop(self):
        """Stop the strategy"""
        self.is_running = False
        self.logger.info(f"Stopping strategy: {self.__class__.__name__}")
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """Place an order through the client"""
        try:
            if not self.should_place_order(symbol, side, quantity):
                self.logger.warning(f"Order blocked by risk management: {symbol} {side} {quantity}")
                return None
                
            order = await self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
            
            self.logger.info(f"Order placed: {order}")
            return order
            
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
    
    def should_place_order(self, symbol: str, side: str, quantity: float) -> bool:
        """Basic risk management check"""
        # Implement basic position size checks
        max_position = self.config.max_position_size_percent / 100.0
        
        # Add your risk management logic here
        # For now, always allow orders (in testnet)
        return True
    
    def calculate_position_size(self, symbol: str, price: float) -> float:
        """Calculate appropriate position size"""
        # Simple position sizing based on config
        # In a real implementation, this would consider account balance
        return 0.001  # Minimal BTC amount for testing


class SimpleBuyHoldStrategy(BaseStrategy):
    """
    Simple buy and hold strategy for demonstration
    Buys on price drops and holds
    """
    
    def __init__(self, config: Config, client: BinanceClient):
        super().__init__(config, client)
        self.last_prices: Dict[str, float] = {}
        self.buy_threshold = -0.02  # Buy on 2% drop
        self.position_size = 0.001  # Small test position
        
    async def on_market_data(self, data: MarketData):
        """Handle ticker data and make trading decisions"""
        if not self.is_running:
            return
            
        symbol = data.symbol
        current_price = data.price
        
        # Store price history
        if symbol not in self.last_prices:
            self.last_prices[symbol] = current_price
            return
        
        last_price = self.last_prices[symbol]
        price_change = (current_price - last_price) / last_price
        
        self.logger.debug(f"{symbol}: {current_price:.8f} ({price_change:.2%})")
        
        # Simple buy logic: buy on significant price drop
        if price_change <= self.buy_threshold and symbol not in self.positions:
            await self._try_buy(symbol, current_price)
        
        # Update last price
        self.last_prices[symbol] = current_price
    
    async def _try_buy(self, symbol: str, price: float):
        """Attempt to buy the symbol"""
        if not self.config.strategy_enabled:
            self.logger.info(f"Strategy disabled - would buy {symbol} at {price}")
            return
            
        try:
            quantity = self.calculate_position_size(symbol, price)
            order = await self.place_order(
                symbol=symbol,
                side="BUY",
                quantity=quantity,
                order_type="MARKET"
            )
            
            if order:
                # Create position record
                position = Position(
                    symbol=symbol,
                    side="BUY",
                    quantity=quantity,
                    entry_price=price,
                    current_price=price,
                    unrealized_pnl=0.0,
                    timestamp=datetime.now()
                )
                self.positions[symbol] = position
                self.logger.info(f"Bought {quantity} {symbol} at {price}")
                
        except Exception as e:
            self.logger.error(f"Failed to buy {symbol}: {e}")
    
    async def on_order_update(self, order_data: Dict[str, Any]):
        """Handle order status updates"""
        self.logger.info(f"Order update: {order_data}")


class ScalpingStrategy(BaseStrategy):
    """
    Simple scalping strategy for demonstration
    NOT RECOMMENDED FOR PRODUCTION USE
    """
    
    def __init__(self, config: Config, client: BinanceClient):
        super().__init__(config, client)
        self.price_history: Dict[str, List[float]] = {}
        self.window_size = 10
        self.scalp_threshold = 0.001  # 0.1% price movement
        
    async def on_market_data(self, data: MarketData):
        """Handle market data for scalping"""
        if not self.is_running:
            return
            
        symbol = data.symbol
        price = data.price
        
        # Maintain price history
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        
        # Keep only recent prices
        if len(self.price_history[symbol]) > self.window_size:
            self.price_history[symbol].pop(0)
        
        # Need enough history for analysis
        if len(self.price_history[symbol]) < self.window_size:
            return
        
        # Simple scalping logic (for demonstration only)
        await self._check_scalping_opportunity(symbol, price)
    
    async def _check_scalping_opportunity(self, symbol: str, current_price: float):
        """Check for scalping opportunities"""
        prices = self.price_history[symbol]
        avg_price = sum(prices) / len(prices)
        
        deviation = (current_price - avg_price) / avg_price
        
        # This is a very basic example - real scalping requires much more sophistication
        if abs(deviation) > self.scalp_threshold:
            self.logger.info(f"Scalping opportunity detected for {symbol}: {deviation:.4f}")
            # In a real strategy, you would implement more sophisticated logic here
    
    async def on_order_update(self, order_data: Dict[str, Any]):
        """Handle order updates for scalping"""
        # Implement order management logic
        pass


def create_strategy(strategy_name: str, config: Config, client: BinanceClient) -> BaseStrategy:
    """Strategy factory function"""
    strategies = {
        "simple_buy_hold": SimpleBuyHoldStrategy,
        "scalping": ScalpingStrategy,
    }
    
    if strategy_name not in strategies:
        raise ValueError(f"Unknown strategy: {strategy_name}. Available: {list(strategies.keys())}")
    
    return strategies[strategy_name](config, client)
