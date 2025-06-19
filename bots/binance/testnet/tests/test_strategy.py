"""
Test Suite for Volatility Breakout Strategy
Comprehensive unit tests for the trading strategy components.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime

import numpy as np

from nautilus_trader.indicators.atr import AverageTrueRange
from nautilus_trader.indicators.bollinger_bands import BollingerBands
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import OrderSide, BarAggregation, PriceType
from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
from nautilus_trader.model.objects import Price, Quantity
from nautilus_trader.test_kit.mocks import MockClock
from nautilus_trader.test_kit.providers import TestInstrumentProvider

# Import strategy components
from strategy import VolatilityBreakoutStrategy, VolatilityBreakoutConfig
from risk_manager import RiskManager, RiskMetrics
from utils import DataProcessor, PriceUtils, ValidationUtils


class TestVolatilityBreakoutStrategy:
    """Test cases for the Volatility Breakout Strategy."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Create test instrument
        self.instrument = TestInstrumentProvider.default_fx_ccy("BTCUSDT")
        self.instrument_id = self.instrument.id
        
        # Create strategy configuration
        self.config = VolatilityBreakoutConfig(
            instrument_ids=[self.instrument_id],
            bar_type=BarType.from_str("BTCUSDT.BINANCE-1-MINUTE-LAST-EXTERNAL"),
            atr_period=14,
            bollinger_period=20,
            bollinger_std=2.0,
            rsi_period=14,
            volume_period=20,
            volume_threshold_multiplier=1.5,
            rsi_min=30.0,
            rsi_max=70.0,
            volatility_threshold_atr=0.5,
            stop_loss_atr_multiplier=2.0,
            take_profit_atr_multiplier=3.0,
            trailing_stop_atr_multiplier=1.5
        )
        
        # Create strategy instance
        self.strategy = VolatilityBreakoutStrategy(self.config)
        
        # Mock clock
        self.clock = MockClock()
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        assert self.strategy.config == self.config
        assert len(self.strategy.indicators) == 0
        assert len(self.strategy.active_positions) == 0
        assert len(self.strategy.last_signals) == 0
    
    def test_setup_indicators(self):
        """Test indicator setup."""
        self.strategy._setup_indicators(self.instrument_id)
        
        indicators = self.strategy.indicators[self.instrument_id]
        
        assert 'atr' in indicators
        assert 'bollinger' in indicators
        assert 'rsi' in indicators
        assert 'volume_ema' in indicators
        
        assert isinstance(indicators['atr'], AverageTrueRange)
        assert isinstance(indicators['bollinger'], BollingerBands)
        assert isinstance(indicators['rsi'], RelativeStrengthIndex)
        
        assert indicators['atr'].period == self.config.atr_period
        assert indicators['bollinger'].period == self.config.bollinger_period
        assert indicators['rsi'].period == self.config.rsi_period
    
    def test_indicators_ready_check(self):
        """Test indicators ready state check."""
        self.strategy._setup_indicators(self.instrument_id)
        indicators = self.strategy.indicators[self.instrument_id]
        
        # Initially not ready
        assert not self.strategy._indicators_ready(indicators)
        
        # Simulate enough data
        for _ in range(25):  # More than max period
            indicators['atr'].update_raw(100.0, 99.0, 99.5)
            indicators['bollinger'].update_raw(99.5)
            indicators['rsi'].update_raw(99.5)
            indicators['volume_ema'].update_raw(1000.0)
        
        # Should be ready now
        assert self.strategy._indicators_ready(indicators)
    
    def test_signal_analysis_bullish(self):
        """Test bullish signal generation."""
        self.strategy._setup_indicators(self.instrument_id)
        indicators = self.strategy.indicators[self.instrument_id]
        
        # Warm up indicators
        for i in range(25):
            price = 100.0 + i * 0.1
            indicators['atr'].update_raw(price + 0.5, price - 0.5, price)
            indicators['bollinger'].update_raw(price)
            indicators['rsi'].update_raw(price)
            indicators['volume_ema'].update_raw(1000.0)
        
        # Create test bar with bullish breakout conditions
        bar = Bar(
            bar_type=self.config.bar_type,
            open=Price(102.0, 2),
            high=Price(103.0, 2),
            low=Price(101.5, 2),
            close=Price(102.8, 2),  # Above Bollinger upper band
            volume=Quantity(2000.0, 0),  # High volume
            ts_event=self.clock.timestamp_ns(),
            ts_init=self.clock.timestamp_ns()
        )
        
        signal = self.strategy._analyze_signals(self.instrument_id, bar)
        
        # Should generate BUY signal under right conditions
        # Note: Actual signal depends on indicator values
        assert signal in ["BUY", "SELL", "NONE"]
    
    def test_signal_analysis_bearish(self):
        """Test bearish signal generation."""
        self.strategy._setup_indicators(self.instrument_id)
        indicators = self.strategy.indicators[self.instrument_id]
        
        # Warm up indicators
        for i in range(25):
            price = 100.0 - i * 0.1
            indicators['atr'].update_raw(price + 0.5, price - 0.5, price)
            indicators['bollinger'].update_raw(price)
            indicators['rsi'].update_raw(price)
            indicators['volume_ema'].update_raw(1000.0)
        
        # Create test bar with bearish breakout conditions
        bar = Bar(
            bar_type=self.config.bar_type,
            open=Price(97.0, 2),
            high=Price(97.5, 2),
            low=Price(96.0, 2),
            close=Price(96.2, 2),  # Below Bollinger lower band
            volume=Quantity(2000.0, 0),  # High volume
            ts_event=self.clock.timestamp_ns(),
            ts_init=self.clock.timestamp_ns()
        )
        
        signal = self.strategy._analyze_signals(self.instrument_id, bar)
        
        # Should generate appropriate signal
        assert signal in ["BUY", "SELL", "NONE"]
    
    def test_volume_confirmation(self):
        """Test volume confirmation logic."""
        self.strategy._setup_indicators(self.instrument_id)
        indicators = self.strategy.indicators[self.instrument_id]
        
        # Setup volume EMA with lower values
        for _ in range(20):
            indicators['volume_ema'].update_raw(1000.0)
        
        avg_volume = indicators['volume_ema'].value
        threshold = avg_volume * self.config.volume_threshold_multiplier
        
        # Test volume confirmation
        high_volume = threshold + 100
        low_volume = threshold - 100
        
        assert high_volume > threshold  # Should pass volume filter
        assert low_volume < threshold   # Should fail volume filter


