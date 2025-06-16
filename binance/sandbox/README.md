# Binance Spot Trading Client

A minimal, modular, and fully dockerized Binance Spot trading client inspired by Nautilus Trader's architecture. This project provides a clean foundation for algorithmic trading with proper separation of concerns and Docker-first development.

## Features

- **Fully Dockerized**: All development, testing, and production operations via Docker
- **Modular Architecture**: Separated config, client, strategy, and testing modules
- **Environment-Based Configuration**: All secrets and settings via `.env` files
- **Multiple Environments**: Development, testing, and production Docker targets
- **WebSocket & REST API**: Full Binance Spot API integration
- **Strategy Framework**: Extensible strategy base classes with examples
- **Comprehensive Testing**: Unit tests and integration test framework
- **Health Monitoring**: Docker health checks and application monitoring
- **Risk Management**: Basic position sizing and risk controls

## Architecture

```
src/
├── config.py      # Environment-based configuration management
├── client.py      # Binance REST & WebSocket API client
├── strategy.py    # Strategy framework and implementations
└── main.py        # Main application entry point

tests/
└── test_basic.py  # Unit and integration tests

Docker Services:
├── binance-client # Production trading client
├── binance-dev    # Development environment
└── binance-test   # Testing environment
```

## Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit your API credentials and settings
nano .env
```

### 2. Development

```bash
# Start development environment
docker-compose up binance-dev

# Access development shell
docker-compose exec binance-dev bash

# Install additional dev packages if needed
pip install ipython jupyter
```

### 3. Testing

```bash
# Run all tests
docker-compose up binance-test

# Run specific tests
docker-compose run --rm binance-test python -m pytest tests/test_basic.py -v

# Run tests with coverage
docker-compose run --rm binance-test python -m pytest tests/ --cov=src/
```

### 4. Production

```bash
# Start trading client
docker-compose up binance-client

# View logs
docker-compose logs -f binance-client

# Monitor health
docker-compose ps
```

## Configuration

All configuration is managed through environment variables in `.env`:

### API Credentials
```bash
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
```

### Environment Settings
```bash
ENVIRONMENT=sandbox          # sandbox, testnet, live
TESTNET=true                 # Use testnet endpoints
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
DEBUG=false                 # Enable debug mode
```

### Trading Configuration
```bash
DEFAULT_SYMBOLS=BTCUSDT,ETHUSDT,ADAUSDT
DEFAULT_INTERVALS=1m,5m,1h
STRATEGY_ENABLED=false      # Enable automated trading
STRATEGY_NAME=simple_buy_hold
```

### Risk Management
```bash
MAX_POSITION_SIZE_PERCENT=10.0  # Max position size as % of balance
MAX_DAILY_LOSS_PERCENT=5.0      # Max daily loss as % of balance
STOP_LOSS_PERCENT=2.0           # Stop loss percentage
TAKE_PROFIT_PERCENT=5.0         # Take profit percentage
```

## API Endpoints

This client uses the latest Binance Spot API endpoints:

### REST API Base URLs
- **Testnet**: `https://testnet.binance.vision`
- **Production**: `https://api.binance.com`

### WebSocket Base URLs
- **Testnet**: `wss://testnet.binance.vision`
- **Production**: `wss://stream.binance.com:9443`

### Supported Endpoints

#### Public Market Data
- `/api/v3/time` - Server time
- `/api/v3/exchangeInfo` - Exchange information
- `/api/v3/ticker/24hr` - 24hr ticker statistics
- `/api/v3/depth` - Order book
- `/api/v3/klines` - Kline/Candlestick data

#### Authenticated Trading
- `/api/v3/account` - Account information
- `/api/v3/openOrders` - Open orders
- `/api/v3/order` - Place/cancel orders

#### WebSocket Streams
- `@ticker` - 24hr ticker statistics
- `@kline_1m` - Kline/Candlestick streams
- `@depth` - Order book depth streams

## Strategy Development

### Creating a Custom Strategy

```python
from src.strategy import BaseStrategy, MarketData

class MyCustomStrategy(BaseStrategy):
    async def on_market_data(self, data: MarketData):
        # Implement your trading logic
        if self.should_buy(data):
            await self.place_order(
                symbol=data.symbol,
                side="BUY",
                quantity=self.calculate_position_size(data.symbol, data.price)
            )
    
    async def on_order_update(self, order_data):
        # Handle order status updates
        pass
    
    def should_buy(self, data: MarketData) -> bool:
        # Implement your buy conditions
        return False
```

