#!/usr/bin/env python3
"""
Quick demo runner to test the bot initialization without full connection
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load test environment
load_dotenv('.env.test')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from coin_selector import CoinSelector
from risk_manager import RiskManager


async def demo_bot_initialization():
    """Demo bot initialization without full connection."""
    print("🚀 Binance Testnet Bot - Demo Initialization")
    print("=" * 60)
    
    try:
        # Test configuration
        print("1️⃣ Loading configuration...")
        config = get_config()
        print(f"   ✅ Configuration loaded: {config.strategy.name}")
        print(f"   📊 Max coins: {config.trading.max_coins}")
        print(f"   💰 Initial balance: ${config.initial_balance:,.2f}")
        
        # Test risk manager
        print("\n2️⃣ Initializing risk manager...")
        risk_manager = RiskManager()
        print(f"   ✅ Risk manager initialized")
        print(f"   🛡️ Max risk per trade: {config.trading.max_risk_per_trade_percent:.1f}%")
        
        # Test coin selector (simulated)
        print("\n3️⃣ Testing coin selector...")
        coin_selector = CoinSelector()
        print(f"   ✅ Coin selector initialized")
        print(f"   🔍 Target coin selection: Top {config.trading.max_coins} by volume")
        
        # Simulate coin selection
        print("\n4️⃣ Simulating coin selection...")
        # Note: This would normally connect to Binance API
        print("   🔄 Would fetch top volume coins from Binance Testnet...")
        print("   💡 In real mode, this would filter and select coins")
        
        # Show strategy parameters
        print("\n5️⃣ Strategy configuration:")
        print(f"   📈 ATR period: {config.strategy.atr_period}")
        print(f"   📊 Bollinger period: {config.strategy.bollinger_period}")
        print(f"   📉 RSI period: {config.strategy.rsi_period}")
        print(f"   🔊 Volume threshold: {config.strategy.volume_threshold_multiplier}x")
        
        # Show safety settings
        print("\n6️⃣ Safety settings:")
        print(f"   🛑 Emergency stop: {config.safety.enable_emergency_stop}")
        print(f"   📉 Max drawdown: {config.strategy.max_drawdown_percent}%")
        print(f"   🔄 Max consecutive losses: {config.safety.max_consecutive_losses}")
        
        print("\n🎉 Demo initialization completed successfully!")
        print("\n📝 Next steps for real trading:")
        print("   1. Set real Binance Testnet API credentials in .env file")
        print("   2. Run: python main.py --mode demo")
        print("   3. Monitor logs for trading activity")
        print("   4. Use analyze_results.py to review performance")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo initialization failed: {e}")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(demo_bot_initialization())
        if success:
            print("\n✨ Bot is ready for trading!")
        else:
            print("\n⚠️  Please fix configuration issues before trading")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
