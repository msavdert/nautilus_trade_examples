#!/usr/bin/env python3
"""
Comprehensive test suite for the One-Three-Melih Trading Strategy
================================================================

This module contains unit tests for the BalanceTracker and OneThreeMelihStrategy
classes, ensuring the step-back balance management logic works correctly.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.test_kit.stubs.identifiers import TestIdStubs

from one_three_melih_strategy import (
    BalanceTracker, 
    OneThreeMelihStrategy, 
    OneThreeMelihConfig
)


class TestBalanceTracker:
    """Test suite for the BalanceTracker class."""
    
    def test_initial_state(self):
        """Test initial balance tracker state."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        assert tracker.get_current_balance() == Decimal("100.00")
        assert tracker.initial_balance == Decimal("100.00")
        assert tracker.trade_count == 0
        assert len(tracker.balance_history) == 1
        assert tracker.balance_history[0] == Decimal("100.00")
    
    def test_profit_target_calculation(self):
        """Test profit target calculation."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        profit_target = tracker.get_profit_target()
        assert profit_target == Decimal("30.00")
        
        # After a winning trade
        tracker.record_profit()
        profit_target = tracker.get_profit_target()
        expected_profit = Decimal("130.00") * Decimal("30.0") / Decimal("100.0")
        assert profit_target == expected_profit
    
    def test_stop_loss_percentage_initial(self):
        """Test stop loss percentage at initial balance."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # At initial balance, should use fixed percentage
        stop_loss_pct = tracker.get_stop_loss_percentage()
        assert stop_loss_pct == Decimal("30.00")
    
    def test_stop_loss_percentage_after_profit(self):
        """Test dynamic stop loss percentage after profit."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Record a profit (balance goes to $130)
        tracker.record_profit()
        
        # Stop loss should return to previous balance ($100)
        stop_loss_pct = tracker.get_stop_loss_percentage()
        # Loss needed: $130 - $100 = $30, which is 30/130 = 23.08%
        expected_pct = (Decimal("30.00") / Decimal("130.00")) * Decimal("100.00")
        assert abs(stop_loss_pct - expected_pct) < Decimal("0.01")
    
    def test_record_profit_progression(self):
        """Test balance progression through profitable trades."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # First profit: $100 -> $130
        balance = tracker.record_profit()
        assert balance == Decimal("130.00")
        assert tracker.trade_count == 1
        assert len(tracker.balance_history) == 2
        
        # Second profit: $130 -> $169
        balance = tracker.record_profit()
        expected_balance = Decimal("130.00") * Decimal("1.30")
        assert abs(balance - expected_balance) < Decimal("0.01")
        assert tracker.trade_count == 2
        assert len(tracker.balance_history) == 3
    
    def test_record_loss_step_back(self):
        """Test step-back logic for losses."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Build up some profits
        tracker.record_profit()  # $100 -> $130
        tracker.record_profit()  # $130 -> $169
        
        # Record a loss (should step back to $130)
        balance = tracker.record_loss()
        assert balance == Decimal("130.00")
        assert tracker.trade_count == 3
        assert len(tracker.balance_history) == 2
        
        # Another loss (should step back to $100)
        balance = tracker.record_loss()
        assert balance == Decimal("100.00")
        assert tracker.trade_count == 4
        assert len(tracker.balance_history) == 1
    
    def test_record_loss_at_initial_balance(self):
        """Test loss recording at initial balance."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Loss at initial balance should stay at initial balance
        balance = tracker.record_loss()
        assert balance == Decimal("100.00")
        assert tracker.trade_count == 1
        assert len(tracker.balance_history) == 1
    
    def test_position_size_calculation(self):
        """Test position size calculation based on EUR/USD price."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Test with EUR/USD price of 1.1000
        price = Price(Decimal("1.1000"), precision=5)
        position_size = tracker.get_position_size(price)
        
        # Expected: $100 / 1.1000 = ~90.91 EUR, rounded to nearest 1000
        assert position_size.as_decimal() >= Decimal("1000")  # Minimum size
    
    def test_statistics_generation(self):
        """Test statistics generation."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Record some trades
        tracker.record_profit()  # Win
        tracker.record_profit()  # Win  
        tracker.record_loss()    # Loss
        
        stats = tracker.get_stats()
        
        assert stats["initial_balance"] == 100.0
        assert stats["current_balance"] == 130.0  # Stepped back from $169 to $130
        assert stats["trade_count"] == 3
        assert stats["current_step"] == 2
        assert stats["total_return_pct"] == 30.0  # 30% gain overall