### Built-in Strategies

#### SimpleBuyHoldStrategy
- Buys on price drops (configurable threshold)
- Holds positions indefinitely
- Good for testing and learning

#### ScalpingStrategy (Demo)
- Short-term price movement detection
- **NOT FOR PRODUCTION USE**
- Educational purposes only

## Testing

### Test Structure
```bash
tests/
├── test_basic.py       # Unit tests for all modules
└── test_integration.py # Integration tests (create as needed)
```

### Running Tests
```bash
# All tests
docker-compose up binance-test

# Specific test file
docker-compose run --rm binance-test python -m pytest tests/test_basic.py

# With coverage
docker-compose run --rm binance-test python -m pytest --cov=src/

# Verbose output
docker-compose run --rm binance-test python -m pytest -v
```

### Test Categories
- **Configuration Tests**: Environment validation
- **Client Tests**: API client functionality
- **Strategy Tests**: Strategy logic and risk management
- **Integration Tests**: Full workflow testing

## Docker Commands

### Development Workflow
```bash
# Start development environment
docker-compose up binance-dev

# Execute commands in dev container
docker-compose exec binance-dev python src/main.py

# Install additional packages
docker-compose exec binance-dev pip install package_name

# Access Python REPL
docker-compose exec binance-dev python
```

### Testing Workflow
```bash
# Run all tests
docker-compose up binance-test

# Debug test failures
docker-compose run --rm binance-test python -m pytest --pdb

# Test with specific markers
docker-compose run --rm binance-test python -m pytest -m "not slow"
```

### Production Workflow
```bash
# Start production client
docker-compose up -d binance-client

# View logs
docker-compose logs -f binance-client

# Check health
curl http://localhost:8080/health  # If health endpoint is exposed

# Stop gracefully
docker-compose stop binance-client
```

## Monitoring and Logging

### Log Files
- Production logs: `./logs/trading_client.log`
- Container logs: `docker-compose logs`

### Health Checks
- Docker health checks via `health.py`
- Application heartbeat logging
- Position and order status monitoring

### Monitoring Integration
```bash
# View real-time logs
docker-compose logs -f binance-client

# Monitor resource usage
docker stats binance_client

# Check application health
docker inspect --format='{{.State.Health.Status}}' binance_client
```

## Security Considerations

1. **API Keys**: Never commit real API keys to version control
2. **Testnet First**: Always test on Binance testnet before live trading
3. **Risk Limits**: Configure appropriate position and loss limits
4. **Container Security**: Non-root user in production containers
5. **Network Isolation**: Docker network isolation for production

## Development Guidelines

### Code Style
```bash
# Format code
docker-compose exec binance-dev black src/ tests/

# Lint code
docker-compose exec binance-dev flake8 src/ tests/

# Type checking
docker-compose exec binance-dev mypy src/
```

### Adding New Features
1. Create feature branch
2. Add tests first (TDD approach)
3. Implement feature
4. Update documentation
5. Test in development environment
6. Test on testnet
7. Create pull request

## Common Issues and Solutions

### API Key Issues
```bash
# Check API key configuration
docker-compose exec binance-dev python -c "from src.config import get_config; print(get_config().binance_api_key[:10])"

# Test API connectivity
docker-compose exec binance-dev python -c "
import asyncio
from src.config import get_config
from src.client import BinanceClient
async def test():
    config = get_config()
    async with BinanceClient(config) as client:
        result = await client.get_server_time()
        print(result)
asyncio.run(test())
"
```

### WebSocket Issues
- Check firewall settings
- Verify network connectivity
- Monitor reconnection attempts in logs

### Strategy Issues
- Enable DEBUG logging
- Use testnet for development
- Start with small position sizes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Update documentation
7. Submit a pull request

## Disclaimer

This software is for educational and research purposes only. Cryptocurrency trading involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred through the use of this software.

**Always test thoroughly on testnet before any live trading.**

## License

This project is open source and available under the MIT License.

## Resources

- [Binance Spot API Documentation](https://github.com/binance/binance-spot-api-docs)
- [Binance Python Connector](https://github.com/binance/binance-connector-python)
- [Nautilus Trader](https://github.com/nautechsystems/nautilus_trader)
- [Docker Documentation](https://docs.docker.com/)
- [pytest Documentation](https://docs.pytest.org/)
