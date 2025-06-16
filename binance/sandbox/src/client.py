"""
Binance Spot API Client
Handles REST API and WebSocket connections to Binance
"""
import asyncio
import hashlib
import hmac
import time
import json
import logging
from typing import Dict, Any, Optional, List, Callable
from urllib.parse import urlencode

import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from .config import Config


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors"""
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error {code}: {message}")


class BinanceClient:
    """
    Binance Spot Trading Client
    Provides REST API and WebSocket functionality
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self._running = False
        
    async def __aenter__(self):
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()
        
    async def start(self):
        """Initialize the client"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=30)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.config.get_headers()
            )
        self._running = True
        self.logger.info("Binance client started")
        
    async def stop(self):
        """Cleanup and close connections"""
        self._running = False
        
        # Close WebSocket connections
        for name, ws in self._ws_connections.items():
            try:
                await ws.close()
                self.logger.info(f"Closed WebSocket connection: {name}")
            except Exception as e:
                self.logger.warning(f"Error closing WebSocket {name}: {e}")
        
        self._ws_connections.clear()
        
        # Close HTTP session
        if self._session:
            await self._session.close()
            self._session = None
            
        self.logger.info("Binance client stopped")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """Generate HMAC SHA256 signature for authenticated requests"""
        query_string = urlencode(params)
        return hmac.new(
            self.config.binance_secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """Make authenticated or public API request"""
        if not self._session:
            raise RuntimeError("Client not started. Use async context manager or call start()")
            
        params = params or {}
        url = f"{self.config.base_url}{endpoint}"
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        try:
            if method.upper() == "GET":
                async with self._session.get(url, params=params) as response:
                    data = await response.json()
            elif method.upper() == "POST":
                async with self._session.post(url, data=params) as response:
                    data = await response.json()
            elif method.upper() == "DELETE":
                async with self._session.delete(url, params=params) as response:
                    data = await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Check for API errors
            if 'code' in data and 'msg' in data:
                raise BinanceAPIError(data['code'], data['msg'])
                
            return data
            
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response: {e}")
            raise
    
    # Public API Methods
    async def get_server_time(self) -> Dict[str, Any]:
        """Get server time"""
        return await self._make_request("GET", "/api/v3/time")
    
    async def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange trading rules and symbol information"""
        return await self._make_request("GET", "/api/v3/exchangeInfo")
    
    async def get_symbol_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get 24hr ticker price change statistics"""
        params = {"symbol": symbol.upper()}
        return await self._make_request("GET", "/api/v3/ticker/24hr", params)
    
    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Get order book for symbol"""
        params = {"symbol": symbol.upper(), "limit": limit}
        return await self._make_request("GET", "/api/v3/depth", params)
    
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 500,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[List]:
        """Get kline/candlestick data"""
        params = {
            "symbol": symbol.upper(),
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
            
        return await self._make_request("GET", "/api/v3/klines", params)
    
    # Authenticated API Methods
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return await self._make_request("GET", "/api/v3/account", signed=True)
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all open orders"""
        params = {}
        if symbol:
            params["symbol"] = symbol.upper()
        return await self._make_request("GET", "/api/v3/openOrders", params, signed=True)
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """Place a new order"""
        params = {
            "symbol": symbol.upper(),
            "side": side.upper(),  # BUY or SELL
            "type": order_type.upper(),  # LIMIT, MARKET, etc.
            "quantity": str(quantity),
            "timeInForce": time_in_force
        }
        
        if price and order_type.upper() in ["LIMIT", "STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT"]:
            params["price"] = str(price)
            
        return await self._make_request("POST", "/api/v3/order", params, signed=True)
    
    async def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an open order"""
        params = {
            "symbol": symbol.upper(),
            "orderId": order_id
        }
        return await self._make_request("DELETE", "/api/v3/order", params, signed=True)
    
    # WebSocket Methods
    async def connect_websocket(
        self,
        stream_name: str,
        callback: Callable[[Dict[str, Any]], None],
        streams: List[str]
    ):
        """Connect to Binance WebSocket stream"""
        stream_url = f"{self.config.ws_base_url}/ws/{'/'.join(streams)}"
        
        try:
            async with websockets.connect(stream_url) as websocket:
                self._ws_connections[stream_name] = websocket
                self.logger.info(f"Connected to WebSocket stream: {stream_name}")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await asyncio.create_task(self._handle_ws_message(callback, data))
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to decode WebSocket message: {e}")
                    except Exception as e:
                        self.logger.error(f"Error handling WebSocket message: {e}")
                        
        except ConnectionClosed:
            self.logger.warning(f"WebSocket connection closed: {stream_name}")
        except WebSocketException as e:
            self.logger.error(f"WebSocket error for {stream_name}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in WebSocket {stream_name}: {e}")
        finally:
            if stream_name in self._ws_connections:
                del self._ws_connections[stream_name]
    
    async def _handle_ws_message(self, callback: Callable, data: Dict[str, Any]):
        """Handle incoming WebSocket message"""
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(data)
            else:
                callback(data)
        except Exception as e:
            self.logger.error(f"Error in WebSocket callback: {e}")
    
    async def subscribe_ticker(self, symbols: List[str], callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to ticker updates"""
        streams = [f"{symbol.lower()}@ticker" for symbol in symbols]
        await self.connect_websocket("ticker", callback, streams)
    
    async def subscribe_klines(
        self,
        symbols: List[str],
        interval: str,
        callback: Callable[[Dict[str, Any]], None]
    ):
        """Subscribe to kline/candlestick updates"""
        streams = [f"{symbol.lower()}@kline_{interval}" for symbol in symbols]
        await self.connect_websocket(f"klines_{interval}", callback, streams)
    
    async def subscribe_orderbook(
        self,
        symbols: List[str],
        callback: Callable[[Dict[str, Any]], None],
        update_speed: str = "1000ms"
    ):
        """Subscribe to order book updates"""
        streams = [f"{symbol.lower()}@depth@{update_speed}" for symbol in symbols]
        await self.connect_websocket("orderbook", callback, streams)
