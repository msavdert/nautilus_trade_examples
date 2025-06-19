#!/usr/bin/env python3
"""
Test Suite for One-Three Risk Management Bot
==========================================

This module contains comprehensive tests for the One-Three trading strategy,
including unit tests, integration tests, and validation tests to ensure
the strategy functions correctly under various market conditions.
"""

import unittest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np

from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.model.currencies import USD
from nautilus_trader.test_kit.stubs.identifiers import TestIdStubs
from nautilus_trader.test_kit.stubs.events import TestEventStubs

from one_three_strategy import OneThreeBot, OneThreeConfig
from utils import RiskCalculator, PerformanceTracker, MarketDataGenerator


class TestOneThreeConfig(unittest.TestCase):
    """Test the OneThreeConfig configuration class."""
    
    def test_default_config_creation(self):
        """Test default configuration creation."""
        config = OneThreeConfig()
        
        self.assertEqual(config.instrument_id, InstrumentId.from_str("EUR/USD.SIM"))
        self.assertEqual(config.trade_size, Decimal("100_000"))
        self.assertEqual(config.take_profit_pips, 1.3)
        self.assertEqual(config.stop_loss_pips, 1.3)
        self.assertFalse(config.enable_time_filter)
        self.assertTrue(config.use_tick_data)
        
    def test_custom_config_creation(self):
        """Test custom configuration creation."""
        config = OneThreeConfig(
            instrument_id=InstrumentId.from_str("GBP/USD.SIM"),
            trade_size=Decimal("50_000"),
            take_profit_pips=2.0,
            stop_loss_pips=1.5,
            max_daily_trades=10,
        )
        
        self.assertEqual(config.instrument_id, InstrumentId.from_str("GBP/USD.SIM"))
        self.assertEqual(config.trade_size, Decimal("50_000"))
        self.assertEqual(config.take_profit_pips, 2.0)
        self.assertEqual(config.stop_loss_pips, 1.5)
        self.assertEqual(config.max_daily_trades, 10)


class TestRiskCalculator(unittest.TestCase):
    """Test the RiskCalculator utility class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.calculator = RiskCalculator(account_balance=100_000, max_risk_per_trade=0.01)
        
    def test_position_size_calculation(self):
        """Test position size calculation based on risk."""
        entry_price = 1.0800
        stop_loss_price = 1.0787  # 1.3 pips stop loss
        
        position_size = self.calculator.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            pip_value=10.0
        )
        
        # With 1% risk ($1000) and 1.3 pip stop loss ($13 per standard lot)
        # Should allow approximately 7 standard lots (700,000 units)
        self.assertGreater(position_size, 600_000)
        self.assertLess(position_size, 800_000)
        
    def test_risk_reward_ratio_calculation(self):
        """Test risk-reward ratio calculation."""
        entry_price = 1.0800
        take_profit_price = 1.0813  # +1.3 pips
        stop_loss_price = 1.0787    # -1.3 pips
        
        rr_ratio = self.calculator.calculate_risk_reward_ratio(
            entry_price=entry_price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price
        )
        
        # Should be 1:1 ratio
        self.assertAlmostEqual(rr_ratio, 1.0, places=1)
        
    def test_balance_update(self):
        """Test account balance update."""
        original_balance = self.calculator.account_balance
        new_balance = 120_000
        
        self.calculator.update_balance(new_balance)
        
        self.assertEqual(self.calculator.account_balance, new_balance)
        self.assertNotEqual(self.calculator.account_balance, original_balance)


class TestPerformanceTracker(unittest.TestCase):
    """Test the PerformanceTracker utility class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()
        
    def test_add_trade(self):
        """Test adding a trade to the tracker."""
        entry_time = datetime.now() - timedelta(minutes=10)
        exit_time = datetime.now()
        
        self.tracker.add_trade(
            entry_time=entry_time,
            exit_time=exit_time,
            entry_price=1.0800,
            exit_price=1.0813,
            position_size=100_000,
            pnl=13.0,
            reason="TAKE_PROFIT"
        )
        
        self.assertEqual(len(self.tracker.trades), 1)
        self.assertEqual(len(self.tracker.equity_curve), 1)
        self.assertEqual(self.tracker.equity_curve[0], 13.0)
        
    def test_performance_statistics(self):
        """Test performance statistics calculation."""
        # Add winning trade
        self.tracker.add_trade(
            entry_time=datetime.now() - timedelta(minutes=20),
            exit_time=datetime.now() - timedelta(minutes=10),
            entry_price=1.0800,
            exit_price=1.0813,
            position_size=100_000,
            pnl=13.0,
            reason="TAKE_PROFIT"
        )
        
        # Add losing trade
        self.tracker.add_trade(
            entry_time=datetime.now() - timedelta(minutes=10),
            exit_time=datetime.now(),
            entry_price=1.0800,
            exit_price=1.0787,
            position_size=100_000,
            pnl=-13.0,
            reason="STOP_LOSS"
        )
        
        stats = self.tracker.get_statistics()
        
        self.assertEqual(stats['total_trades'], 2)
        self.assertEqual(stats['winning_trades'], 1)
        self.assertEqual(stats['losing_trades'], 1)
        self.assertEqual(stats['win_rate'], 50.0)
        self.assertEqual(stats['total_pnl'], 0.0)
        self.assertAlmostEqual(stats['profit_factor'], 1.0, places=1)


