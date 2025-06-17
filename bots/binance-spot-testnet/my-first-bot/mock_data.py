#!/usr/bin/env python3
"""
Mock market data generator for testnet environments.
Simulates real market data when WebSocket streams are not available.
"""

import asyncio
import random
from decimal import Decimal
from nautilus_trader.model.data import QuoteTick, TradeTick
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.core.datetime import dt_to_unix_nanos
from datetime import datetime, timezone


class MockDataGenerator:
    """Generates mock market data for testing purposes."""
    
    def __init__(self, instrument, base_price: float = 45000.0):
        self.instrument = instrument
        self.base_price = base_price
        self.current_price = base_price
        self.is_running = False
        
    async def start_mock_data(self, strategy, interval_seconds: float = 1.0):
        """Start generating mock market data."""
        self.is_running = True
        
        while self.is_running:
            try:
                # Generate price movement (small random walk)
                price_change = random.uniform(-50, 50)  # $50 max change
                self.current_price = max(1000, self.current_price + price_change)
                
                # Create mock quote tick
                bid_price = Price(self.current_price - random.uniform(0.1, 2.0), precision=2)
                ask_price = Price(self.current_price + random.uniform(0.1, 2.0), precision=2)
                
                quote_tick = QuoteTick(
                    instrument_id=self.instrument.id,
                    bid_price=bid_price,
                    ask_price=ask_price,
                    bid_size=Quantity(random.uniform(0.1, 5.0), precision=8),
                    ask_size=Quantity(random.uniform(0.1, 5.0), precision=8),
                    ts_event=dt_to_unix_nanos(datetime.now(timezone.utc)),
                    ts_init=dt_to_unix_nanos(datetime.now(timezone.utc))
                )
                
                # Send to strategy
                strategy.on_quote_tick(quote_tick)
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                print(f"Mock data error: {e}")
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop generating mock data."""
        self.is_running = False
