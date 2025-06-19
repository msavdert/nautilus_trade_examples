"""
Top 50 Volume Coin Selector Module
Fetches and selects the highest volume cryptocurrency pairs from Binance Testnet.
"""

import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
import json
from dataclasses import dataclass
from config import get_config


@dataclass
class CoinInfo:
    """Information about a cryptocurrency trading pair."""
    symbol: str
    base_asset: str
    quote_asset: str
    volume_24h_usdt: float
    price: float
    price_change_24h: float
    market_cap_rank: Optional[int] = None


class CoinSelector:
    """
    Selects top volume cryptocurrency pairs from Binance.
    
    Features:
    - Fetches 24h volume data from Binance API
    - Filters out stablecoins and fiat pairs
    - Supports both spot and futures markets
    - Provides real-time volume ranking
    """
    
    # Binance Testnet API endpoints
    TESTNET_BASE_URL = "https://testnet.binance.vision/api"
    FUTURES_BASE_URL = "https://testnet.binance.vision/fapi"
    
    # Common stablecoins to exclude
    STABLECOINS = {
        'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'PAXG', 'USDP',
        'FRAX', 'LUSD', 'USDD', 'GUSD', 'SUSD'
    }
    
    # Fiat currencies to exclude
    FIAT_CURRENCIES = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF',
        'CNY', 'KRW', 'RUB', 'BRL', 'TRY'
    }
    
    def __init__(self):
        """Initialize coin selector."""
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _fetch_json(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Fetch JSON data from API endpoint.
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            self.logger.error(f"API request failed for {url}: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error for {url}: {e}")
            raise
    
    async def get_spot_24h_ticker(self) -> List[Dict[str, Any]]:
        """
        Get 24h ticker statistics for spot trading pairs.
        
        Returns:
            List of 24h ticker data
        """
        url = f"{self.TESTNET_BASE_URL}/v3/ticker/24hr"
        
        try:
            data = await self._fetch_json(url)
            self.logger.info(f"Fetched {len(data)} spot ticker data")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch spot ticker data: {e}")
            return []
    
    async def get_futures_24h_ticker(self) -> List[Dict[str, Any]]:
        """
        Get 24h ticker statistics for futures trading pairs.
        
        Returns:
            List of 24h ticker data
        """
        url = f"{self.FUTURES_BASE_URL}/v1/ticker/24hr"
        
        try:
            data = await self._fetch_json(url)
            self.logger.info(f"Fetched {len(data)} futures ticker data")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch futures ticker data: {e}")
            return []
    
    async def get_exchange_info(self) -> Dict[str, Any]:
        """
        Get exchange information including trading rules.
        
        Returns:
            Exchange information
        """
        if self.config.exchange.account_type == "USDT_FUTURE":
            url = f"{self.FUTURES_BASE_URL}/v1/exchangeInfo"
        else:
            url = f"{self.TESTNET_BASE_URL}/v3/exchangeInfo"
        
        try:
            data = await self._fetch_json(url)
            self.logger.info("Fetched exchange information")
            return data
        except Exception as e:
            self.logger.error(f"Failed to fetch exchange info: {e}")
            return {}
    
    def _filter_trading_pairs(self, ticker_data: List[Dict[str, Any]], 
                             exchange_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter trading pairs based on configuration criteria.
        
        Args:
            ticker_data: 24h ticker data
            exchange_info: Exchange information
            
        Returns:
            Filtered trading pairs
        """
        # Get active symbols from exchange info
        active_symbols = set()
        if 'symbols' in exchange_info:
            for symbol_info in exchange_info['symbols']:
                if symbol_info.get('status') == 'TRADING':
                    active_symbols.add(symbol_info['symbol'])
        
        filtered_pairs = []
        
        for ticker in ticker_data:
            symbol = ticker.get('symbol', '')
            volume = float(ticker.get('quoteVolume', 0))
            
            # Skip if not trading
            if symbol not in active_symbols:
                continue
            
            # Skip if volume is too low
            if volume < self.config.trading.min_24h_volume_usdt:
                continue
            
            # Parse symbol to get base and quote assets
            base_asset, quote_asset = self._parse_symbol(symbol, exchange_info)
            if not base_asset or not quote_asset:
                continue
            
            # Filter stablecoins if configured
            if self.config.trading.exclude_stablecoins:
                if (base_asset in self.STABLECOINS or 
                    quote_asset in self.STABLECOINS):
                    continue
            
            # Filter fiat pairs if configured
            if self.config.trading.exclude_fiat_pairs:
                if (base_asset in self.FIAT_CURRENCIES or 
                    quote_asset in self.FIAT_CURRENCIES):
                    continue
            
            # Add base and quote assets to ticker data
            ticker['baseAsset'] = base_asset
            ticker['quoteAsset'] = quote_asset
            filtered_pairs.append(ticker)
        
        self.logger.info(f"Filtered to {len(filtered_pairs)} trading pairs")
        return filtered_pairs
    
    def _parse_symbol(self, symbol: str, exchange_info: Dict[str, Any]) -> tuple[str, str]:
        """
        Parse symbol to extract base and quote assets.
        
        Args:
            symbol: Trading pair symbol
            exchange_info: Exchange information containing symbol details
            
        Returns:
            Tuple of (base_asset, quote_asset)
        """
        # Try to find symbol in exchange info first
        if 'symbols' in exchange_info:
            for symbol_info in exchange_info['symbols']:
                if symbol_info['symbol'] == symbol:
                    return symbol_info['baseAsset'], symbol_info['quoteAsset']
        
        # Fallback: try common quote assets
        common_quotes = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB', 'BUSD']
        for quote in common_quotes:
            if symbol.endswith(quote):
                base = symbol[:-len(quote)]
                if base:
                    return base, quote
        
        self.logger.warning(f"Could not parse symbol: {symbol}")
        return "", ""
    
    def _create_coin_info_list(self, ticker_data: List[Dict[str, Any]]) -> List[CoinInfo]:
        """
        Create list of CoinInfo objects from ticker data.
        
        Args:
            ticker_data: Filtered ticker data
            
        Returns:
            List of CoinInfo objects
        """
        coin_list = []
        
        for ticker in ticker_data:
            try:
                coin_info = CoinInfo(
                    symbol=ticker['symbol'],
                    base_asset=ticker['baseAsset'],
                    quote_asset=ticker['quoteAsset'],
                    volume_24h_usdt=float(ticker.get('quoteVolume', 0)),
                    price=float(ticker.get('lastPrice', 0)),
                    price_change_24h=float(ticker.get('priceChangePercent', 0))
                )
                coin_list.append(coin_info)
            except (ValueError, KeyError) as e:
                self.logger.warning(f"Error creating CoinInfo for {ticker.get('symbol', 'unknown')}: {e}")
                continue
        
        return coin_list
    
    async def get_top_volume_coins(self, limit: Optional[int] = None) -> List[CoinInfo]:
        """
        Get top volume cryptocurrency pairs.
        
        Args:
            limit: Maximum number of coins to return (defaults to config max_coins)
            
        Returns:
            List of top volume coins sorted by 24h volume
        """
        limit = limit or self.config.trading.max_coins
        
        try:
            # Fetch data concurrently
            if self.config.exchange.account_type == "USDT_FUTURE":
                ticker_task = self.get_futures_24h_ticker()
            else:
                ticker_task = self.get_spot_24h_ticker()
            
            exchange_info_task = self.get_exchange_info()
            
            ticker_data, exchange_info = await asyncio.gather(
                ticker_task, exchange_info_task
            )
            
            if not ticker_data:
                self.logger.error("No ticker data received")
                return []
            
            # Filter and process data
            filtered_pairs = self._filter_trading_pairs(ticker_data, exchange_info)
            coin_list = self._create_coin_info_list(filtered_pairs)
            
            # Sort by volume and take top N
            sorted_coins = sorted(
                coin_list, 
                key=lambda x: x.volume_24h_usdt, 
                reverse=True
            )[:limit]
            
            self.logger.info(f"Selected top {len(sorted_coins)} volume coins")
            
            # Log top 10 for visibility
            for i, coin in enumerate(sorted_coins[:10], 1):
                self.logger.info(
                    f"{i}. {coin.symbol}: "
                    f"${coin.volume_24h_usdt:,.0f} volume, "
                    f"${coin.price:.4f} price, "
                    f"{coin.price_change_24h:+.2f}% change"
                )
            
            return sorted_coins
            
        except Exception as e:
            self.logger.error(f"Error getting top volume coins: {e}")
            return []
    
    async def get_coin_symbols(self, limit: Optional[int] = None) -> List[str]:
        """
        Get list of top volume coin symbols.
        
        Args:
            limit: Maximum number of symbols to return
            
        Returns:
            List of trading pair symbols
        """
        coins = await self.get_top_volume_coins(limit)
        return [coin.symbol for coin in coins]
    
    async def update_coin_list(self) -> List[CoinInfo]:
        """
        Update and return current top volume coins.
        
        Returns:
            Updated list of top volume coins
        """
        self.logger.info("Updating top volume coin list...")
        coins = await self.get_top_volume_coins()
        
        if coins:
            self.logger.info(f"Updated coin list with {len(coins)} coins")
            self.logger.info(f"Top coin: {coins[0].symbol} with ${coins[0].volume_24h_usdt:,.0f} volume")
        else:
            self.logger.warning("Failed to update coin list")
        
        return coins
    
    def get_excluded_assets(self) -> Set[str]:
        """
        Get set of excluded assets based on configuration.
        
        Returns:
            Set of excluded asset symbols
        """
        excluded = set()
        
        if self.config.trading.exclude_stablecoins:
            excluded.update(self.STABLECOINS)
        
        if self.config.trading.exclude_fiat_pairs:
            excluded.update(self.FIAT_CURRENCIES)
        
        return excluded
    
    async def validate_symbols(self, symbols: List[str]) -> List[str]:
        """
        Validate that symbols are currently tradeable.
        
        Args:
            symbols: List of symbols to validate
            
        Returns:
            List of valid symbols
        """
        try:
            exchange_info = await self.get_exchange_info()
            
            if not exchange_info or 'symbols' not in exchange_info:
                self.logger.warning("No exchange info available for validation")
                return symbols
            
            active_symbols = {
                s['symbol'] for s in exchange_info['symbols'] 
                if s.get('status') == 'TRADING'
            }
            
            valid_symbols = [s for s in symbols if s in active_symbols]
            invalid_symbols = [s for s in symbols if s not in active_symbols]
            
            if invalid_symbols:
                self.logger.warning(f"Invalid symbols removed: {invalid_symbols}")
            
            self.logger.info(f"Validated {len(valid_symbols)}/{len(symbols)} symbols")
            return valid_symbols
            
        except Exception as e:
            self.logger.error(f"Error validating symbols: {e}")
            return symbols


async def main():
    """Test the coin selector functionality."""
    logging.basicConfig(level=logging.INFO)
    
    async with CoinSelector() as selector:
        # Test getting top volume coins
        coins = await selector.get_top_volume_coins(10)
        
        print("\n=== Top 10 Volume Coins ===")
        for i, coin in enumerate(coins, 1):
            print(f"{i:2d}. {coin.symbol:<12} "
                  f"Vol: ${coin.volume_24h_usdt:>12,.0f} "
                  f"Price: ${coin.price:>10.4f} "
                  f"Change: {coin.price_change_24h:>+7.2f}%")
        
        # Test getting symbols only
        symbols = await selector.get_coin_symbols(5)
        print(f"\nTop 5 symbols: {symbols}")
        
        # Test validation
        test_symbols = ['BTCUSDT', 'ETHUSDT', 'INVALID', 'ADAUSDT']
        valid_symbols = await selector.validate_symbols(test_symbols)
        print(f"\nValidation test: {test_symbols} -> {valid_symbols}")


if __name__ == "__main__":
    asyncio.run(main())