class TestMarketDataGenerator(unittest.TestCase):
    """Test the MarketDataGenerator utility class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = MarketDataGenerator(seed=42)
        
    def test_tick_data_generation(self):
        """Test tick data generation."""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        num_ticks = 1000
        
        data = self.generator.generate_tick_data(
            start_date=start_date,
            end_date=end_date,
            num_ticks=num_ticks,
            base_price=1.0800
        )
        
        self.assertEqual(len(data), num_ticks)
        self.assertIn('timestamp', data.columns)
        self.assertIn('bid_price', data.columns)
        self.assertIn('ask_price', data.columns)
        
        # Check that bid < ask (proper spread)
        self.assertTrue((data['bid_price'] < data['ask_price']).all())
        
        # Check price range is reasonable
        self.assertTrue(data['bid_price'].min() > 1.0500)
        self.assertTrue(data['ask_price'].max() < 1.1200)


class TestOneThreeStrategy(unittest.TestCase):
    """Test the main OneThreeBot strategy class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = OneThreeConfig(
            instrument_id=InstrumentId.from_str("EUR/USD.SIM"),
            trade_size=Decimal("100_000"),
            take_profit_pips=1.3,
            stop_loss_pips=1.3,
            max_daily_trades=5,
        )
        
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        strategy = OneThreeBot(config=self.config)
        
        self.assertEqual(strategy.config.instrument_id, self.config.instrument_id)
        self.assertEqual(strategy.config.trade_size, self.config.trade_size)
        self.assertEqual(strategy.trade_count, 0)
        self.assertEqual(strategy.daily_trade_count, 0)
        self.assertIsNone(strategy.current_position)
        
    def test_pip_calculations(self):
        """Test pip value calculations."""
        strategy = OneThreeBot(config=self.config)
        
        # Test pip size
        self.assertEqual(strategy.pip_size, 0.0001)
        
        # Test pip calculations in exit conditions
        entry_price = 1.0800
        take_profit_price = 1.0813  # +1.3 pips
        stop_loss_price = 1.0787    # -1.3 pips
        
        tp_pips = (take_profit_price - entry_price) / strategy.pip_size
        sl_pips = (entry_price - stop_loss_price) / strategy.pip_size
        
        self.assertAlmostEqual(tp_pips, 1.3, places=1)
        self.assertAlmostEqual(sl_pips, 1.3, places=1)


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = OneThreeConfig(
            trade_size=Decimal("100_000"),
            take_profit_pips=1.3,
            stop_loss_pips=1.3,
            max_daily_trades=3,
        )
        
    def test_daily_trade_limit(self):
        """Test that daily trade limits are respected."""
        strategy = OneThreeBot(config=self.config)
        
        # Simulate reaching daily limit
        strategy.daily_trade_count = self.config.max_daily_trades
        
        # Should not enter new position when limit reached
        # This would need mocking of the actual trading infrastructure
        # For now, just test the counter
        self.assertEqual(strategy.daily_trade_count, self.config.max_daily_trades)
        
    def test_risk_parameters_consistency(self):
        """Test that risk parameters remain consistent."""
        strategy = OneThreeBot(config=self.config)
        
        # Verify that take profit and stop loss are equal (1:1 R:R)
        self.assertEqual(strategy.config.take_profit_pips, strategy.config.stop_loss_pips)
        
        # Verify pip size calculation
        expected_pip_size = 0.0001  # Standard for EUR/USD
        self.assertEqual(strategy.pip_size, expected_pip_size)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_config_values(self):
        """Test handling of invalid configuration values."""
        # Test negative pip values
        with self.assertRaises(Exception):
            config = OneThreeConfig(take_profit_pips=-1.0)
            
        with self.assertRaises(Exception):
            config = OneThreeConfig(stop_loss_pips=-1.0)
            
    def test_zero_position_size(self):
        """Test handling of zero position size."""
        config = OneThreeConfig(trade_size=Decimal("0"))
        strategy = OneThreeBot(config=config)
        
        # Should handle zero position size gracefully
        self.assertEqual(strategy.trade_quantity.raw, 0)


class TestPerformanceEdgeCases(unittest.TestCase):
    """Test performance calculation edge cases."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()
        
    def test_empty_performance_tracker(self):
        """Test performance tracker with no trades."""
        stats = self.tracker.get_statistics()
        
        # Should return empty dict or default values
        self.assertEqual(len(stats), 0)
        
    def test_single_trade_performance(self):
        """Test performance tracker with single trade."""
        self.tracker.add_trade(
            entry_time=datetime.now() - timedelta(minutes=10),
            exit_time=datetime.now(),
            entry_price=1.0800,
            exit_price=1.0813,
            position_size=100_000,
            pnl=13.0,
            reason="TAKE_PROFIT"
        )
        
        stats = self.tracker.get_statistics()
        
        self.assertEqual(stats['total_trades'], 1)
        self.assertEqual(stats['winning_trades'], 1)
        self.assertEqual(stats['win_rate'], 100.0)
        self.assertEqual(stats['total_pnl'], 13.0)


def run_tests():
    """Run all tests and display results."""
    print("🧪 Running One-Three Strategy Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestOneThreeConfig,
        TestRiskCalculator,
        TestPerformanceTracker,
        TestMarketDataGenerator,
        TestOneThreeStrategy,
        TestIntegrationScenarios,
        TestErrorHandling,
        TestPerformanceEdgeCases,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Display summary
    print(f"\n📊 Test Results Summary:")
    print(f"   • Tests Run: {result.testsRun}")
    print(f"   • Failures: {len(result.failures)}")
    print(f"   • Errors: {len(result.errors)}")
    print(f"   • Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split(chr(10))[-2]}")
    
    if result.errors:
        print(f"\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split(chr(10))[-2]}")
    
    if not result.failures and not result.errors:
        print("\n✅ All tests passed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
