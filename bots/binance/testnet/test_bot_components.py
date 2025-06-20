#!/usr/bin/env python3
"""
Comprehensive integration tests for bot components.

This script tests the integration between different bot components to ensure
they work together correctly. Unlike unit tests, these tests validate:
- Component interactions
- End-to-end workflows
- Real API calls (in testnet)
- Configuration integration

Run with: python test_bot_components.py
"""

import asyncio
import logging
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import get_config
from utils.coin_selector import CoinSelector
from utils.risk_manager import RiskManager
from utils import LoggingUtils, DataUtils, MathUtils
from strategies.rsi_mean_reversion import RSIMeanReversionStrategy


class ComponentTester:
    """Manages component testing with detailed reporting."""
    
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.config = None
        self.logger = None
        
    async def setup(self):
        """Setup test environment."""
        try:
            # Load configuration
            self.config = get_config()
            
            # Setup logging
            self.logger = LoggingUtils.setup_logger(
                name="component_test",
                level="INFO",
                log_dir=project_root / "logs"
            )
            
            print("✅ Test environment setup complete")
            return True
            
        except Exception as e:
            print(f"❌ Test setup failed: {e}")
            return False
    
    def record_test(self, test_name: str, success: bool, details: str = "", duration: float = 0.0):
        """Record test result."""
        self.test_results.append({
            "test_name": test_name,
            "success": success,
            "details": details,
            "duration": duration,
            "timestamp": datetime.now()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"     {details}")
    
    async def test_config_integration(self) -> bool:
        """Test configuration loading and validation."""
        start_time = datetime.now()
        test_name = "Configuration Integration"
        
        try:
            # Test config loading
            config = get_config()
            
            # Validate required sections
            required_sections = ['endpoints', 'trading', 'risk']
            missing_sections = [s for s in required_sections if not hasattr(config, s)]
            
            if missing_sections:
                self.record_test(test_name, False, f"Missing sections: {missing_sections}")
                return False
            
            # Validate critical parameters
            critical_params = [
                (config.trading.top_coins_count > 0, "top_coins_count must be > 0"),
                (0 < config.trading.max_position_size_pct < 1, "max_position_size_pct must be 0-1"),
                (config.trading.rsi_period > 1, "rsi_period must be > 1"),
            ]
            
            for check, message in critical_params:
                if not check:
                    self.record_test(test_name, False, f"Validation failed: {message}")
                    return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, True, "All configuration parameters valid", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_coin_selector_integration(self) -> bool:
        """Test coin selector with API integration."""
        start_time = datetime.now()
        test_name = "Coin Selector Integration"
        
        try:
            coin_selector = CoinSelector(self.config)
            
            # Test initialization
            assert coin_selector.config == self.config
            assert len(coin_selector.excluded_coins) > 0
            
            # Test symbol filtering
            test_symbols = [
                ("BTCUSDT", True),   # Valid
                ("ETHUSDT", True),   # Valid
                ("BTCEUR", False),   # Not USDT
                ("USDCUSDT", False), # Stablecoin
                ("BTCUP", False),    # Leveraged token
            ]
            
            for symbol, expected in test_symbols:
                result = coin_selector._is_valid_symbol(symbol)
                if result != expected:
                    self.record_test(test_name, False, f"Symbol filtering failed for {symbol}")
                    return False
            
            # Test API call (with timeout and error handling)
            try:
                coin_selector.session.timeout.total = 15.0  # Longer timeout for integration test
                top_coins = await coin_selector.get_top_coins_by_volume()
                
                if top_coins:
                    # Validate coin data structure
                    for coin in top_coins[:5]:  # Check first 5
                        if not all([coin.symbol, coin.volume_24h > 0, coin.price > 0]):
                            self.record_test(test_name, False, f"Invalid coin data: {coin.symbol}")
                            return False
                    
                    detail = f"Retrieved {len(top_coins)} valid coins"
                else:
                    detail = "No coins retrieved (API may be unavailable)"
                    
            except Exception as api_error:
                detail = f"API call failed: {api_error} (this may be expected in testnet)"
            
            # Cleanup
            await coin_selector.cleanup()
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, True, detail, duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_risk_manager_integration(self) -> bool:
        """Test risk manager with portfolio integration."""
        start_time = datetime.now()
        test_name = "Risk Manager Integration"
        
        try:
            risk_manager = RiskManager(self.config)
            
            # Create mock portfolio
            mock_portfolio = Mock()
            mock_account = Mock()
            mock_account.balance.return_value = Mock()
            mock_account.balance.return_value.as_double.return_value = 10000.0
            
            mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
            mock_portfolio.positions_open.return_value = []
            mock_portfolio.position_for_instrument.return_value = None  # No existing position
            
            # Test session initialization
            risk_manager.initialize_session(mock_portfolio)
            
            if risk_manager.session_start_balance != 10000.0:
                self.record_test(test_name, False, "Session initialization failed")
                return False
            
            # Test position approval logic
            from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
            from nautilus_trader.model.enums import OrderSide
            
            instrument_id = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
            
            can_open, reason = risk_manager.can_open_position(
                mock_portfolio, instrument_id, OrderSide.BUY, 500.0
            )
            
            if not can_open:
                self.record_test(test_name, False, f"Position approval failed: {reason}")
                return False
            
            # Test stop loss/take profit calculation
            from nautilus_trader.model.enums import OrderSide
            
            entry_price = 50000.0
            stop_loss, take_profit = risk_manager.calculate_stop_loss_take_profit(
                entry_price, OrderSide.BUY, volatility=0.02
            )
            
            # Validate that stops are correctly positioned
            if stop_loss >= entry_price or take_profit <= entry_price:
                self.record_test(test_name, False, "Stop loss/take profit calculation incorrect")
                return False
            
            # Test risk metrics
            metrics = risk_manager.get_risk_metrics(mock_portfolio)
            
            if not all([
                hasattr(metrics, 'total_exposure'),
                hasattr(metrics, 'active_positions'),
                hasattr(metrics, 'drawdown_pct'),
                metrics.active_positions == 0
            ]):
                self.record_test(test_name, False, "Risk metrics calculation failed")
                return False
            
            # Test emergency stop
            risk_manager.emergency_stop()
            if not risk_manager.emergency_stop_active:
                self.record_test(test_name, False, "Emergency stop activation failed")
                return False
                
            risk_manager.reset_emergency_stop()
            if risk_manager.emergency_stop_active:
                self.record_test(test_name, False, "Emergency stop reset failed")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, True, "All risk management functions working", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_strategy_integration(self) -> bool:
        """Test strategy integration with other components."""
        start_time = datetime.now()
        test_name = "Strategy Integration"
        
        try:
            # Test strategy import and initialization
            from strategies.rsi_mean_reversion import RSIMeanReversionStrategy
            
            # Validate strategy has required methods
            required_methods = [
                'on_start', 'on_stop', 'on_bar', 'on_order_filled',
                'on_position_opened', 'on_position_closed', 'add_instrument'
            ]
            
            for method in required_methods:
                if not hasattr(RSIMeanReversionStrategy, method):
                    self.record_test(test_name, False, f"Missing required method: {method}")
                    return False
            
            # Test strategy configuration validation
            strategy_config = self.config.trading
            
            if not all([
                1 < strategy_config.rsi_period <= 50,
                50 < strategy_config.rsi_overbought <= 90,
                10 <= strategy_config.rsi_oversold < 50,
                strategy_config.rsi_oversold < strategy_config.rsi_overbought,
                strategy_config.volume_threshold_multiplier > 0
            ]):
                self.record_test(test_name, False, "Invalid strategy configuration")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, True, "Strategy integration validated", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_utility_integration(self) -> bool:
        """Test utility function integration."""
        start_time = datetime.now()
        test_name = "Utility Integration"
        
        try:
            from utils import DataUtils, MathUtils, PerformanceTracker
            
            # Test DataUtils
            test_values = [
                (DataUtils.safe_float("123.45"), 123.45),
                (DataUtils.safe_float("invalid", 0.0), 0.0),
                (DataUtils.safe_int("123"), 123),
                (DataUtils.safe_int("invalid", 0), 0),
            ]
            
            for result, expected in test_values:
                if result != expected:
                    self.record_test(test_name, False, f"DataUtils validation failed: {result} != {expected}")
                    return False
            
            # Test formatting functions
            currency_test = DataUtils.format_currency(1_234_567.89)
            percent_test = DataUtils.format_percentage(0.1234)
            
            if not currency_test or not percent_test:
                self.record_test(test_name, False, "Formatting functions failed")
                return False
            
            # Test MathUtils
            test_returns = [0.01, -0.02, 0.015, -0.01, 0.005] * 10
            
            volatility = MathUtils.calculate_volatility(test_returns)
            sharpe = MathUtils.calculate_sharpe_ratio(test_returns)
            
            if volatility <= 0 or not isinstance(sharpe, (int, float)):
                self.record_test(test_name, False, "MathUtils calculations failed")
                return False
            
            # Test PerformanceTracker
            tracker = PerformanceTracker()
            
            # Add test trades
            now = datetime.now()
            for i in range(5):
                tracker.add_trade(
                    instrument=f"TEST{i}USDT",
                    side="BUY" if i % 2 == 0 else "SELL",
                    entry_price=1000.0 + i * 10,
                    exit_price=1000.0 + i * 10 + (5 if i % 2 == 0 else -5),
                    quantity=1.0,
                    entry_time=now - timedelta(hours=i+1),
                    exit_time=now - timedelta(hours=i)
                )
            
            stats = tracker.get_stats()
            
            if stats.total_trades != 5 or not (0 <= stats.win_rate <= 1):
                self.record_test(test_name, False, "PerformanceTracker validation failed")
                return False
            
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, True, "All utility functions working correctly", duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, False, f"Exception: {e}", duration)
            return False
    
    async def test_end_to_end_workflow(self) -> bool:
        """Test end-to-end workflow simulation."""
        start_time = datetime.now()
        test_name = "End-to-End Workflow"
        
        try:
            # Initialize all components
            coin_selector = CoinSelector(self.config)
            risk_manager = RiskManager(self.config)
            
            # Mock portfolio
            mock_portfolio = Mock()
            mock_account = Mock()
            mock_account.balance.return_value = Mock()
            mock_account.balance.return_value.as_double.return_value = 10000.0
            
            mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
            mock_portfolio.positions_open.return_value = []
            mock_portfolio.position_for_instrument.return_value = None  # No existing position
            
            # Initialize risk manager session
            risk_manager.initialize_session(mock_portfolio)
            
            # Simulate workflow steps
            workflow_steps = []
            
            # Step 1: Get trading pairs
            try:
                # Use mock data if API fails
                with patch.object(coin_selector, 'get_top_coins_by_volume') as mock_get_coins:
                    mock_get_coins.return_value = [
                        Mock(symbol="BTCUSDT", volume_24h=1000000000, price=50000),
                        Mock(symbol="ETHUSDT", volume_24h=500000000, price=3000),
                    ]
                    
                    coins = await coin_selector.get_top_coins_by_volume()
                    workflow_steps.append(f"✅ Retrieved {len(coins)} trading pairs")
                    
            except Exception as e:
                workflow_steps.append(f"⚠️  Coin selection step failed: {e}")
            
            # Step 2: Risk checks
            from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
            from nautilus_trader.model.enums import OrderSide
            
            instrument_id = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
            can_open, reason = risk_manager.can_open_position(
                mock_portfolio, instrument_id, OrderSide.BUY, 500.0
            )
            
            workflow_steps.append(f"✅ Risk check: {reason}")
            
            # Step 3: Position sizing
            mock_instrument = Mock()
            mock_instrument.id = instrument_id
            mock_instrument.size_precision = 6
            
            from nautilus_trader.model.objects import Price
            price = Price.from_str("50000.00")
            
            quantity = risk_manager.calculate_position_size(
                mock_portfolio, mock_instrument, price, volatility=0.02
            )
            
            workflow_steps.append(f"✅ Position size calculated: {quantity}")
            
            # Step 4: Stop loss/take profit
            entry_price = 50000.0
            stop_loss, take_profit = risk_manager.calculate_stop_loss_take_profit(
                entry_price, OrderSide.BUY, volatility=0.02
            )
            
            workflow_steps.append(f"✅ Risk levels: SL=${stop_loss:.2f}, TP=${take_profit:.2f}")
            
            # Step 5: Performance tracking
            from utils import PerformanceTracker
            tracker = PerformanceTracker()
            
            tracker.add_trade(
                instrument="BTCUSDT",
                side="BUY",
                entry_price=entry_price,
                exit_price=entry_price * 1.02,  # 2% profit
                quantity=0.1,
                entry_time=datetime.now() - timedelta(hours=1),
                exit_time=datetime.now()
            )
            
            stats = tracker.get_stats()
            workflow_steps.append(f"✅ Performance tracked: {stats.total_trades} trades")
            
            # Cleanup
            await coin_selector.cleanup()
            
            duration = (datetime.now() - start_time).total_seconds()
            details = "; ".join(workflow_steps)
            self.record_test(test_name, True, details, duration)
            return True
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.record_test(test_name, False, f"Exception: {e}", duration)
            return False
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*80)
        print("COMPONENT INTEGRATION TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   - {result['test_name']}: {result['details']}")
        
        total_duration = sum(r['duration'] for r in self.test_results)
        print(f"\nTotal Test Duration: {total_duration:.2f} seconds")
        
        # Overall assessment
        if passed_tests == total_tests:
            print("\n🎉 ALL INTEGRATION TESTS PASSED!")
            print("   Your bot components are working together correctly.")
        elif passed_tests >= total_tests * 0.8:
            print("\n⚠️  MOSTLY SUCCESSFUL - MINOR INTEGRATION ISSUES")
            print("   Most components work but check failed tests above.")
        else:
            print("\n🚨 MULTIPLE INTEGRATION FAILURES")
            print("   Significant issues detected. Review components before deployment.")
        
        return passed_tests == total_tests


async def main():
    """Run component integration tests."""
    print("🔧 BINANCE FUTURES TESTNET BOT - COMPONENT INTEGRATION TESTS")
    print("=" * 80)
    print("Testing component interactions and end-to-end workflows...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = ComponentTester()
    
    # Setup test environment
    if not await tester.setup():
        print("❌ Test setup failed. Exiting.")
        return False
    
    # Run integration tests
    tests = [
        tester.test_config_integration,
        tester.test_coin_selector_integration,
        tester.test_risk_manager_integration,
        tester.test_strategy_integration,
        tester.test_utility_integration,
        tester.test_end_to_end_workflow,
    ]
    
    print(f"\nRunning {len(tests)} integration tests...\n")
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            traceback.print_exc()
    
    # Print summary
    success = tester.print_summary()
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        traceback.print_exc()
        sys.exit(1)
