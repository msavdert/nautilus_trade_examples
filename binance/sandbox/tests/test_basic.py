"""
Basic tests for Binance Spot Trading Client
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config
from client import BinanceClient, BinanceAPIError
from strategy import SimpleBuyHoldStrategy, MarketData


class TestConfig:
    """Test configuration management"""
    
    def test_config_creation(self):
        """Test basic config creation"""
        # This will use environment variables or defaults
        config = Config(
            binance_api_key="test_key",
            binance_secret_key="test_secret"
        )
        
        assert config.binance_api_key == "test_key"
        assert config.binance_secret_key == "test_secret"
        assert config.testnet is True  # Default value
        assert config.log_level == "INFO"  # Default value
    
    def test_config_validation(self):
        """Test config validation"""
        with pytest.raises(ValueError):
            Config(
                binance_api_key="test",
                binance_secret_key="test",
                log_level="INVALID"
            )
    
    def test_base_url_property(self):
        """Test base URL property"""
        config = Config(
            binance_api_key="test",
            binance_secret_key="test",
            testnet=True
        )
        assert "testnet" in config.base_url
        
        config.testnet = False
        assert "api.binance.com" in config.base_url
    
    def test_symbols_list_property(self):
        """Test symbols list parsing"""
        config = Config(
            binance_api_key="test",
            binance_secret_key="test",
            default_symbols="BTCUSDT,ETHUSDT,ADAUSDT"
        )
        
        symbols = config.symbols_list
        assert symbols == ["BTCUSDT", "ETHUSDT", "ADAUSDT"]


class TestBinanceClient:
    """Test Binance API client"""
    
    @pytest.fixture
    def config(self):
        """Test configuration fixture"""
        return Config(
            binance_api_key="test_key",
            binance_secret_key="test_secret",
            testnet=True
        )
    
    @pytest.fixture
    def client(self, config):
        """Test client fixture"""
        return BinanceClient(config)
    
    def test_client_initialization(self, client):
        """Test client initialization"""
        assert client.config is not None
        assert client._session is None
        assert len(client._ws_connections) == 0
        assert client._running is False
    
    def test_signature_generation(self, client):
        """Test HMAC signature generation"""
        params = {"symbol": "BTCUSDT", "side": "BUY", "timestamp": 1234567890}
        signature = client._generate_signature(params)
        
        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA256 hex string length
    
    @pytest.mark.asyncio
    async def test_context_manager(self, client):
        """Test async context manager"""
        async with client as c:
            assert c._session is not None
            assert c._running is True
        
        # After context exit
        assert client._session is None
        assert client._running is False
    
    @pytest.mark.asyncio
    async def test_start_stop(self, client):
        """Test manual start/stop"""
        await client.start()
        assert client._session is not None
        assert client._running is True
        
        await client.stop()
        assert client._session is None
        assert client._running is False


class TestStrategy:
    """Test strategy implementations"""
    
    @pytest.fixture
    def config(self):
        """Test configuration fixture"""
        return Config(
            binance_api_key="test_key",
            binance_secret_key="test_secret",
            strategy_enabled=True,
            max_position_size_percent=5.0
        )
    
    @pytest.fixture
    def mock_client(self, config):
        """Mock client fixture"""
        client = Mock(spec=BinanceClient)
        client.config = config
        client.place_order = AsyncMock()
        return client
    
    @pytest.fixture
    def strategy(self, config, mock_client):
        """Strategy fixture"""
        return SimpleBuyHoldStrategy(config, mock_client)
    
    @pytest.mark.asyncio
    async def test_strategy_initialization(self, strategy):
        """Test strategy initialization"""
        assert strategy.config is not None
        assert strategy.client is not None
        assert len(strategy.positions) == 0
        assert strategy.is_running is False
    
    @pytest.mark.asyncio
    async def test_strategy_start_stop(self, strategy):
        """Test strategy start/stop"""
        await strategy.start()
        assert strategy.is_running is True
        
        await strategy.stop()
        assert strategy.is_running is False
    
    @pytest.mark.asyncio
    async def test_market_data_handling(self, strategy):
        """Test market data handling"""
        await strategy.start()
        
        # Create test market data
        market_data = MarketData(
            symbol="BTCUSDT",
            price=50000.0,
            volume=100.0,
            timestamp=None
        )
        
        # This should not raise an exception
        await strategy.on_market_data(market_data)
        
        # Test with price drop
        market_data2 = MarketData(
            symbol="BTCUSDT",
            price=49000.0,  # 2% drop
            volume=100.0,
            timestamp=None
        )
        
        await strategy.on_market_data(market_data2)
    
    def test_position_size_calculation(self, strategy):
        """Test position size calculation"""
        size = strategy.calculate_position_size("BTCUSDT", 50000.0)
        assert isinstance(size, float)
        assert size > 0
    
    def test_risk_management(self, strategy):
        """Test basic risk management"""
        should_allow = strategy.should_place_order("BTCUSDT", "BUY", 0.001)
        assert isinstance(should_allow, bool)


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """Test full workflow with mocked API"""
        config = Config(
            binance_api_key="test_key",
            binance_secret_key="test_secret",
            testnet=True
        )
        
        with patch('aiohttp.ClientSession') as mock_session:
            # Mock successful API responses
            mock_response = AsyncMock()
            mock_response.json.return_value = {"serverTime": 1234567890}
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            client = BinanceClient(config)
            
            async with client:
                # Test API call
                result = await client.get_server_time()
                assert "serverTime" in result


# Test fixtures for pytest
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests with: python -m pytest tests/test_basic.py -v
    pytest.main([__file__, "-v"])
