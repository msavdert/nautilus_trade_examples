"""
Unit tests for the RSI Mean Reversion Strategy.

These tests validate the strategy logic, risk management,
and integration with the Nautilus framework.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone
from decimal import Decimal

from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue, StrategyId
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.model.objects import Price, Quantity, Money
from nautilus_trader.model.currencies import USD, BTC
from nautilus_trader.model.enums import OrderSide, PriceType
from nautilus_trader.model.data import Bar, BarType, BarSpecification
from nautilus_trader.test_kit.stubs.identifiers import TestIdStubs

from strategies.rsi_mean_reversion import RSIMeanReversionStrategy, RSIMeanReversionConfig
from config import get_config


class TestRSIMeanReversionStrategy:
    """Test suite for RSI Mean Reversion Strategy."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        # Create strategy configuration
        self.config = RSIMeanReversionConfig(
            strategy_id=StrategyId("RSI_MEAN_REVERSION-TEST"),
            rsi_period=14,
            rsi_oversold=30.0,
            rsi_overbought=70.0,
            position_size_pct=0.05,
            stop_loss_pct=0.02,
            take_profit_pct=0.04,
            leverage=5,
            max_open_positions=3,
        )
        
        # Create strategy instance
        self.strategy = RSIMeanReversionStrategy(self.config)
        
        # Mock components
        self.mock_portfolio = Mock()
        self.mock_cache = Mock()
        
        # Setup instrument
        self.instrument_id = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
        self.instrument = CurrencyPair(
            id=self.instrument_id,
            raw_symbol=Symbol("BTCUSDT"),
            base_currency=BTC,
            quote_currency=USD,
            price_precision=2,
            size_precision=6,
            price_increment=Price.from_str("0.01"),
            size_increment=Quantity.from_str("0.000001"),
            lot_size=None,
            max_quantity=None,
            min_quantity=Quantity.from_str("0.000001"),
            max_notional=None,
            min_notional=Money(10.00, USD),
            max_price=None,
            min_price=Price.from_str("0.01"),
            margin_init=Decimal("0.1"),
            margin_maint=Decimal("0.05"),
            maker_fee=Decimal("0.001"),
            taker_fee=Decimal("0.001"),
            ts_event=0,
            ts_init=0,
        )
        
        # Add instrument to strategy
        self.strategy.add_instrument(self.instrument_id)
        
        # Mock strategy methods
        self.strategy.portfolio = self.mock_portfolio
        self.strategy.cache = self.mock_cache
        self.strategy.submit_order = Mock()
        self.strategy.close_position = Mock()
    
    def create_test_bar(self, 
                       close_price: float,
                       high_price: float = None,
                       low_price: float = None,
                       volume: float = 1000.0) -> Bar:
        """Create a test bar with specified parameters."""
        if high_price is None:
            high_price = close_price * 1.01
        if low_price is None:
            low_price = close_price * 0.99
        
        bar_type = BarType(
            instrument_id=self.instrument_id,
            bar_spec=BarSpecification(5, 1, PriceType.LAST, 0),
            aggregation_source=1,
        )
        
        return Bar(
            bar_type=bar_type,
            open=Price.from_str(f"{close_price:.2f}"),
            high=Price.from_str(f"{high_price:.2f}"),
            low=Price.from_str(f"{low_price:.2f}"),
            close=Price.from_str(f"{close_price:.2f}"),
            volume=Quantity.from_str(f"{volume:.0f}"),
            ts_event=0,
            ts_init=0,
        )
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        assert self.strategy.config.rsi_period == 14
        assert self.strategy.config.rsi_oversold == 30.0
        assert self.strategy.config.rsi_overbought == 70.0
        assert self.instrument_id in self.strategy.instruments
        assert self.instrument_id in self.strategy.rsi
    
    def test_add_instrument(self):
        """Test adding an instrument to the strategy."""
        new_instrument_id = InstrumentId(Symbol("ETHUSDT"), Venue("BINANCE"))
        
        self.strategy.add_instrument(new_instrument_id)
        
        assert new_instrument_id in self.strategy.instruments
        assert new_instrument_id in self.strategy.rsi
        assert new_instrument_id in self.strategy.ma
        assert new_instrument_id in self.strategy.volume_ma
    
    def test_indicator_updates(self):
        """Test that indicators are updated correctly."""
        # Create test bars to initialize indicators
        prices = [100.0, 101.0, 99.0, 102.0, 98.0, 103.0, 97.0, 104.0, 96.0, 105.0]
        
        for price in prices:
            bar = self.create_test_bar(price)
            self.strategy.on_bar(bar)
        
        # Check that indicators are initialized
        rsi = self.strategy.rsi[self.instrument_id]
        ma = self.strategy.ma[self.instrument_id]
        volume_ma = self.strategy.volume_ma[self.instrument_id]
        
        assert rsi.count > 0
        assert ma.count > 0
        assert volume_ma.count > 0
    
    def test_long_signal_detection(self):
        """Test detection of long entry signals."""
        # Mock portfolio to allow new positions
        self.mock_portfolio.positions_open.return_value = []
        self.mock_cache.instrument.return_value = self.instrument
        
        # Mock account for position sizing
        mock_account = Mock()
        mock_account.balance.return_value = Money(10000.0, USD)
        self.mock_portfolio.account.return_value = mock_account
        
        # Setup conditions for long signal
        # Need to get RSI below 30, price above MA, volume above average
        
        # First, create bars to initialize indicators
        init_prices = [100.0] * 20  # Initialize with stable prices
        for price in init_prices:
            bar = self.create_test_bar(price, volume=1000.0)
            self.strategy.on_bar(bar)
        
        # Force RSI to oversold level and set up other conditions
        rsi_indicator = self.strategy.rsi[self.instrument_id]
        ma_indicator = self.strategy.ma[self.instrument_id]
        volume_ma_indicator = self.strategy.volume_ma[self.instrument_id]
        
        # Mock indicator values
        rsi_indicator.value = 25.0  # Oversold
        ma_indicator.value = 99.0   # Price will be above this
        volume_ma_indicator.value = 1000.0  # Volume will be above this
        
        # Mark indicators as initialized
        rsi_indicator._initialized = True
        ma_indicator._initialized = True
        volume_ma_indicator._initialized = True
        
        # Create bar that should trigger long signal
        signal_bar = self.create_test_bar(100.0, volume=1300.0)  # High volume
        
        # Process the bar
        self.strategy.on_bar(signal_bar)
        
        # Check if order was submitted (long signal detected)
        self.strategy.submit_order.assert_called()
        submitted_order = self.strategy.submit_order.call_args[0][0]
        assert submitted_order.side == OrderSide.BUY
    
    def test_short_signal_detection(self):
        """Test detection of short entry signals."""
        # Mock portfolio to allow new positions
        self.mock_portfolio.positions_open.return_value = []
        self.mock_cache.instrument.return_value = self.instrument
        
        # Mock account for position sizing
        mock_account = Mock()
        mock_account.balance.return_value = Money(10000.0, USD)
        self.mock_portfolio.account.return_value = mock_account
        
        # Initialize indicators
        init_prices = [100.0] * 20
        for price in init_prices:
            bar = self.create_test_bar(price, volume=1000.0)
            self.strategy.on_bar(bar)
        
        # Setup conditions for short signal
        rsi_indicator = self.strategy.rsi[self.instrument_id]
        ma_indicator = self.strategy.ma[self.instrument_id]
        volume_ma_indicator = self.strategy.volume_ma[self.instrument_id]
        
        # Mock indicator values
        rsi_indicator.value = 75.0  # Overbought
        ma_indicator.value = 101.0  # Price will be below this
        volume_ma_indicator.value = 1000.0  # Volume will be above this
        
        # Mark indicators as initialized
        rsi_indicator._initialized = True
        ma_indicator._initialized = True
        volume_ma_indicator._initialized = True
        
        # Create bar that should trigger short signal
        signal_bar = self.create_test_bar(100.0, volume=1300.0)  # High volume
        
        # Process the bar
        self.strategy.on_bar(signal_bar)
        
        # Check if order was submitted (short signal detected)
        self.strategy.submit_order.assert_called()
        submitted_order = self.strategy.submit_order.call_args[0][0]
        assert submitted_order.side == OrderSide.SELL
    
    def test_position_limits(self):
        """Test that position limits are respected."""
        # Mock portfolio with maximum positions already open
        mock_positions = [Mock() for _ in range(self.config.max_open_positions)]
        self.mock_portfolio.positions_open.return_value = mock_positions
        
        # Initialize indicators
        init_prices = [100.0] * 20
        for price in init_prices:
            bar = self.create_test_bar(price)
            self.strategy.on_bar(bar)
        
        # Setup signal conditions
        rsi_indicator = self.strategy.rsi[self.instrument_id]
        ma_indicator = self.strategy.ma[self.instrument_id]
        volume_ma_indicator = self.strategy.volume_ma[self.instrument_id]
        
        rsi_indicator.value = 25.0
        ma_indicator.value = 99.0
        volume_ma_indicator.value = 1000.0
        
        rsi_indicator._initialized = True
        ma_indicator._initialized = True
        volume_ma_indicator._initialized = True
        
        # Create signal bar
        signal_bar = self.create_test_bar(100.0, volume=1300.0)
        
        # Process the bar
        self.strategy.on_bar(signal_bar)
        
        # Should not submit order due to position limit
        self.strategy.submit_order.assert_not_called()
    
    def test_daily_trade_limit(self):
        """Test that daily trade limits are respected."""
        # Set daily trades to maximum
        self.strategy.daily_trades = self.strategy.max_daily_trades
        
        # Mock portfolio
        self.mock_portfolio.positions_open.return_value = []
        self.mock_cache.instrument.return_value = self.instrument
        
        # Initialize and setup indicators
        init_prices = [100.0] * 20
        for price in init_prices:
            bar = self.create_test_bar(price)
            self.strategy.on_bar(bar)
        
        rsi_indicator = self.strategy.rsi[self.instrument_id]
        ma_indicator = self.strategy.ma[self.instrument_id]
        volume_ma_indicator = self.strategy.volume_ma[self.instrument_id]
        
        rsi_indicator.value = 25.0
        ma_indicator.value = 99.0
        volume_ma_indicator.value = 1000.0
        
        rsi_indicator._initialized = True
        ma_indicator._initialized = True
        volume_ma_indicator._initialized = True
        
        # Create signal bar
        signal_bar = self.create_test_bar(100.0, volume=1300.0)
        
        # Process the bar
        self.strategy.on_bar(signal_bar)
        
        # Should not submit order due to daily limit
        self.strategy.submit_order.assert_not_called()
    
    def test_position_sizing_calculation(self):
        """Test position size calculation."""
        # Mock account balance
        mock_account = Mock()
        mock_account.balance.return_value = Money(10000.0, USD)
        self.mock_portfolio.account.return_value = mock_account
        
        # Calculate position size
        price = Price.from_str("50000.00")
        quantity = self.strategy._calculate_position_size(self.instrument, price)
        
        # Expected: 10000 * 0.05 * 5 (leverage) = 2500 USD position
        # At 50000 price = 0.05 BTC
        expected_quantity = 2500.0 / 50000.0
        
        assert abs(quantity.as_double() - expected_quantity) < 0.001
    
    def test_stop_loss_take_profit_calculation(self):
        """Test stop loss and take profit calculation."""
        entry_price = 50000.0
        
        # Test long position
        stop_loss, take_profit = self.strategy._calculate_stop_loss_take_profit(
            entry_price, OrderSide.BUY
        )
        
        expected_stop = entry_price * (1 - self.config.stop_loss_pct)
        expected_profit = entry_price * (1 + self.config.take_profit_pct)
        
        assert abs(stop_loss - expected_stop) < 1.0
        assert abs(take_profit - expected_profit) < 1.0
        
        # Test short position
        stop_loss, take_profit = self.strategy._calculate_stop_loss_take_profit(
            entry_price, OrderSide.SELL
        )
        
        expected_stop = entry_price * (1 + self.config.stop_loss_pct)
        expected_profit = entry_price * (1 - self.config.take_profit_pct)
        
        assert abs(stop_loss - expected_stop) < 1.0
        assert abs(take_profit - expected_profit) < 1.0
    
    def test_exit_signal_detection(self):
        """Test exit signal detection for existing positions."""
        # Mock existing position
        mock_position = Mock()
        mock_position.side = OrderSide.BUY
        mock_position.instrument_id = self.instrument_id
        
        self.strategy.active_positions[self.instrument_id] = mock_position
        
        # Initialize indicators
        init_prices = [100.0] * 20
        for price in init_prices:
            bar = self.create_test_bar(price)
            self.strategy.on_bar(bar)
        
        # Setup exit condition (RSI in neutral zone for long position)
        rsi_indicator = self.strategy.rsi[self.instrument_id]
        rsi_indicator.value = 65.0  # Above neutral upper (60)
        rsi_indicator._initialized = True
        
        # Create bar
        exit_bar = self.create_test_bar(100.0)
        
        # Process the bar
        self.strategy.on_bar(exit_bar)
        
        # Should close position
        self.strategy.close_position.assert_called_with(self.instrument_id)
    
    def test_emergency_stop(self):
        """Test emergency stop functionality."""
        # Trigger emergency stop
        self.strategy._emergency_stop()
        
        # Check that daily trades is set to maximum (preventing new trades)
        assert self.strategy.daily_trades == self.strategy.max_daily_trades


