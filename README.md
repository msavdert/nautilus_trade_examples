# Nautilus Trader Examples

A project for developing trading bots with Nautilus Trader across different exchanges and strategies.

## 📋 Project Structure

```
nautilus_trade_examples/
├── docs/                           # Documentation
│   ├── trading-fundamentals.md     # Trading fundamentals
│   ├── risk-management.md          # Risk management
│   ├── LOGGING.md                  # Logging guide
│   └── bot-guides/                 # Bot development guides
│       └── binance-spot-testnet.md # Binance Spot Testnet bot guide
├── bots/                           # Trading bots
│   └── my-first-bot/               # Your first bot (created after setup)
├── docker-compose.yml              # Nautilus Trader container
├── README.md                       # This file (English)
├── README.tr.md                    # Turkish documentation
└── logs/                           # Application logs
```

## 🚀 Quick Start

This project allows you to develop your own trading bots from scratch using Nautilus Trader in a containerized environment.

### 1. Start the Container
```bash
docker-compose up -d
```

### 2. Create Your First Bot
```bash
docker exec -it nautilus-trader bash -c "cd /workspace/bots/ && uv init my-first-bot"
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv add nautilus_trader"
```

### 3. Connect to Container (Optional)
```bash
docker exec -it nautilus-trader bash
```

### 4. Develop Your Bot
After creating your first bot, you can:
- Navigate to `bots/my-first-bot/` in your editor
- Follow the step-by-step documentation in `docs/` folder
- Learn how to write trading bots from scratch with Nautilus

## 📚 Documentation

After creating your first bot, you can follow our step-by-step beginner guides:

### 🎯 Start Here: Your First Bot
- **[My First Bot - Complete Beginner Guide](docs/bot-guides/my-first-bot.md)** - Learn to build a simple moving average trading bot from scratch

### 📚 Additional Documentation
- How to write trading bots with Nautilus from scratch
- Step-by-step bot development guides  
- Best practices and examples

## 🛠️ Development Workflow

1. **Initialize**: Use the commands above to create your first bot
2. **Learn**: Follow the [My First Bot guide](docs/bot-guides/my-first-bot.md)
3. **Develop**: Write your trading strategies
4. **Test**: Use testnet environments for safe testing
5. **Deploy**: Move to live trading when ready

## 📝 Available Documentation

- **[My First Bot Guide](docs/bot-guides/my-first-bot.md)** - Complete beginner tutorial
- [Trading Fundamentals](docs/trading-fundamentals.md)
- [Risk Management](docs/risk-management.md)
- [Logging Guide](docs/LOGGING.md)
- [Bot Development Guides](docs/bot-guides/)

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
