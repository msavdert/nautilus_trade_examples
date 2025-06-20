"""
Coin Selection Utility for Binance Futures Testnet

This module handles the selection of top trading pairs based on volume,
market capitalization, and other criteria. It interfaces with Binance
Futures Testnet API to get real-time market data.

Key Features:
- Fetches top 50 coins by 24h volume
- Filters out stablecoins and low-volume pairs
- Validates instruments are available for futures trading
- Provides instrument mapping for Nautilus framework
- Handles US region-specific requirements
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue


@dataclass
class CoinInfo:
    """Information about a trading pair."""
    symbol: str
    base_asset: str
    quote_asset: str
    volume_24h: float
    price: float
    price_change_24h: float
    is_futures_enabled: bool = False
    min_notional: float = 0.0
    tick_size: float = 0.0001
    step_size: float = 0.001


class CoinSelector:
    """
    Coin selection utility for Binance Futures Testnet.
    
    Selects the most suitable trading pairs based on:
    - 24h trading volume
    - Price volatility
    - Liquidity
    - Futures availability
    """
    
    def __init__(self, config_manager):
        """
        Initialize coin selector.
        
        Args:
            config_manager: Configuration manager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Binance Futures Testnet API endpoints
        self.base_url = self.config.endpoints.futures_api_url
        
        # Cache for coin data
        self._cache: Dict[str, CoinInfo] = {}
        self._cache_timestamp: Optional[datetime] = None
        self._cache_duration = timedelta(minutes=5)  # Cache for 5 minutes
        
        # Excluded coins (stablecoins, etc.)
        self.excluded_coins = set(self.config.trading.excluded_coins + [
            "USDCUSDT", "BUSDUSDT", "TUSDUSDT", "FDUSD", "USDC",
            "USDT", "BUSD", "TUSD", "DAI", "PAX", "GUSD"
        ])
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_futures_exchange_info(self) -> Dict:
        """
        Fetch exchange information from Binance Futures API.
        
        Returns:
            Exchange info dictionary
        """
        url = f"{self.base_url}/exchangeInfo"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch exchange info: {response.status}")
                
                data = await response.json()
                return data
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _fetch_24h_ticker_stats(self) -> List[Dict]:
        """
        Fetch 24h ticker statistics from Binance Futures API.
        
        Returns:
            List of ticker statistics
        """
        url = f"{self.base_url}/ticker/24hr"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch ticker stats: {response.status}")
                
                data = await response.json()
                return data
    
    def _is_valid_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid for trading.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            True if valid, False otherwise
        """
        # Must be USDT futures pair
        if not symbol.endswith("USDT"):
            return False
        
        # Extract base asset
        base_asset = symbol.replace("USDT", "")
        
        # Skip excluded coins
        if base_asset in self.excluded_coins or symbol in self.excluded_coins:
            return False
        
        # Skip leveraged tokens
        if any(suffix in base_asset for suffix in ["UP", "DOWN", "BULL", "BEAR"]):
            return False
        
        # Skip very short symbols (likely test coins)
        if len(base_asset) < 2:
            return False
        
        return True
    
    async def _fetch_coin_data(self) -> Dict[str, CoinInfo]:
        """
        Fetch comprehensive coin data from Binance Futures API.
        
        Returns:
            Dictionary mapping symbol to CoinInfo
        """
        self.logger.info("Fetching coin data from Binance Futures Testnet")
        
        try:
            # Fetch exchange info and ticker stats in parallel
            exchange_info_task = self._fetch_futures_exchange_info()
            ticker_stats_task = self._fetch_24h_ticker_stats()
            
            exchange_info, ticker_stats = await asyncio.gather(
                exchange_info_task, ticker_stats_task
            )
            
            # Create mapping of symbols to ticker data
            ticker_map = {item["symbol"]: item for item in ticker_stats}
            
            # Process exchange info to get trading rules
            coins = {}
            
            for symbol_info in exchange_info.get("symbols", []):
                symbol = symbol_info["symbol"]
                
                # Skip if not valid or not trading
                if not self._is_valid_symbol(symbol):
                    continue
                
                if symbol_info["status"] != "TRADING":
                    continue
                
                # Get ticker data
                ticker = ticker_map.get(symbol)
                if not ticker:
                    continue
                
                # Parse trading rules
                min_notional = 0.0
                tick_size = 0.0001
                step_size = 0.001
                
                for filter_info in symbol_info.get("filters", []):
                    if filter_info["filterType"] == "MIN_NOTIONAL":
                        min_notional = float(filter_info["notional"])
                    elif filter_info["filterType"] == "PRICE_FILTER":
                        tick_size = float(filter_info["tickSize"])
                    elif filter_info["filterType"] == "LOT_SIZE":
                        step_size = float(filter_info["stepSize"])
                
                # Create CoinInfo
                base_asset = symbol.replace("USDT", "")
                volume_24h = float(ticker["quoteVolume"])
                price = float(ticker["lastPrice"])
                price_change_24h = float(ticker["priceChangePercent"])
                
                coin_info = CoinInfo(
                    symbol=symbol,
                    base_asset=base_asset,
                    quote_asset="USDT",
                    volume_24h=volume_24h,
                    price=price,
                    price_change_24h=price_change_24h,
                    is_futures_enabled=True,
                    min_notional=min_notional,
                    tick_size=tick_size,
                    step_size=step_size
                )
                
                coins[symbol] = coin_info
            
            self.logger.info(f"Fetched data for {len(coins)} trading pairs")
            return coins
            
        except Exception as e:
            self.logger.error(f"Error fetching coin data: {e}")
            raise
    
    async def get_top_coins(self, 
                           count: int = 50,
                           min_volume_usd: float = 10_000_000,
                           force_refresh: bool = False) -> List[CoinInfo]:
        """
        Get top coins by trading volume.
        
        Args:
            count: Number of top coins to return
            min_volume_usd: Minimum 24h volume in USD
            force_refresh: Force refresh of cached data
            
        Returns:
            List of top CoinInfo objects
        """
        # Check cache
        now = datetime.utcnow()
        if (not force_refresh and 
            self._cache_timestamp and 
            now - self._cache_timestamp < self._cache_duration and
            self._cache):
            
            self.logger.info("Using cached coin data")
            coins = list(self._cache.values())
        else:
            # Fetch fresh data
            self._cache = await self._fetch_coin_data()
            self._cache_timestamp = now
            coins = list(self._cache.values())
        
        # Filter by minimum volume
        filtered_coins = [
            coin for coin in coins 
            if coin.volume_24h >= min_volume_usd
        ]
        
        # Sort by volume (descending)
        sorted_coins = sorted(
            filtered_coins, 
            key=lambda x: x.volume_24h, 
            reverse=True
        )
        
        # Return top N
        top_coins = sorted_coins[:count]
        
        self.logger.info(
            f"Selected {len(top_coins)} top coins "
            f"(min volume: ${min_volume_usd:,.0f})"
        )
        
        for i, coin in enumerate(top_coins[:10]):  # Log top 10
            self.logger.info(
                f"{i+1:2d}. {coin.symbol:<12} "
                f"Volume: ${coin.volume_24h:>12,.0f} "
                f"Price: ${coin.price:>8.4f} "
                f"Change: {coin.price_change_24h:>6.2f}%"
            )
        
        return top_coins
    
    def get_nautilus_instrument_ids(self, coins: List[CoinInfo]) -> List[InstrumentId]:
        """
        Convert coin symbols to Nautilus InstrumentId objects.
        
        Args:
            coins: List of coin information
            
        Returns:
            List of Nautilus InstrumentId objects
        """
        instrument_ids = []
        
        for coin in coins:
            try:
                # Create Nautilus InstrumentId for Binance
                symbol = Symbol(coin.symbol)
                venue = Venue("BINANCE")
                instrument_id = InstrumentId(symbol, venue)
                
                instrument_ids.append(instrument_id)
                
            except Exception as e:
                self.logger.warning(f"Failed to create InstrumentId for {coin.symbol}: {e}")
        
        self.logger.info(f"Created {len(instrument_ids)} Nautilus instrument IDs")
        return instrument_ids
    
    async def get_top_instrument_ids(self, 
                                   count: int = 50,
                                   min_volume_usd: float = 10_000_000) -> List[InstrumentId]:
        """
        Get top trading instrument IDs for Nautilus framework.
        
        Args:
            count: Number of top instruments to return
            min_volume_usd: Minimum 24h volume in USD
            
        Returns:
            List of Nautilus InstrumentId objects
        """
        # Get top coins
        top_coins = await self.get_top_coins(count, min_volume_usd)
        
        # Convert to instrument IDs
        instrument_ids = self.get_nautilus_instrument_ids(top_coins)
        
        return instrument_ids
    
    def get_coin_info(self, symbol: str) -> Optional[CoinInfo]:
        """
        Get detailed information about a specific coin.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            CoinInfo object or None if not found
        """
        return self._cache.get(symbol)
    
    async def validate_instruments(self, instrument_ids: List[InstrumentId]) -> List[InstrumentId]:
        """
        Validate that instruments are available for trading.
        
        Args:
            instrument_ids: List of instrument IDs to validate
            
        Returns:
            List of valid instrument IDs
        """
        # Ensure we have fresh data
        if not self._cache:
            await self._fetch_coin_data()
        
        valid_instruments = []
        
        for instrument_id in instrument_ids:
            symbol = str(instrument_id.symbol)
            
            if symbol in self._cache:
                coin_info = self._cache[symbol]
                if coin_info.is_futures_enabled and coin_info.volume_24h > 0:
                    valid_instruments.append(instrument_id)
                else:
                    self.logger.warning(f"Invalid instrument: {symbol}")
            else:
                self.logger.warning(f"Instrument not found: {symbol}")
        
        self.logger.info(f"Validated {len(valid_instruments)}/{len(instrument_ids)} instruments")
        return valid_instruments
    
    def get_leverage_recommendations(self, coins: List[CoinInfo]) -> Dict[str, int]:
        """
        Get recommended leverage for each coin based on volatility.
        
        Args:
            coins: List of coin information
            
        Returns:
            Dictionary mapping symbol to recommended leverage
        """
        recommendations = {}
        
        for coin in coins:
            # Base leverage on price volatility
            abs_change = abs(coin.price_change_24h)
            
            if abs_change <= 2.0:
                leverage = 10  # Low volatility
            elif abs_change <= 5.0:
                leverage = 7   # Medium volatility
            elif abs_change <= 10.0:
                leverage = 5   # High volatility
            else:
                leverage = 3   # Very high volatility
            
            # Cap at configured maximum
            max_leverage = self.config.trading.max_leverage
            leverage = min(leverage, max_leverage)
            
            recommendations[coin.symbol] = leverage
        
        return recommendations
    
    async def cleanup(self):
        """
        Cleanup resources used by the coin selector.
        
        This method should be called when the coin selector is no longer needed
        to properly close any open connections and free resources.
        """
        try:
            if hasattr(self, 'session') and self.session and not self.session.closed:
                await self.session.close()
                self.logger.debug("HTTP session closed successfully")
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")
        
        # Reset session to None
        if hasattr(self, 'session'):
            self.session = None
