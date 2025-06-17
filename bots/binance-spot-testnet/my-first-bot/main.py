#!/usr/bin/env python3

import asyncio
import json
from decimal import Decimal

from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
from nautilus_trader.adapters.sandbox.factory import SandboxLiveExecClientFactory
from nautilus_trader.common.enums import LogColor
from nautilus_trader.core.data import Data
from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.data import Bar, QuoteTick, TradeTick
from nautilus_trader.model.identifiers import ClientId, InstrumentId
from nautilus_trader.trading import Strategy
from nautilus_trader.trading.config import StrategyConfig

from config import create_config


# *** THIS IS A TEST STRATEGY WITH NO ALPHA ADVANTAGE WHATSOEVER. ***
# *** IT IS NOT INTENDED TO BE USED TO TRADE LIVE WITH REAL MONEY. ***


class TestStrategyConfig(StrategyConfig, frozen=True):
    spot_instrument_id: InstrumentId


class TestStrategy(Strategy):
    def __init__(self, config: TestStrategyConfig) -> None:
        super().__init__(config)
        self.spot_instrument = None  # Initialized in on_start

    def on_start(self) -> None:
        self.spot_instrument = self.cache.instrument(self.config.spot_instrument_id)
        if self.spot_instrument is None:
            self.log.error(
                f"Could not find instrument for {self.config.spot_instrument_id}"
                f"\nPossible instruments: {self.cache.instrument_ids()}",
            )
            self.stop()
            return

        # Get account balances
        account = self.portfolio.account(venue=self.spot_instrument.venue)
        balances = {str(currency): str(balance) for currency, balance in account.balances().items()}
        self.log.info(f"Spot balances\n{json.dumps(balances, indent=4)}", LogColor.GREEN)

        # Note: Binance Spot Testnet has limited WebSocket support
        # Real-time market data streams are not available on testnet
        self.log.info("📊 Testnet Environment - Limited market data", LogColor.BLUE)
        self.log.info("ℹ️  Real-time streams not available on testnet (this is normal)", LogColor.BLUE)
        self.log.info("🤖 Bot is running in simulation mode...", LogColor.GREEN)
        
        # For testnet, we'll work without live market data
        # In production, you would subscribe to real streams:
        # self.subscribe_trade_ticks(self.config.spot_instrument_id)
        # self.subscribe_quote_ticks(self.config.spot_instrument_id)

    def on_data(self, data: Data) -> None:
        self.log.info(f"📊 Received data: {repr(data)}", LogColor.CYAN)

    def on_quote_tick(self, tick: QuoteTick) -> None:
        self.log.info(f"💰 Quote tick: {repr(tick)}", LogColor.CYAN)

    def on_trade_tick(self, tick: TradeTick) -> None:
        self.log.info(f"💹 Trade tick: {repr(tick)}", LogColor.CYAN)

    def on_bar(self, bar: Bar) -> None:
        self.log.info(f"📈 Bar data: {repr(bar)}", LogColor.CYAN)

    def on_stop(self) -> None:
        # Clean stop - no subscriptions to unsubscribe in testnet mode
        self.log.info("🛑 Strategy stopped successfully", LogColor.BLUE)


async def main():
    """
    Show how to run a strategy in a sandbox for the Binance venue.
    """
    # Configure the trading node
    config_node = create_config()

    # Instantiate the node with a configuration
    node = TradingNode(config=config_node)

    # Configure your strategy
    strat_config = TestStrategyConfig(
        spot_instrument_id=InstrumentId.from_str("BTCUSDT.BINANCE"),
    )
    # Instantiate your strategy
    strategy = TestStrategy(config=strat_config)

    # Add your strategies and modules
    node.trader.add_strategy(strategy)

    # Register your client factories with the node (can take user-defined factories)
    node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
    node.add_exec_client_factory("BINANCE", SandboxLiveExecClientFactory)
    node.build()

    print("🚀 Starting Nautilus Trader bot...")
    print("📖 Press CTRL+C to stop the bot gracefully")

    try:
        await node.run_async()
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user (CTRL+C)")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔄 Shutting down bot...")
        await shutdown_node_safely(node)


async def shutdown_node_safely(node: TradingNode):
    """Safely shutdown the trading node to avoid runtime errors."""
    try:
        # First, try to stop the node gracefully
        if hasattr(node, '_loop') and node._loop and not node._loop.is_closed():
            await node.stop_async()
            # Give some time for async cleanup
            await asyncio.sleep(0.2)
        else:
            print("⚠️  Event loop already closed, skipping async stop")
    except RuntimeError as e:
        if "Event loop stopped before Future completed" in str(e):
            print("ℹ️  Note: Event loop shutdown warning (this is normal)")
        else:
            print(f"⚠️  Shutdown warning: {e}")
    except Exception as e:
        print(f"⚠️  Shutdown error: {e}")
    finally:
        try:
            # Always try to dispose resources
            node.dispose()
            print("✅ Bot shutdown complete")
        except Exception as e:
            print(f"⚠️  Final cleanup warning: {e}")


# Stop and dispose of the node with SIGINT/CTRL+C
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot terminated by user")
    except (RuntimeError, asyncio.CancelledError) as e:
        if "Event loop stopped" in str(e) or "CancelledError" in str(e):
            print("ℹ️  Bot shutdown completed (normal cleanup)")
        else:
            print(f"❌ Runtime error: {e}")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
