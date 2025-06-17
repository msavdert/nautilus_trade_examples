# 🌊 Nautilus Trader - Professional Sandbox Trading System

[![License](https://img.shields.io/badge/license-LGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![Binance](https://img.shields.io/badge/exchange-Binance%20Testnet-yellow.svg)](https://testnet.binance.vision/)

**A professional algorithmic trading system built on Nautilus Trader framework with EMA Cross strategy, PostgreSQL storage, and Redis caching - completely safe for testing with Binance Testnet.**

> 🇹🇷 **Türkçe dokümantasyon için**: [README.tr.md](README.tr.md)

---

## 🌟 Features

- **Safe Testing Environment**: Uses Binance Testnet - no real money involved
- **Professional Architecture**: Built on Nautilus Trader, industry-standard trading framework
- **EMA Cross Strategy**: Proven algorithmic trading strategy with 10/20 period exponential moving averages
- **Complete Infrastructure**: PostgreSQL for historical data, Redis for real-time caching
- **Docker Containerized**: One-command deployment with docker-compose
- **Risk Management**: Built-in risk controls to prevent losses
- **Real-time Market Data**: Live streaming from Binance Testnet
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Production Ready**: Scalable architecture suitable for real trading (with modifications)

---

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** installed
- **Binance Testnet Account**
- **Git** for cloning the repository

### 1. Setup Binance Testnet API

1. Go to [Binance Testnet](https://testnet.binance.vision/)
2. Create an account or login
3. Generate API Key and Secret
4. Create `.env` file in this directory:

```bash
# .env
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

### 2. Start Trading System

```bash
# Start all services (PostgreSQL, Redis, Trading Bot)
docker-compose up -d

# View logs in real-time
docker-compose logs -f nautilus-sandbox-trader
```

### 3. Monitor the System

```bash
# Check service status
docker-compose ps

# View PostgreSQL logs
docker-compose logs -f nautilus-postgres

# View Redis logs
docker-compose logs -f nautilus-redis

# Stop all services
docker-compose stop

# Remove all containers (data preserved)
docker-compose down
```

---

## 📊 Trading Strategy

### EMA Cross Strategy

The system uses a proven **EMA Cross Strategy** with the following logic:

**Strategy Components:**
- **Fast EMA**: 10-period exponential moving average (captures short-term trends)
- **Slow EMA**: 20-period exponential moving average (captures long-term trends)
- **Timeframe**: 1-minute candles for responsive trading
- **Trading Pair**: BTCUSDT.BINANCE (most liquid pair)

**Trading Signals:**
- **BUY Signal**: Fast EMA crosses above Slow EMA (Golden Cross)
- **SELL Signal**: Fast EMA crosses below Slow EMA (Death Cross)

**Risk Management:**
- **Trade Size**: 0.001 BTC per trade (~$30-50 test amount)
- **Maximum Orders**: 10 orders per second limit
- **Position Limit**: $1000 maximum per order
- **Stop Loss**: Automatic via Nautilus risk engine

---

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                 Nautilus Trader Sandbox                    │
├─────────────────────────────────────────────────────────────┤
│  📊 Trading Bot (sandbox_trader.py)                        │
│  ├── EMA Cross Strategy                                     │
│  ├── Risk Management Engine                                 │
│  ├── Order Management System                               │
│  └── Real-time Market Data Processing                      │
├─────────────────────────────────────────────────────────────┤
│  🏦 PostgreSQL Database                                     │
│  ├── Historical OHLCV Data                                 │
│  ├── Orders & Trades History                               │
│  ├── Positions & Portfolio Data                            │
│  └── Strategy Performance Metrics                          │
├─────────────────────────────────────────────────────────────┤
│  🚀 Redis Cache                                             │
│  ├── Real-time Market Data                                 │
│  ├── Order Book Snapshots                                  │
│  ├── Recent Trade Data                                     │
│  └── System State Cache                                    │
├─────────────────────────────────────────────────────────────┤
│  📡 Binance Testnet API                                     │
│  ├── Market Data WebSocket                                 │
│  ├── Order Execution REST API                              │
│  ├── Account Information                                   │
│  └── Real-time Price Feeds                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration

### Environment Variables

All configuration is centralized in `sandbox_trader.py` for maximum transparency and control. The system uses environment variables for sensitive data:

```bash
# Binance Testnet API
BINANCE_TESTNET_API_KEY=your_api_key
BINANCE_TESTNET_API_SECRET=your_api_secret

# Database (Docker automatically sets these)
NAUTILUS_DATABASE_HOST=nautilus-postgres
NAUTILUS_DATABASE_PORT=5432
NAUTILUS_DATABASE_NAME=nautilus
NAUTILUS_DATABASE_USER=nautilus
NAUTILUS_DATABASE_PASSWORD=nautilus123

# Cache (Docker automatically sets these)
NAUTILUS_CACHE_DATABASE_HOST=nautilus-redis
NAUTILUS_CACHE_DATABASE_PORT=6379
```

### Strategy Parameters

Key trading parameters can be modified in `sandbox_trader.py`:

```python
# EMA Periods
fast_ema_period = 10        # Fast EMA
slow_ema_period = 20        # Slow EMA

# Trading Size
trade_size = Decimal("0.001")  # 0.001 BTC per trade

# Trading Pair
instrument_id = "BTCUSDT.BINANCE"

# Timeframe
bar_type = "BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL"

# Risk Limits
max_order_submit_rate = "10/00:00:01"      # 10 orders per second
max_notional_per_order = Decimal("1000.0") # $1000 max per order
```

---

## 📊 Monitoring & Logs

### Log Files

The system generates comprehensive logs for monitoring:

```bash
logs/
├── nautilus_trader.log         # Main trading logs
├── database.log               # Database operations
├── redis.log                  # Cache operations
└── errors.log                 # Error logs
```

### Real-time Monitoring

```bash
# Watch trading activity
docker-compose logs -f nautilus-sandbox-trader

# Monitor all services
docker-compose logs -f

# Check system resources
docker stats

# Access PostgreSQL directly
docker exec -it nautilus-postgres psql -U nautilus -d nautilus

# Access Redis directly
docker exec -it nautilus-redis redis-cli
```

### Performance Metrics

Key metrics to monitor:

- **Order Fill Rate**: Orders executed vs placed
- **Strategy Performance**: P&L tracking
- **Latency**: Order execution speed
- **System Health**: CPU, Memory, Network
- **Data Quality**: Market data completeness

---

## 🛠️ Customization

### Adding New Strategies

To implement a custom strategy:

1. Create a new strategy class inheriting from `Strategy`
2. Implement required methods: `on_start()`, `on_stop()`, `on_bar()`
3. Update `create_strategy()` method in `sandbox_trader.py`
4. Configure strategy parameters

### Adding New Trading Pairs

```python
# In create_config() method
load_ids=frozenset([
    InstrumentId.from_str("BTCUSDT.BINANCE"),
    InstrumentId.from_str("ETHUSDT.BINANCE"),    # Add Ethereum
    InstrumentId.from_str("ADAUSDT.BINANCE"),    # Add Cardano
]),
```

### Database Schema Customization

Nautilus automatically creates required tables. For custom tables:

```sql
-- Create custom tables in data/postgres_init/custom.sql
CREATE TABLE IF NOT EXISTS custom_metrics (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value DECIMAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔒 Security Best Practices

**API Security:**
- ✅ Always use Testnet for development
- ✅ Never commit API keys to version control
- ✅ Use environment variables for sensitive data
- ✅ Regularly rotate API keys
- ✅ Enable IP whitelisting on Binance

**System Security:**
- ✅ Use Docker for isolation
- ✅ Regular backup of database
- ✅ Monitor logs for unusual activity
- ✅ Keep dependencies updated
- ✅ Use strong passwords for production

---

## 🐛 Troubleshooting

### Common Issues

**1. Container won't start**
```bash
# Check Docker service
sudo systemctl status docker

# Check logs
docker-compose logs nautilus-sandbox-trader

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**2. API Connection Issues**
```bash
# Verify API keys in .env file
cat .env

# Test API connectivity
curl -X GET "https://testnet.binance.vision/api/v3/time"

# Check network connectivity
docker exec nautilus-sandbox-trader ping testnet.binance.vision
```

**3. Database Connection Issues**
```bash
# Check PostgreSQL status
docker-compose ps nautilus-postgres

# Test database connection
docker exec -it nautilus-postgres psql -U nautilus -d nautilus -c "SELECT 1;"

# Reset database
docker-compose down
docker volume rm sandbox_postgres_data
docker-compose up -d
```

**4. Redis Connection Issues**
```bash
# Check Redis status
docker-compose ps nautilus-redis

# Test Redis connection
docker exec -it nautilus-redis redis-cli ping

# Clear Redis cache
docker exec -it nautilus-redis redis-cli FLUSHALL
```

### Debug Mode

```python
# In sandbox_trader.py, change log level
logging_config = LoggingConfig(
    log_level="DEBUG",  # Change from INFO to DEBUG
    log_colors=True,
)
```

---

## 📊 Historical Data Analysis

### Querying PostgreSQL Database

The system stores all historical data in PostgreSQL. Use the provided tools to analyze your trading data:

#### Quick Data Queries

```bash
# List available tables
python3 query_historical_data.py --list-tables

# List available instruments
python3 query_historical_data.py --list-instruments

# Get BTCUSDT bar data (last 100 bars)
python3 query_historical_data.py --bars BTCUSDT --limit 100

# Get tick data with date range
python3 query_historical_data.py --ticks BTCUSDT --start 2025-06-15 --end 2025-06-16

# Trading statistics for last 7 days
python3 query_historical_data.py --stats BTCUSDT --days 7

# Order history
python3 query_historical_data.py --orders --limit 20

# Position history
python3 query_historical_data.py --positions --limit 20

# Export to CSV
python3 query_historical_data.py --bars BTCUSDT --output btc_data.csv
```

#### Direct PostgreSQL Access

```bash
# Connect to PostgreSQL container
docker exec -it nautilus-postgres psql -U trading_user -d nautilus_trading

# Or from host (port 5433)
psql -h localhost -p 5433 -U trading_user -d nautilus_trading
```

#### Common SQL Queries

```sql
-- Latest OHLCV data
SELECT ts_event, open, high, low, close, volume 
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%' 
ORDER BY ts_event DESC LIMIT 50;

-- Daily trading volume
SELECT 
    DATE(ts_event) as date,
    SUM(volume) as daily_volume,
    AVG(close) as avg_price
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
GROUP BY DATE(ts_event)
ORDER BY date DESC;

-- Trading performance
SELECT 
    COUNT(*) as total_orders,
    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as profitable_trades,
    SUM(realized_pnl) as total_pnl
FROM positions 
WHERE trader_id = 'SANDBOX-TRADER-001';
```

#### Test All Queries

```bash
# Run comprehensive test
./test_queries.sh
```

**📚 For detailed query examples, see**: [POSTGRESQL_QUERIES.md](POSTGRESQL_QUERIES.md)

---

## 🔄 Production Deployment

**⚠️ Important: This sandbox is for testing only. For production deployment:**

1. **Switch to Live API**: Change from Testnet to live Binance API
2. **Enhance Security**: Use secure secrets management
3. **Scale Infrastructure**: Use Kubernetes or Docker Swarm
4. **Add Monitoring**: Implement Prometheus, Grafana
5. **Backup Strategy**: Automated database backups
6. **Load Balancing**: Multiple trading nodes for redundancy
7. **Legal Compliance**: Ensure regulatory compliance

---

## 📚 Learning Resources

**Nautilus Trader:**
- [Official Documentation](https://nautilustrader.io/)
- [API Reference](https://docs.nautilustrader.io/)
- [GitHub Repository](https://github.com/nautechsystems/nautilus_trader)

**Algorithmic Trading:**
- [Quantitative Trading Strategies](https://www.quantstart.com/)
- [Python for Finance](https://pypi.org/project/yfinance/)
- [Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)

**Technical Analysis:**
- [Moving Averages](https://www.investopedia.com/terms/m/movingaverage.asp)
- [EMA vs SMA](https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp)

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**Areas for improvement:**
- Additional trading strategies
- Enhanced risk management
- UI/Dashboard development
- Performance optimizations
- Documentation improvements

---

## 📄 License

This project is licensed under the LGPL-3.0 License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**This software is for educational and testing purposes only. Trading involves substantial risk of loss and is not suitable for all investors. Past performance is not indicative of future results. Use at your own risk.**

- This is a Testnet implementation using virtual funds
- No real money is involved in this sandbox
- Always test thoroughly before any live trading
- Consult with financial advisors for investment decisions
- The authors are not responsible for any financial losses

---

## 📞 Support

For support and questions:

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check the official Nautilus documentation
- **Community**: Join trading and Python communities

---

**Happy Trading!** 🚀📈