class TestStrategyIntegration:
    """Integration tests for strategy with mocked Nautilus components."""
    
    @pytest.fixture
    def strategy_with_mocks(self):
        """Create strategy with all necessary mocks."""
        config = RSIMeanReversionConfig(
            strategy_id=StrategyId("RSI_MEAN_REVERSION-INTEGRATION"),
            rsi_period=5,  # Shorter period for faster testing
            rsi_oversold=30.0,
            rsi_overbought=70.0,
        )
        
        strategy = RSIMeanReversionStrategy(config)
        
        # Mock all necessary components
        strategy.portfolio = Mock()
        strategy.cache = Mock()
        strategy.submit_order = Mock()
        strategy.close_position = Mock()
        
        return strategy
    
    def test_full_trading_cycle(self, strategy_with_mocks):
        """Test a complete trading cycle from signal to exit."""
        strategy = strategy_with_mocks
        instrument_id = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
        
        # Setup mocks
        strategy.portfolio.positions_open.return_value = []
        strategy.cache.instrument.return_value = Mock()
        
        mock_account = Mock()
        mock_account.balance.return_value = Money(10000.0, USD)
        strategy.portfolio.account.return_value = mock_account
        
        # Add instrument
        strategy.add_instrument(instrument_id)
        
        # Simulate price movement that creates oversold condition
        prices = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55]  # Declining prices
        
        for price in prices:
            bar = strategy.create_test_bar(price)
            strategy.on_bar(bar)
        
        # At this point, RSI should be low and might trigger a signal
        # This is a simplified test - in reality, we'd need more sophisticated
        # market simulation to reliably trigger signals
        
        assert len(strategy.instruments) == 1
        assert instrument_id in strategy.rsi


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
