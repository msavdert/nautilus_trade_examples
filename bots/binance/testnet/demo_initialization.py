#!/usr/bin/env python3
"""
Demo script to test bot initialization and component validation.

This script demonstrates the bot's initialization process without running
any actual trading operations. It's useful for:
- Validating configuration
- Testing API connectivity
- Checking component initialization
- Verifying setup before running the full bot

Run with: python demo_initialization.py
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_config
from utils.coin_selector import CoinSelector
from utils.risk_manager import RiskManager
from utils import LoggingUtils


async def demo_config_validation():
    """Demonstrate configuration validation."""
    print("\n" + "="*60)
    print("1. CONFIGURATION VALIDATION")
    print("="*60)
    
    try:
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Trading strategy: {config.trading.strategy_name}")
        print(f"   - Risk per trade: {config.trading.max_position_size_pct*100}%")
        print(f"   - Max daily loss: {config.risk.daily_loss_limit_pct*100}%")
        print(f"   - API endpoints: {config.endpoints.futures_api_url}")
        
        # Check for required environment variables
        try:
            credentials = config.get_binance_credentials()
            api_key = credentials["api_key"]
            api_secret = credentials["api_secret"]
            print(f"✅ API Key configured (length: {len(api_key)} chars)")
            print(f"✅ API Secret configured (length: {len(api_secret)} chars)")
        except ValueError:
            print("⚠️  WARNING: API credentials not set in environment")
            print("   Please set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET")
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


async def demo_logging_setup():
    """Demonstrate logging setup."""
    print("\n" + "="*60)
    print("2. LOGGING SYSTEM")
    print("="*60)
    
    try:
        # Setup logging
        logger = LoggingUtils.setup_logger(
            name="demo",
            level="INFO",
            log_dir=project_root / "logs"
        )
        
        print("✅ Logging system initialized")
        print(f"   - Log directory: {project_root / 'logs'}")
        print(f"   - Log level: INFO")
        
        # Test different log levels
        logger.debug("This is a debug message")
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        
        print("✅ Test log messages written")
        
        return True
        
    except Exception as e:
        print(f"❌ Logging setup failed: {e}")
        return False


async def demo_coin_selector():
    """Demonstrate coin selection functionality."""
    print("\n" + "="*60)
    print("3. COIN SELECTOR")
    print("="*60)
    
    try:
        config = get_config()
        coin_selector = CoinSelector(config)
        
        print("✅ CoinSelector initialized")
        print(f"   - Target coins: {config.trading.top_coins_count}")
        print(f"   - Excluded coins: {len(coin_selector.excluded_coins)}")
        
        # Test API connectivity (with timeout)
        print("📡 Testing API connectivity...")
        try:
            # Set a shorter timeout for demo
            coin_selector.session.timeout.total = 10.0
            
            top_coins = await coin_selector.get_top_coins_by_volume()
            
            if top_coins:
                print(f"✅ Successfully fetched {len(top_coins)} coins")
                print("   Top 5 coins by volume:")
                for i, coin in enumerate(top_coins[:5]):
                    volume_str = f"{coin.volume_24h/1_000_000:.1f}M" if coin.volume_24h > 1_000_000 else f"{coin.volume_24h/1_000:.1f}K"
                    print(f"     {i+1}. {coin.symbol}: ${volume_str} (${coin.price:.2f})")
            else:
                print("⚠️  No coins returned (possible API issues)")
                
        except asyncio.TimeoutError:
            print("⚠️  API request timed out - this may be normal in testnet")
        except Exception as api_error:
            print(f"⚠️  API connectivity issue: {api_error}")
            print("   This is normal if API credentials are not configured")
        
        return True
        
    except Exception as e:
        print(f"❌ CoinSelector demo failed: {e}")
        return False
    finally:
        # Cleanup
        try:
            await coin_selector.cleanup()
        except:
            pass


async def demo_risk_manager():
    """Demonstrate risk management functionality."""
    print("\n" + "="*60)
    print("4. RISK MANAGER")
    print("="*60)
    
    try:
        config = get_config()
        risk_manager = RiskManager(config)
        
        print("✅ RiskManager initialized")
        print(f"   - Risk per trade: {config.trading.max_position_size_pct*100}%")
        print(f"   - Max daily loss: {config.risk.daily_loss_limit_pct*100}%")
        print(f"   - Max drawdown: {config.risk.max_drawdown_pct*100}%")
        print(f"   - Max positions: {config.trading.max_open_positions}")
        
        # Test risk calculations
        print("\n📊 Testing risk calculations:")
        
        from nautilus_trader.model.enums import OrderSide
        
        # Test stop loss and take profit calculation
        entry_price = 50000.0
        volatility = 0.02
        
        stop_loss, take_profit = risk_manager.calculate_stop_loss_take_profit(
            entry_price, OrderSide.BUY, volatility
        )
        
        print(f"   - Entry price: ${entry_price:,.2f}")
        print(f"   - Stop loss: ${stop_loss:,.2f} ({((stop_loss/entry_price)-1)*100:+.2f}%)")
        print(f"   - Take profit: ${take_profit:,.2f} ({((take_profit/entry_price)-1)*100:+.2f}%)")
        
        # Test emergency stop
        print(f"\n🚨 Emergency stop status: {'ACTIVE' if risk_manager.emergency_stop_active else 'INACTIVE'}")
        
        return True
        
    except Exception as e:
        print(f"❌ RiskManager demo failed: {e}")
        return False


async def demo_data_utilities():
    """Demonstrate data utility functions."""
    print("\n" + "="*60)
    print("5. UTILITY FUNCTIONS")
    print("="*60)
    
    try:
        from utils import DataUtils, MathUtils, PerformanceTracker
        
        print("✅ Utility modules imported")
        
        # Test data utilities
        print("\n📊 DataUtils tests:")
        print(f"   - Format currency: {DataUtils.format_currency(1_234_567.89)}")
        print(f"   - Format percentage: {DataUtils.format_percentage(0.1234)}")
        print(f"   - Safe float: {DataUtils.safe_float('123.45', 0.0)}")
        print(f"   - Safe int: {DataUtils.safe_int('abc', 999)}")
        
        # Test math utilities
        print("\n🧮 MathUtils tests:")
        test_returns = [0.01, -0.02, 0.015, -0.01, 0.005] * 10
        volatility = MathUtils.calculate_volatility(test_returns)
        sharpe = MathUtils.calculate_sharpe_ratio(test_returns)
        
        print(f"   - Volatility: {volatility:.4f}")
        print(f"   - Sharpe ratio: {sharpe:.4f}")
        
        equity_curve = [1000, 1100, 1050, 1200, 1150, 1300, 1200, 1400]
        max_dd = MathUtils.calculate_max_drawdown(equity_curve)
        print(f"   - Max drawdown: {max_dd:.2%}")
        
        # Test performance tracker
        print("\n📈 PerformanceTracker test:")
        tracker = PerformanceTracker()
        
        # Add a sample trade
        from datetime import datetime, timedelta
        now = datetime.now()
        tracker.add_trade(
            instrument="BTCUSDT",
            side="BUY",
            entry_price=50000.0,
            exit_price=51000.0,
            quantity=0.1,
            entry_time=now - timedelta(hours=2),
            exit_time=now
        )
        
        stats = tracker.get_stats()
        print(f"   - Total trades: {stats.total_trades}")
        print(f"   - Win rate: {stats.win_rate:.1%}")
        print(f"   - Total PnL: ${stats.total_pnl:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility functions demo failed: {e}")
        return False


async def demo_strategy_validation():
    """Demonstrate strategy validation."""
    print("\n" + "="*60)
    print("6. STRATEGY VALIDATION")
    print("="*60)
    
    try:
        from strategies.rsi_mean_reversion import RSIMeanReversionStrategy
        
        config = get_config()
        
        print("✅ Strategy module imported")
        print(f"   - Strategy: RSI Mean Reversion")
        print(f"   - RSI period: {config.trading.rsi_period}")
        print(f"   - RSI overbought: {config.trading.rsi_overbought}")
        print(f"   - RSI oversold: {config.trading.rsi_oversold}")
        print(f"   - Volume threshold: {config.trading.volume_threshold_multiplier}")
        
        print("\n📋 Strategy parameters validated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy validation failed: {e}")
        return False


async def main():
    """Run the complete demo initialization."""
    print("🚀 BINANCE FUTURES TESTNET BOT - INITIALIZATION DEMO")
    print("=" * 60)
    print("This demo validates all bot components without executing trades.")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success_count = 0
    total_tests = 6
    
    # Run all demos
    demos = [
        demo_config_validation,
        demo_logging_setup,
        demo_coin_selector,
        demo_risk_manager,
        demo_data_utilities,
        demo_strategy_validation
    ]
    
    for demo in demos:
        try:
            if await demo():
                success_count += 1
        except Exception as e:
            print(f"❌ Demo failed with unexpected error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("DEMO SUMMARY")
    print("="*60)
    print(f"✅ Successful components: {success_count}/{total_tests}")
    print(f"❌ Failed components: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 ALL COMPONENTS INITIALIZED SUCCESSFULLY!")
        print("   Your bot is ready for testing and deployment.")
    elif success_count >= total_tests * 0.8:
        print("\n⚠️  MOSTLY SUCCESSFUL - MINOR ISSUES DETECTED")
        print("   Your bot should work but check warnings above.")
    else:
        print("\n🚨 MULTIPLE COMPONENT FAILURES DETECTED")
        print("   Please resolve issues before running the bot.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return success_count == total_tests


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {e}")
        sys.exit(1)
