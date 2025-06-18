# Nautilus Trader Examples

A project for developing trading bots with Nautilus Trader across different exchanges and strategies.

> **⚠️ Important**: All commands in this project must be run using `docker exec` inside the Docker container. This ensures proper environment setup and dependency management.

## 📋 Project Structure

```
nautilus_trade_examples/
├── bots/                           # Trading bots
│   ├── my-first-bot/               # Complete beginner tutorial bot
│   └── backtest-bot/               # Learn backtesting and strategy validation
├── docker-compose.yml              # Nautilus Trader container
├── README.md                       # This file
└── logs/                           # Application logs
```

## 🚀 Quick Start

This project allows you to develop your own trading bots from scratch using Nautilus Trader in a containerized environment.

> **📝 Note**: All development happens inside Docker containers. This ensures consistent environment and proper dependency management.

### 1. Start the Container
```bash
docker-compose up -d
```
This starts both Redis cache and Nautilus Trader containers.

### 2. Create Your First Bot
```bash
# All commands use docker exec to run inside the container
docker exec -it nautilus-trader bash -c "cd /workspace/bots/ && uv init my-first-bot"
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv add nautilus_trader"
```

### 3. Test Your Setup
```bash
# Verify everything works
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv run python main.py"
```

### 4. Connect to Container (Optional)
For interactive development:
```bash
docker exec -it nautilus-trader bash
# Now you're inside the container and can run commands directly
```

### 4. Develop Your Bot
After creating your first bot, you can:
- Navigate to `bots/my-first-bot/` in your editor
- Follow the complete tutorial in the bot's README
- Learn how to write trading bots from scratch

## 🤖 Available Bots

### 1. [My First Bot](bots/my-first-bot/)
**Perfect for absolute beginners**
- Complete step-by-step tutorial
- Simple moving average strategy
- Detailed explanations of every concept
- Single-file implementation

### 2. [Backtest Bot](bots/backtest-bot/)
**Learn strategy testing and validation**
- Comprehensive backtesting guide
- Synthetic data generation
- Performance analysis tools
- Real data integration examples

## 🛠️ Development Workflow

1. **Initialize**: Use the commands above to create your first bot
2. **Learn**: Follow the [My First Bot](bots/my-first-bot/) tutorial
3. **Test**: Learn backtesting with [Backtest Bot](bots/backtest-bot/)
4. **Develop**: Write your own trading strategies
5. **Validate**: Test thoroughly before live trading

## ⚠️ Important Notes

- **Security**: Never commit your API keys to git
- **Testing**: Always use testnet before live trading
- **Risk Management**: Always use stop-loss and position sizing
- **Learning**: Start with small amounts and learn step by step

## 🔗 Useful Links

- [Nautilus Trader Docs](https://nautilustrader.io/)
- [Binance API Docs](https://developers.binance.com/)
- [Binance Testnet](https://testnet.binance.vision/)

---

## 🔧 Redis Setup

Redis is included in the Docker setup for market data caching and is automatically configured.

### Adding Redis to Your Bot (Optional)

The Redis **server** is already running in Docker. If you want to use Redis directly in your bot code, you need to add the Python Redis client:

```bash
# Enter your bot directory
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv add redis"
```

Or if you're already inside the container:
```bash
cd /workspace/bots/my-first-bot
uv add redis
```

### When Do You Need Redis Package?

✅ **Redis package REQUIRED:**
- Custom caching logic in your bot
- Direct Redis data access
- Running test scripts that use Redis

❌ **Redis package NOT REQUIRED:**
- Basic Nautilus Trader usage
- Simple trading strategies

> **Note:** Redis **server** is already running in Docker. `uv add redis` is only needed for Python code to connect to Redis.

### Redis Connection Details
- **Host**: `redis` (from container) or `localhost` (from host)
- **Port**: `6379`
- **Database**: `0` (default)

### Redis Management
```bash
# Connect to Redis CLI
docker exec -it redis-server redis-cli

# Check Redis status
docker exec -it redis-server redis-cli ping

# Monitor Redis commands
docker exec -it redis-server redis-cli monitor
```

### Redis Data Persistence
Redis data is persisted in Docker volumes and will be retained between container restarts.

---
**Note**: These projects are for educational purposes. Trading involves risks, use at your own responsibility.
