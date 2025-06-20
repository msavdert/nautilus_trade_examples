"""
Tests for utility modules including coin selector and risk manager.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from utils.coin_selector import CoinSelector, CoinInfo
from utils.risk_manager import RiskManager, RiskMetrics
from config import get_config


class TestCoinSelector:
    """Test suite for CoinSelector."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = get_config()
        self.coin_selector = CoinSelector(self.config)
    
    def test_coin_selector_initialization(self):
        """Test coin selector initialization."""
        assert self.coin_selector.config == self.config
        assert self.coin_selector.base_url == self.config.endpoints.futures_api_url
        assert len(self.coin_selector.excluded_coins) > 0
    
    def test_valid_symbol_filtering(self):
        """Test symbol validation logic."""
        # Valid symbols
        assert self.coin_selector._is_valid_symbol("BTCUSDT")
        assert self.coin_selector._is_valid_symbol("ETHUSDT")
        assert self.coin_selector._is_valid_symbol("ADAUSDT")
        
        # Invalid symbols
        assert not self.coin_selector._is_valid_symbol("BTCEUR")  # Not USDT
        assert not self.coin_selector._is_valid_symbol("USDCUSDT")  # Excluded
        assert not self.coin_selector._is_valid_symbol("BTCUP")  # Leveraged token
        assert not self.coin_selector._is_valid_symbol("ETHDOWN")  # Leveraged token
    
    @pytest.mark.asyncio
    async def test_fetch_coin_data_mock(self):
        """Test fetching coin data with mocked API responses."""
        # Mock API responses
        mock_exchange_info = {
            "symbols": [
                {
                    "symbol": "BTCUSDT",
                    "status": "TRADING",
                    "filters": [
                        {"filterType": "MIN_NOTIONAL", "notional": "10.0"},
                        {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                        {"filterType": "LOT_SIZE", "stepSize": "0.000001"}
                    ]
                },
                {
                    "symbol": "ETHUSDT", 
                    "status": "TRADING",
                    "filters": [
                        {"filterType": "MIN_NOTIONAL", "notional": "10.0"},
                        {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                        {"filterType": "LOT_SIZE", "stepSize": "0.000001"}
                    ]
                }
            ]
        }
        
        mock_ticker_stats = [
            {
                "symbol": "BTCUSDT",
                "lastPrice": "50000.0",
                "quoteVolume": "1000000000.0",
                "priceChangePercent": "2.5"
            },
            {
                "symbol": "ETHUSDT",
                "lastPrice": "3000.0", 
                "quoteVolume": "500000000.0",
                "priceChangePercent": "-1.2"
            }
        ]
        
        with patch.object(self.coin_selector, '_fetch_futures_exchange_info') as mock_exchange:
            with patch.object(self.coin_selector, '_fetch_24h_ticker_stats') as mock_ticker:
                mock_exchange.return_value = mock_exchange_info
                mock_ticker.return_value = mock_ticker_stats
                
                coin_data = await self.coin_selector._fetch_coin_data()
                
                assert len(coin_data) == 2
                assert "BTCUSDT" in coin_data
                assert "ETHUSDT" in coin_data
                
                btc_info = coin_data["BTCUSDT"]
                assert btc_info.symbol == "BTCUSDT"
                assert btc_info.price == 50000.0
                assert btc_info.volume_24h == 1000000000.0
    
    def test_coin_info_creation(self):
        """Test CoinInfo data class."""
        coin_info = CoinInfo(
            symbol="BTCUSDT",
            base_asset="BTC",
            quote_asset="USDT",
            volume_24h=1000000000.0,
            price=50000.0,
            price_change_24h=2.5,
            is_futures_enabled=True,
            min_notional=10.0,
            tick_size=0.01,
            step_size=0.000001
        )
        
        assert coin_info.symbol == "BTCUSDT"
        assert coin_info.base_asset == "BTC"
        assert coin_info.volume_24h == 1000000000.0
        assert coin_info.is_futures_enabled


class TestRiskManager:
    """Test suite for RiskManager."""
    
    def setup_method(self):
        """Setup test environment."""
        self.config = get_config()
        self.risk_manager = RiskManager(self.config)
    
    def test_risk_manager_initialization(self):
        """Test risk manager initialization."""
        assert self.risk_manager.config == self.config
        assert self.risk_manager.daily_trades == 0
        assert self.risk_manager.daily_realized_pnl == 0.0
        assert not self.risk_manager.emergency_stop_active
    
    def test_session_initialization(self):
        """Test session initialization."""
        # Mock portfolio
        mock_portfolio = Mock()
        mock_account = Mock()
        mock_account.balance.return_value = Mock()
        mock_account.balance.return_value.as_double.return_value = 10000.0
        
        mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
        
        # Initialize session
        self.risk_manager.initialize_session(mock_portfolio)
        
        assert self.risk_manager.session_start_balance == 10000.0
        assert self.risk_manager.peak_balance == 10000.0
    
    def test_position_approval_logic(self):
        """Test position approval logic."""
        # Mock portfolio
        mock_portfolio = Mock()
        mock_account = Mock()
        mock_account.balance.return_value = Mock()
        mock_account.balance.return_value.as_double.return_value = 10000.0
        
        mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
        mock_portfolio.positions_open.return_value = []
        mock_portfolio.position_for_instrument.return_value = None  # No existing position
        
        from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
        from nautilus_trader.model.enums import OrderSide
        
        instrument_id = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
        
        # Test normal position approval
        can_open, reason = self.risk_manager.can_open_position(
            mock_portfolio, instrument_id, OrderSide.BUY, 500.0
        )
        
        assert can_open, f"Position approval failed: {reason}"
        assert "approved" in reason.lower()
        
        # Test emergency stop
        self.risk_manager.emergency_stop_active = True
        can_open, reason = self.risk_manager.can_open_position(
            mock_portfolio, instrument_id, OrderSide.BUY, 500.0
        )
        
        assert not can_open
        assert "emergency" in reason.lower()
    
    def test_position_size_calculation(self):
        """Test position size calculation."""
        # Mock portfolio and instrument
        mock_portfolio = Mock()
        mock_account = Mock()
        mock_account.balance.return_value = Mock()
        mock_account.balance.return_value.as_double.return_value = 10000.0
        
        mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
        
        from nautilus_trader.model.instruments import CurrencyPair
        from nautilus_trader.model.identifiers import InstrumentId, Symbol, Venue
        from nautilus_trader.model.objects import Price, Quantity
        from nautilus_trader.model.currencies import USD, BTC
        
        instrument_id = InstrumentId(Symbol("BTCUSDT"), Venue("BINANCE"))
        instrument = Mock()
        instrument.id = instrument_id
        instrument.size_precision = 6
        
        price = Price.from_str("50000.00")
        
        # Calculate position size
        quantity = self.risk_manager.calculate_position_size(
            mock_portfolio, instrument, price, volatility=0.02
        )
        
        # Should return some quantity based on risk parameters
        assert quantity.as_double() > 0
    
    def test_stop_loss_take_profit_calculation(self):
        """Test stop loss and take profit calculation."""
        from nautilus_trader.model.enums import OrderSide
        
        entry_price = 50000.0
        
        # Test long position
        stop_loss, take_profit = self.risk_manager.calculate_stop_loss_take_profit(
            entry_price, OrderSide.BUY, volatility=0.02
        )
        
        assert stop_loss < entry_price  # Stop loss should be below entry for long
        assert take_profit > entry_price  # Take profit should be above entry for long
        
        # Test short position
        stop_loss, take_profit = self.risk_manager.calculate_stop_loss_take_profit(
            entry_price, OrderSide.SELL, volatility=0.02
        )
        
        assert stop_loss > entry_price  # Stop loss should be above entry for short
        assert take_profit < entry_price  # Take profit should be below entry for short
    
    def test_risk_metrics_calculation(self):
        """Test risk metrics calculation."""
        # Mock portfolio with some data
        mock_portfolio = Mock()
        mock_account = Mock()
        mock_account.balance.return_value = Mock()
        mock_account.balance.return_value.as_double.return_value = 9500.0  # Some loss
        
        mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
        mock_portfolio.positions_open.return_value = []
        
        # Initialize session first
        self.risk_manager.session_start_balance = 10000.0
        self.risk_manager.peak_balance = 10000.0
        
        # Calculate metrics
        metrics = self.risk_manager.get_risk_metrics(mock_portfolio)
        
        assert isinstance(metrics, RiskMetrics)
        assert metrics.total_exposure >= 0
        assert metrics.active_positions == 0
        assert metrics.drawdown_pct >= 0
    
    def test_risk_limit_checking(self):
        """Test risk limit checking."""
        # Mock portfolio with loss
        mock_portfolio = Mock()
        mock_account = Mock()
        mock_account.balance.return_value = Mock()
        mock_account.balance.return_value.as_double.return_value = 8000.0  # 20% loss
        
        mock_portfolio.accounts.return_value = {"BINANCE": mock_account}
        mock_portfolio.positions_open.return_value = []
        
        # Set starting balances
        self.risk_manager.daily_start_balance = 10000.0
        self.risk_manager.session_start_balance = 10000.0
        self.risk_manager.peak_balance = 10000.0
        
        # Check risk limits
        violations = self.risk_manager.check_risk_limits(mock_portfolio)
        
        # Should detect violations due to significant loss
        assert len(violations) > 0
        assert any("loss" in v.lower() or "drawdown" in v.lower() for v in violations)
    
    def test_emergency_stop_activation(self):
        """Test emergency stop activation."""
        assert not self.risk_manager.emergency_stop_active
        
        self.risk_manager.emergency_stop()
        
        assert self.risk_manager.emergency_stop_active
        
        # Test reset
        self.risk_manager.reset_emergency_stop()
        
        assert not self.risk_manager.emergency_stop_active


class TestUtilityFunctions:
    """Test utility functions."""
    
    def test_data_utils(self):
        """Test data utility functions."""
        from utils import DataUtils
        
        # Test safe conversions
        assert DataUtils.safe_float("123.45") == 123.45
        assert DataUtils.safe_float("invalid", 0.0) == 0.0
        assert DataUtils.safe_int("123") == 123
        assert DataUtils.safe_int("invalid", 0) == 0
        
        # Test formatting
        assert DataUtils.format_currency(1000.0) == "$1.00K"
        assert DataUtils.format_currency(1_000_000.0) == "$1.00M"
        assert DataUtils.format_percentage(0.1234) == "12.34%"
    
    def test_math_utils(self):
        """Test mathematical utility functions."""
        from utils import MathUtils
        
        # Test volatility calculation
        returns = [0.01, -0.02, 0.015, -0.01, 0.005] * 5  # 25 returns
        volatility = MathUtils.calculate_volatility(returns, window=20)
        assert volatility > 0
        
        # Test Sharpe ratio
        sharpe = MathUtils.calculate_sharpe_ratio(returns)
        assert isinstance(sharpe, float)
        
        # Test max drawdown
        equity_curve = [1000, 1100, 1050, 1200, 1150, 1300, 1200, 1400]
        max_dd = MathUtils.calculate_max_drawdown(equity_curve)
        assert 0 <= max_dd <= 1  # Should be between 0 and 100%
    
    def test_performance_tracker(self):
        """Test performance tracking."""
        from utils import PerformanceTracker
        
        tracker = PerformanceTracker()
        
        # Add some trades
        entry_time = datetime.now()
        exit_time = entry_time + timedelta(hours=2)
        
        tracker.add_trade(
            instrument="BTCUSDT",
            side="BUY",
            entry_price=50000.0,
            exit_price=51000.0,  # Winning trade
            quantity=0.1,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        tracker.add_trade(
            instrument="ETHUSDT",
            side="SELL",
            entry_price=3000.0,
            exit_price=3100.0,  # Losing trade for short
            quantity=1.0,
            entry_time=entry_time,
            exit_time=exit_time
        )
        
        # Get statistics
        stats = tracker.get_stats()
        
        assert stats.total_trades == 2
        assert stats.winning_trades == 1
        assert stats.losing_trades == 1
        assert stats.win_rate == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
