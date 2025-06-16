# Binance Spot Trading Client

🚀 **A minimal, modular, and fully dockerized Binance Spot trading client inspired by Nautilus Trader's architecture.**

This project provides a clean foundation for algorithmic trading with proper separation of concerns and Docker-first development approach.

## 🌟 Features

- **🐳 Fully Dockerized**: All development, testing, and production operations via Docker containers
- **📦 Modular Architecture**: Clean separation of config, client, strategy, and testing modules  
- **🔧 Environment-Based Configuration**: All secrets and settings managed via `.env` files
- **🎯 Multi-Environment Support**: Development, testing, and production Docker targets
- **📡 Complete Binance Integration**: WebSocket & REST API with latest endpoints
- **🧠 Strategy Framework**: Extensible strategy base classes with built-in examples
- **🧪 Comprehensive Testing**: Unit tests and integration test framework
- **💚 Health Monitoring**: Docker health checks and application monitoring
- **🛡️ Risk Management**: Position sizing, stop-loss, and risk controls

## 🏗️ Architecture

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

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone or navigate to the project directory
cd binance/sandbox

# Copy environment template
cp .env.example .env

# Edit your configuration (add your Binance API credentials)
nano .env
```

### 2. Essential Configuration

Edit your `.env` file with your Binance API credentials:

```bash
# Required API Credentials
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

# Safety Settings (IMPORTANT!)
ENVIRONMENT=sandbox
TESTNET=true
STRATEGY_ENABLED=false  # Start with false for safety

# Trading Configuration
DEFAULT_SYMBOLS=BTCUSDT,ETHUSDT,ADAUSDT
MAX_POSITION_SIZE_PERCENT=10.0
STOP_LOSS_PERCENT=2.0
```

### 3. Development Environment

```bash
# Build all Docker images
make build
# or: docker-compose build

# Start development environment
make dev
# or: docker-compose up binance-dev

# Access development shell
make dev-shell
# or: docker-compose exec binance-dev bash
```

### 4. Testing

```bash
# Run all tests
make test
# or: docker-compose up binance-test

# Run tests with coverage
make test-cov

# Run specific tests
docker-compose run --rm binance-test python -m pytest tests/test_basic.py -v
```

### 5. Production

```bash
# Start trading client
make prod
# or: docker-compose up binance-client

# Start in background
make prod-daemon
# or: docker-compose up -d binance-client

# Monitor logs
make prod-logs
# or: docker-compose logs -f binance-client
```

## 📡 API Integration

This client uses the latest Binance Spot API endpoints (as of 2024):

### Endpoints
- **Testnet**: `https://testnet.binance.vision`
- **Production**: `https://api.binance.com`
- **WebSocket Testnet**: `wss://testnet.binance.vision`
- **WebSocket Production**: `wss://stream.binance.com:9443`

### Supported Features
- ✅ Market data (ticker, orderbook, klines)
- ✅ Account information
- ✅ Order management (place, cancel, query)
- ✅ WebSocket streams (real-time data)
- ✅ Authentication with HMAC-SHA256
- ✅ Rate limiting and error handling

## 🎯 Strategy Development

### Creating Custom Strategies

```python
from src.strategy import BaseStrategy, MarketData

class MyStrategy(BaseStrategy):
    async def on_market_data(self, data: MarketData):
        # Your trading logic here
        if self.should_buy(data):
            await self.place_order(
                symbol=data.symbol,
                side="BUY", 
                quantity=self.calculate_position_size(data.symbol, data.price)
            )
    
    async def on_order_update(self, order_data):
        # Handle order status updates
        pass
```

### Built-in Strategies

- **SimpleBuyHoldStrategy**: Buys on price drops, holds positions
- **ScalpingStrategy**: Demo scalping strategy (educational only)

## 🛡️ Safety & Risk Management

### ⚠️ Critical Safety Notes

1. **Always use TESTNET first**: Set `TESTNET=true` in `.env`
2. **Start with strategy disabled**: Set `STRATEGY_ENABLED=false`  
3. **Use small position sizes**: Start with minimal amounts
4. **Monitor continuously**: Never leave strategies unattended
5. **Paper trade extensively**: Test all logic before live trading

### Risk Controls

- Position size limits as percentage of balance
- Stop-loss and take-profit levels
- Daily loss limits
- Rate limiting for API calls

## 🧪 Testing Framework

### Test Structure
```bash
tests/
├── test_basic.py       # Core functionality tests
└── test_integration.py # End-to-end workflow tests
```

### Running Tests
```bash
# All tests
make test

# Specific test categories  
docker-compose run --rm binance-test python -m pytest tests/test_basic.py::TestConfig -v

# With coverage report
make test-cov

# Debug mode
docker-compose run --rm binance-test python -m pytest --pdb
```

## 📊 Monitoring & Logging

### Log Management
- Container logs: `docker-compose logs -f`
- Application logs: `./logs/trading_client.log`
- Structured logging with configurable levels

### Health Checks
```bash
# Check container health
make health

# Monitor resource usage  
docker stats binance_client

# Application status
docker inspect --format='{{.State.Health.Status}}' binance_client
```

## 🔧 Docker Commands Reference

### Development Workflow
```bash
make dev           # Start development environment
make dev-shell     # Access development shell  
make dev-logs      # View development logs
```

### Testing Workflow
```bash
make test          # Run all tests
make test-unit     # Run unit tests only
make test-cov      # Run with coverage
make test-debug    # Debug test failures
```

### Production Workflow  
```bash
make prod          # Start production client
make prod-daemon   # Start in background
make prod-logs     # View production logs
make prod-stop     # Stop gracefully
```

### Maintenance
```bash
make clean         # Clean containers and volumes
make format        # Format code with black
make lint          # Lint with flake8
make syntax-check  # Validate Python syntax
```

## 📈 Development Roadmap

### Phase 1: Foundation (✅ Complete)
- [x] Docker infrastructure
- [x] Binance API integration
- [x] Basic strategy framework
- [x] Testing infrastructure
- [x] Documentation

### Phase 2: Enhancement (Next Steps)
- [ ] Advanced risk management
- [ ] Performance analytics  
- [ ] Database integration
- [ ] Real-time dashboards
- [ ] Alert systems

### Phase 3: Advanced Features
- [ ] Machine learning integration
- [ ] Multi-exchange support
- [ ] Portfolio optimization
- [ ] Backtesting framework

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## 📚 Resources

- [Binance Spot API Docs](https://github.com/binance/binance-spot-api-docs)
- [Nautilus Trader](https://github.com/nautechsystems/nautilus_trader)
- [Docker Documentation](https://docs.docker.com/)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)

## ⚖️ Disclaimer

**This software is for educational and research purposes only.** Cryptocurrency trading involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred through the use of this software.

**Always test thoroughly on testnet before any live trading.**

## 📄 License

This project is open source and available under the MIT License.

---

**🎉 Ready to start algorithmic trading? Begin with `make setup` and `make dev`!**

For Turkish documentation, see [README.tr.md](README.tr.md)