class TestOneThreeMelihStrategy:
    """Test suite for the OneThreeMelihStrategy class."""
    
    @pytest.fixture
    def strategy_config(self):
        """Create a test strategy configuration."""
        return OneThreeMelihConfig(
            strategy_id=TestIdStubs.strategy_id(),
            initial_balance=Decimal("100.00"),
            profit_target_percentage=Decimal("30.0"),
        )
    
    @pytest.fixture
    def strategy(self, strategy_config):
        """Create a test strategy instance."""
        return OneThreeMelihStrategy(strategy_config)
    
    def test_strategy_initialization(self, strategy):
        """Test strategy initialization."""
        assert strategy.balance_tracker.initial_balance == Decimal("100.00")
        assert strategy.balance_tracker.profit_percentage == Decimal("30.0")
        assert strategy.current_position is None
        assert strategy.total_trades == 0
        assert strategy.winning_trades == 0
        assert strategy.losing_trades == 0
        assert strategy.consecutive_losses == 0
    
    def test_balance_tracker_integration(self, strategy):
        """Test integration with balance tracker."""
        # Initial state
        assert strategy.balance_tracker.get_current_balance() == Decimal("100.00")
        
        # Simulate a profitable trade
        strategy.balance_tracker.record_profit()
        assert strategy.balance_tracker.get_current_balance() == Decimal("130.00")
        
        # Simulate a losing trade
        strategy.balance_tracker.record_loss()
        assert strategy.balance_tracker.get_current_balance() == Decimal("100.00")


class TestIntegrationScenarios:
    """Integration test scenarios for complete trading workflows."""
    
    def test_complete_trading_scenario(self):
        """Test a complete trading scenario with multiple wins and losses."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Scenario: Win, Win, Loss, Win, Loss, Loss
        results = []
        
        # Trade 1: Win ($100 -> $130)
        balance = tracker.record_profit()
        results.append(("Win", balance))
        
        # Trade 2: Win ($130 -> $169)
        balance = tracker.record_profit()
        results.append(("Win", balance))
        
        # Trade 3: Loss ($169 -> $130, step back)
        balance = tracker.record_loss()
        results.append(("Loss", balance))
        
        # Trade 4: Win ($130 -> $169)
        balance = tracker.record_profit()
        results.append(("Win", balance))
        
        # Trade 5: Loss ($169 -> $130, step back)
        balance = tracker.record_loss()
        results.append(("Loss", balance))
        
        # Trade 6: Loss ($130 -> $100, step back)
        balance = tracker.record_loss()
        results.append(("Loss", balance))
        
        # Verify final state
        assert tracker.get_current_balance() == Decimal("100.00")
        assert tracker.trade_count == 6
        assert len(tracker.balance_history) == 1  # Back to initial
        
        # Verify the progression was correct
        expected_balances = [
            Decimal("130.00"),  # First win
            Decimal("169.00"),  # Second win  
            Decimal("130.00"),  # Loss, step back
            Decimal("169.00"),  # Win again
            Decimal("130.00"),  # Loss, step back
            Decimal("100.00"),  # Loss, step back to initial
        ]
        
        for i, (trade_type, balance) in enumerate(results):
            assert abs(balance - expected_balances[i]) < Decimal("0.01"), f"Trade {i+1} balance mismatch"
    
    def test_maximum_step_progression(self):
        """Test progression to higher steps and proper step-back."""
        tracker = BalanceTracker(
            initial_balance=Decimal("100.00"),
            profit_percentage=Decimal("30.0")
        )
        
        # Build up to step 5 with consecutive wins
        expected_balances = [Decimal("100.00")]
        current_balance = Decimal("100.00")
        
        for i in range(5):
            current_balance = tracker.record_profit()
            expected_balances.append(current_balance)
        
        # Verify we're at step 6 (index 5)
        assert len(tracker.balance_history) == 6
        
        # Now step back through losses
        for i in range(5):
            balance = tracker.record_loss()
            expected_balance = expected_balances[-(i+2)]  # Step back
            assert abs(balance - expected_balance) < Decimal("0.01")
        
        # Should be back at initial balance
        assert tracker.get_current_balance() == Decimal("100.00")
        assert len(tracker.balance_history) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
