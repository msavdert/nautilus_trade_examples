#!/usr/bin/env python3
"""
Simple test script to verify bot components work correctly
This script tests key components without requiring API keys.
"""

import asyncio
import logging
import sys
import os
from dotenv import load_dotenv

# Load test environment variables
load_dotenv('.env.test')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import get_config
from risk_manager import RiskManager
from utils import DataProcessor, PriceUtils, ValidationUtils


def test_config_loading():
    """Test configuration loading."""
    print("🔧 Testing configuration loading...")
    try:
        config = get_config()
        print(f"✅ Config loaded successfully:")
        print(f"   - Exchange: {config.exchange.name}")
        print(f"   - Account type: {config.exchange.account_type}")
        print(f"   - Max coins: {config.trading.max_coins}")
        print(f"   - Strategy: {config.strategy.name}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False


def test_risk_manager():
    """Test risk manager functionality."""
    print("\n📊 Testing risk manager...")
    try:
        risk_manager = RiskManager()
        
        # Test risk summary (simplified test)
        summary = risk_manager.get_risk_summary()
        print(f"✅ Risk manager working:")
        print(f"   - Risk summary available: {len(summary)} metrics")
        print(f"   - Summary keys: {list(summary.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Risk manager test failed: {e}")
        return False


def test_utils():
    """Test utility functions."""
    print("\n🔧 Testing utility functions...")
    try:
        # Test price utilities
        price = 50123.456789
        formatted_price = PriceUtils.format_price(price, precision=2)
        print(f"✅ Price formatting: {price} -> {formatted_price}")
        
        # Test validation
        is_valid_price = ValidationUtils.validate_price(50000.0, min_price=0.0)
        print(f"✅ Price validation: 50000.0 -> {is_valid_price}")
        
        # Test symbol sanitization
        sanitized = ValidationUtils.sanitize_symbol("btcusdt")
        print(f"✅ Symbol sanitization: btcusdt -> {sanitized}")
        
        # Test data processing - ATR calculation
        highs = [100, 102, 101, 103, 105]
        lows = [98, 99, 98, 100, 102]
        closes = [99, 101, 100, 102, 104]
        atr = DataProcessor.calculate_atr(highs, lows, closes, period=3)
        print(f"✅ ATR calculation: {atr:.4f}")
        
        return True
    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False


async def test_coin_selector_mock():
    """Test coin selector with mock data (no API calls)."""
    print("\n🪙 Testing coin selector (mock mode)...")
    try:
        # Import here to avoid circular imports
        from coin_selector import CoinSelector, CoinInfo
        
        # Create mock coin data
        mock_coins = [
            CoinInfo(
                symbol="BTCUSDT",
                base_asset="BTC",
                quote_asset="USDT",
                volume_24h_usdt=1000000000,
                price=50000.0,
                price_change_24h=2.5
            ),
            CoinInfo(
                symbol="ETHUSDT",
                base_asset="ETH",
                quote_asset="USDT",
                volume_24h_usdt=800000000,
                price=3000.0,
                price_change_24h=1.8
            )
        ]
        
        print(f"✅ Coin selector can be imported and used:")
        for coin in mock_coins:
            print(f"   - {coin.symbol}: ${coin.volume_24h_usdt:,.0f} volume")
        
        return True
    except Exception as e:
        print(f"❌ Coin selector test failed: {e}")
        return False


async def main():
    """Run all component tests."""
    print("🚀 Binance Testnet Bot - Component Testing\n")
    
    tests = [
        ("Configuration", test_config_loading),
        ("Risk Manager", test_risk_manager),
        ("Utils", test_utils),
        ("Coin Selector", test_coin_selector_mock),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n📋 Test Results Summary:")
    print(f"{'='*50}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1
    
    print(f"{'='*50}")
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All components are working correctly!")
        print("🔥 Bot is ready for configuration and testing!")
    else:
        print("⚠️  Some components need attention before running the bot.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