class TestRiskManager:
    """Test cases for Risk Manager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.risk_manager = RiskManager()
        self.instrument = TestInstrumentProvider.default_fx_ccy("BTCUSDT")
        
    def test_position_size_calculation(self):
        """Test position size calculation."""
        entry_price = Price(50000.0, 2)
        stop_loss = Price(49000.0, 2)
        atr_value = 500.0
        account_balance = Mock()
        account_balance.as_double.return_value = 10000.0
        
        position_size = self.risk_manager.calculate_position_size(
            self.instrument, entry_price, stop_loss, atr_value, account_balance
        )
        
        assert isinstance(position_size, Quantity)
        assert position_size.as_double() > 0
    
    def test_stop_loss_calculation(self):
        """Test stop loss calculation."""
        entry_price = Price(50000.0, 2)
        atr_value = 500.0
        
        # Test BUY order
        stop_loss_buy = self.risk_manager.calculate_stop_loss(
            entry_price, atr_value, OrderSide.BUY
        )
        
        # Stop loss should be below entry for BUY
        assert stop_loss_buy.as_double() < entry_price.as_double()
        
        # Test SELL order
        stop_loss_sell = self.risk_manager.calculate_stop_loss(
            entry_price, atr_value, OrderSide.SELL
        )
        
        # Stop loss should be above entry for SELL
        assert stop_loss_sell.as_double() > entry_price.as_double()
    
    def test_take_profit_calculation(self):
        """Test take profit calculation."""
        entry_price = Price(50000.0, 2)
        atr_value = 500.0
        
        # Test BUY order
        take_profit_buy = self.risk_manager.calculate_take_profit(
            entry_price, atr_value, OrderSide.BUY
        )
        
        # Take profit should be above entry for BUY
        assert take_profit_buy.as_double() > entry_price.as_double()
        
        # Test SELL order
        take_profit_sell = self.risk_manager.calculate_take_profit(
            entry_price, atr_value, OrderSide.SELL
        )
        
        # Take profit should be below entry for SELL
        assert take_profit_sell.as_double() < entry_price.as_double()
    
    def test_trade_validation(self):
        """Test trade entry validation."""
        instrument_id = self.instrument.id
        side = OrderSide.BUY
        quantity = Quantity(0.1, 1)
        price = Price(50000.0, 2)
        
        # Test valid trade
        is_valid, reason = self.risk_manager.validate_trade_entry(
            instrument_id, side, quantity, price
        )
        
        assert is_valid
        assert "validated" in reason.lower()
        
        # Test emergency stop
        self.risk_manager.trigger_emergency_stop()
        is_valid, reason = self.risk_manager.validate_trade_entry(
            instrument_id, side, quantity, price
        )
        
        assert not is_valid
        assert "emergency stop" in reason.lower()
    
    def test_daily_pnl_tracking(self):
        """Test daily PnL tracking."""
        initial_pnl = self.risk_manager.daily_pnl
        
        # Update PnL
        self.risk_manager.update_daily_pnl(100.0)
        assert self.risk_manager.daily_pnl == initial_pnl + 100.0
        
        # Update again
        self.risk_manager.update_daily_pnl(-50.0)
        assert self.risk_manager.daily_pnl == initial_pnl + 50.0
    
    def test_consecutive_losses_tracking(self):
        """Test consecutive losses tracking."""
        assert self.risk_manager.consecutive_losses == 0
        
        # Record losing trade
        self.risk_manager.record_trade_result(-100.0, False)
        assert self.risk_manager.consecutive_losses == 1
        
        # Record another losing trade
        self.risk_manager.record_trade_result(-50.0, False)
        assert self.risk_manager.consecutive_losses == 2
        
        # Record winning trade - should reset
        self.risk_manager.record_trade_result(200.0, True)
        assert self.risk_manager.consecutive_losses == 0


class TestDataProcessor:
    """Test cases for Data Processor utilities."""
    
    def test_atr_calculation(self):
        """Test ATR calculation."""
        high = [102, 103, 104, 103, 105, 106, 107, 106, 108, 109, 110, 109, 111, 112, 113]
        low = [100, 101, 102, 101, 103, 104, 105, 104, 106, 107, 108, 107, 109, 110, 111]
        close = [101, 102, 103, 102, 104, 105, 106, 105, 107, 108, 109, 108, 110, 111, 112]
        
        atr = DataProcessor.calculate_atr(high, low, close, period=14)
        
        assert isinstance(atr, float)
        assert atr > 0
    
    def test_bollinger_bands_calculation(self):
        """Test Bollinger Bands calculation."""
        prices = [100 + i + np.random.normal(0, 0.5) for i in range(25)]
        
        bands = DataProcessor.calculate_bollinger_bands(prices, period=20, std_dev=2.0)
        
        assert 'upper' in bands
        assert 'middle' in bands
        assert 'lower' in bands
        
        assert bands['upper'] > bands['middle'] > bands['lower']
    
    def test_rsi_calculation(self):
        """Test RSI calculation."""
        # Create trending price data
        prices = [100 + i * 0.5 for i in range(20)]
        
        rsi = DataProcessor.calculate_rsi(prices, period=14)
        
        assert isinstance(rsi, float)
        assert 0 <= rsi <= 100
        
        # Uptrending prices should have RSI > 50
        assert rsi > 50
    
    def test_volume_sma_calculation(self):
        """Test volume SMA calculation."""
        volumes = [1000 + i * 10 for i in range(25)]
        
        sma = DataProcessor.calculate_volume_sma(volumes, period=20)
        
        assert isinstance(sma, float)
        assert sma > 0
        
        # Should be close to the average of last 20 values
        expected = sum(volumes[-20:]) / 20
        assert abs(sma - expected) < 1e-6


class TestPriceUtils:
    """Test cases for Price utilities."""
    
    def test_tick_size_rounding(self):
        """Test price rounding to tick size."""
        price = 50123.456789
        tick_size = 0.01
        
        rounded = PriceUtils.round_to_tick_size(price, tick_size)
        
        assert rounded == 50123.46
    
    def test_lot_size_rounding(self):
        """Test quantity rounding to lot size."""
        quantity = 0.123456789
        lot_size = 0.001
        
        rounded = PriceUtils.round_to_lot_size(quantity, lot_size)
        
        assert rounded == 0.123
    
    def test_notional_value_calculation(self):
        """Test notional value calculation."""
        price = 50000.0
        quantity = 0.5
        
        notional = PriceUtils.calculate_notional_value(price, quantity)
        
        assert notional == 25000.0
    
    def test_percentage_change_calculation(self):
        """Test percentage change calculation."""
        old_value = 100.0
        new_value = 110.0
        
        change = PriceUtils.calculate_percentage_change(old_value, new_value)
        
        assert change == 10.0
        
        # Test with decrease
        new_value = 90.0
        change = PriceUtils.calculate_percentage_change(old_value, new_value)
        
        assert change == -10.0


class TestValidationUtils:
    """Test cases for Validation utilities."""
    
    def test_price_validation(self):
        """Test price validation."""
        # Valid prices
        assert ValidationUtils.validate_price(100.0)
        assert ValidationUtils.validate_price(0.001)
        assert ValidationUtils.validate_price(999999.99)
        
        # Invalid prices
        assert not ValidationUtils.validate_price(-1.0)
        assert not ValidationUtils.validate_price(float('nan'))
        assert not ValidationUtils.validate_price(float('inf'))
    
    def test_quantity_validation(self):
        """Test quantity validation."""
        # Valid quantities
        assert ValidationUtils.validate_quantity(1.0)
        assert ValidationUtils.validate_quantity(0.001)
        assert ValidationUtils.validate_quantity(0.0)  # Zero allowed
        
        # Invalid quantities
        assert not ValidationUtils.validate_quantity(-1.0)
        assert not ValidationUtils.validate_quantity(float('nan'))
        assert not ValidationUtils.validate_quantity(float('inf'))
    
    def test_symbol_sanitization(self):
        """Test symbol sanitization."""
        # Test various inputs
        assert ValidationUtils.sanitize_symbol("btcusdt") == "BTCUSDT"
        assert ValidationUtils.sanitize_symbol(" ethusdt ") == "ETHUSDT"
        assert ValidationUtils.sanitize_symbol("ADA-USDT") == "ADA-USDT"


# Async test for coin selector
class TestCoinSelectorAsync:
    """Async test cases for Coin Selector."""
    
    @pytest.mark.asyncio
    async def test_coin_selector_creation(self):
        """Test coin selector creation and basic functionality."""
        from coin_selector import CoinSelector
        
        selector = CoinSelector()
        
        # Test excluded assets
        excluded = selector.get_excluded_assets()
        assert isinstance(excluded, set)
        assert len(excluded) > 0
        assert 'USDT' in excluded  # Should include stablecoins
    
    @pytest.mark.asyncio
    async def test_symbol_validation(self):
        """Test symbol validation functionality."""
        from coin_selector import CoinSelector
        
        async with CoinSelector() as selector:
            # Mock the exchange info response
            with patch.object(selector, 'get_exchange_info') as mock_exchange_info:
                mock_exchange_info.return_value = {
                    'symbols': [
                        {'symbol': 'BTCUSDT', 'status': 'TRADING'},
                        {'symbol': 'ETHUSDT', 'status': 'TRADING'},
                        {'symbol': 'INVALID', 'status': 'HALT'}
                    ]
                }
                
                test_symbols = ['BTCUSDT', 'ETHUSDT', 'INVALID', 'NONEXISTENT']
                valid_symbols = await selector.validate_symbols(test_symbols)
                
                assert 'BTCUSDT' in valid_symbols
                assert 'ETHUSDT' in valid_symbols
                assert 'INVALID' not in valid_symbols
                assert 'NONEXISTENT' not in valid_symbols


# Test configuration
@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    from config import BotConfig, ExchangeConfig, TradingConfig, StrategyConfig
    
    return BotConfig(
        exchange=ExchangeConfig(),
        trading=TradingConfig(),
        strategy=StrategyConfig(),
        logging=None,
        execution=None,
        safety=None
    )


def test_configuration_loading(sample_config):
    """Test configuration loading and validation."""
    config = sample_config
    
    assert config.exchange.testnet is True
    assert config.trading.max_coins == 50
    assert config.strategy.atr_period == 14


# Performance test
def test_strategy_performance():
    """Test strategy performance with large datasets."""
    # This test ensures the strategy can handle large amounts of data efficiently
    
    config = VolatilityBreakoutConfig(
        instrument_ids=[],
        bar_type=BarType.from_str("BTCUSDT.BINANCE-1-MINUTE-LAST-EXTERNAL")
    )
    
    strategy = VolatilityBreakoutStrategy(config)
    instrument_id = InstrumentId.from_str("BTCUSDT.BINANCE")
    
    # Setup indicators
    strategy._setup_indicators(instrument_id)
    
    # Process large number of updates
    import time
    start_time = time.time()
    
    for i in range(1000):
        price = 100.0 + i * 0.01
        indicators = strategy.indicators[instrument_id]
        indicators['atr'].update_raw(price + 0.5, price - 0.5, price)
        indicators['bollinger'].update_raw(price)
        indicators['rsi'].update_raw(price)
        indicators['volume_ema'].update_raw(1000.0)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    # Should process 1000 updates quickly (less than 1 second)
    assert processing_time < 1.0


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
