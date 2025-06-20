# Binance Futures Testnet Trading Bot

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Nautilus](https://img.shields.io/badge/nautilus-1.200.0+-green.svg)](https://github.com/nautechsystems/nautilus_trader)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive automated trading bot for **Binance Futures Testnet** using the Nautilus framework. This bot implements an **RSI Mean Reversion strategy** with robust risk management and is designed specifically for learning, testing, and developing trading strategies in a safe testnet environment.

## ⚠️ IMPORTANT DISCLAIMERS

- **TESTNET ONLY**: This bot is designed exclusively for Binance Futures Testnet and should NEVER be used with real funds
- **Educational Purpose**: This is for learning and testing trading strategies only
- **No Financial Advice**: This software does not constitute financial advice
- **Use at Your Own Risk**: Trading involves risk of loss, even in testnet environments
- **US Users**: Designed with US regional requirements in mind

## 🎯 Features

### Trading Strategy
- **RSI Mean Reversion Strategy**: Well-documented and proven approach for crypto markets
- **Multi-Instrument Trading**: Trades top 50 cryptocurrencies by volume
- **Volume & Trend Confirmation**: Additional filters to improve signal quality
- **Configurable Parameters**: Easily adjustable strategy settings

### Risk Management
- **Position Sizing**: Automatic position sizing based on account balance and volatility
- **Stop Loss & Take Profit**: Automatic SL/TP orders with configurable levels
- **Daily Loss Limits**: Protection against excessive daily losses
- **Drawdown Protection**: Emergency stop mechanisms
- **Maximum Position Limits**: Prevents over-exposure

### Technical Features
- **Real-time Data**: Live market data from Binance Futures Testnet
- **US Compatible**: Uses US-compatible API endpoints
- **Docker Ready**: Fully containerized for easy deployment
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Backtesting**: Historical strategy testing capabilities
- **Performance Analytics**: Detailed performance tracking and reporting

## 📋 Requirements

### System Requirements
- Python 3.11 or higher
- Docker (recommended)
- 4GB RAM minimum
- Stable internet connection

### API Requirements
- Binance Futures Testnet account
- Testnet API key and secret
- US-compatible Binance account (for US users)

## 🚀 Quick Start

### 1. Get Binance Testnet Credentials

1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Create an account or log in
3. Generate API key and secret
4. **Important for US Users**: Ensure your account is US-compatible

### 2. Setup Environment

#### Via Docker (Recommended)

```bash
# Navigate to the project directory
cd /workspace/bots/binance/testnet/

# Copy environment template
cp .env.example .env

# Edit .env file with your testnet credentials
nano .env  # or your preferred editor

# Run the bot
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance/testnet/ && uv run python main.py --mode demo"
```

#### Direct Installation

```bash
# Navigate to project directory
cd bots/binance/testnet/

# Install dependencies
uv install

# Or with pip
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env

# Run the bot
python main.py --mode demo
```

### 3. Configure Your Environment

Edit your `.env` file with your Binance Testnet credentials:

```env
# Your Binance Futures Testnet API credentials
BINANCE_TESTNET_API_KEY=your_testnet_api_key_here
BINANCE_TESTNET_API_SECRET=your_testnet_api_secret_here

# Optional: Override default settings
TRADING_MAX_POSITIONS=3
TRADING_LEVERAGE=5
LOG_LEVEL=INFO
```

## 🎮 Usage

### Command Line Options

```bash
# Demo mode (paper trading)
python main.py --mode demo --instruments 20 --initial-balance 10000

# Live mode (testnet with real API calls)
python main.py --mode live --instruments 50 --log-level DEBUG

# Backtest mode
python run_backtest.py --symbols BTCUSDT ETHUSDT --start 2024-01-01 --end 2024-12-31
```

### Docker Usage (Recommended)

```bash
# Demo mode
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance/testnet/ && uv run python main.py --mode demo"

# Live testnet mode
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance/testnet/ && uv run python main.py --mode live --instruments 30"

# Run backtest
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance/testnet/ && uv run python run_backtest.py"

# Run tests
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance/testnet/ && uv run pytest tests/ -v"
```

### Available Commands

| Command | Description |
|---------|-------------|
| `--mode demo` | Paper trading mode (no real API calls) |
| `--mode live` | Live testnet mode (real API calls to testnet) |
| `--mode backtest` | Historical backtesting |
| `--instruments N` | Number of top instruments to trade (default: 20) |
| `--initial-balance N` | Initial balance for demo mode (default: 10000) |
| `--log-level LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `--config FILE` | Custom configuration file |

## 📊 Strategy Details

### RSI Mean Reversion Strategy

**Why This Strategy?**

1. **Proven Effectiveness**: RSI mean reversion is one of the most studied and effective strategies in crypto markets
2. **Risk Management**: Built-in oversold/overbought levels provide natural entry/exit points
3. **Adaptability**: Works well across different timeframes and market conditions
4. **Clear Signals**: Generates unambiguous trading signals that are easy to validate

**Strategy Logic:**

#### Entry Conditions (LONG)
- RSI falls below 30 (oversold)
- Price is above 20-period moving average (trend filter)
- Volume is 20% above average (confirmation)
- No existing position in same instrument

#### Entry Conditions (SHORT)
- RSI rises above 70 (overbought)
- Price is below 20-period moving average (trend filter)
- Volume is 20% above average (confirmation)
- No existing position in same instrument

#### Exit Conditions
- RSI returns to neutral zone (40-60)
- Stop loss triggered (2% adverse move)
- Take profit triggered (4% favorable move)
- Daily loss limit reached

#### Risk Management
- Maximum 5% of account per position
- 2% stop loss, 4% take profit (1:2 risk-reward ratio)
- Maximum 3 open positions simultaneously
- Daily loss limit protection (8% of account)

### Configuration Parameters

Key parameters can be adjusted in `config/config.yaml`:

```yaml
trading:
  rsi_period: 14                    # RSI calculation period
  rsi_oversold: 30.0               # Oversold threshold
  rsi_overbought: 70.0             # Overbought threshold
  max_position_size_pct: 0.05      # 5% max position size
  stop_loss_pct: 0.02              # 2% stop loss
  take_profit_pct: 0.04            # 4% take profit
  default_leverage: 5              # Default leverage
  max_open_positions: 3            # Max simultaneous positions
```

## 🛡️ Risk Management

### Built-in Protections

1. **Position Sizing**: Automatic sizing based on account balance and volatility
2. **Stop Losses**: Mandatory stop losses on all positions
3. **Daily Limits**: Maximum daily loss protection
4. **Drawdown Protection**: Emergency stop at maximum drawdown
5. **Position Limits**: Maximum number of open positions
6. **Leverage Control**: Conservative leverage settings

### Emergency Features

- **Emergency Stop**: Immediate cessation of all trading
- **Position Liquidation**: Automatic position closure on risk violations
- **Alert System**: Comprehensive logging and monitoring

## 📈 Performance Monitoring

### Real-time Monitoring

The bot provides comprehensive real-time monitoring:

- Portfolio value and P&L
- Individual position performance
- Risk metrics and exposure
- Daily trading statistics
- Strategy effectiveness metrics

### Logging

Detailed logging includes:

- Trade executions and rationale
- Risk management decisions
- Market data and signals
- System health and errors
- Performance statistics

Log files are stored in the `logs/` directory with daily rotation.

## 🧪 Testing and Backtesting

### Unit Tests

```bash
# Run all tests
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance/testnet/ && uv run pytest tests/ -v"

# Run specific test files
uv run pytest tests/test_strategy.py -v
uv run pytest tests/test_utils.py -v
```

### Backtesting

```bash
# Backtest single symbol
python run_backtest.py --symbols BTCUSDT --start 2024-01-01 --end 2024-12-31

# Backtest multiple symbols
python run_backtest.py --symbols BTCUSDT ETHUSDT ADAUSDT --start 2024-06-01 --end 2024-12-31 --balance 10000

# Generate detailed reports
python run_backtest.py --symbols BTCUSDT --start 2024-01-01 --end 2024-12-31 --config config/backtest.yaml
```

Backtest results are saved in `backtest_results/` with:
- JSON performance data
- HTML performance charts
- Detailed trade logs
- Risk analysis reports

## 🔧 Configuration

### Environment Variables (.env)

```env
# Binance Futures Testnet API Credentials
BINANCE_TESTNET_API_KEY=your_testnet_api_key_here
BINANCE_TESTNET_API_SECRET=your_testnet_api_secret_here

# Trading Configuration Override
TRADING_MAX_POSITIONS=3
TRADING_POSITION_SIZE_PCT=0.05
TRADING_LEVERAGE=5

# Risk Management Override
RISK_MAX_DAILY_LOSS_PCT=0.08
RISK_MAX_DRAWDOWN_PCT=0.12

# Regional Settings for US Users
BINANCE_US_MODE=true
TIMEZONE=America/New_York
```

### Configuration Files

- `config/config.yaml`: Main trading configuration
- `.env`: Environment variables and secrets
- `pyproject.toml`: Python dependencies and project metadata

### US Users - Special Considerations

For users based in the United States:

1. **API Endpoints**: The bot uses US-compatible Binance Futures Testnet endpoints
2. **Account Verification**: Ensure your Binance account is US-compatible
3. **Regulatory Compliance**: This bot is for testnet/educational use only
4. **Time Zones**: Configure appropriate timezone in `.env` file

## 🐛 Troubleshooting

### Common Issues

#### API Connection Issues
```
Error: Failed to connect to Binance API
```
**Solution**: 
- Verify your API credentials in `.env`
- Ensure you're using Testnet credentials, not mainnet
- Check your internet connection
- Verify API key permissions include Futures trading

#### Insufficient Data Error
```
Error: Insufficient data for indicators
```
**Solution**:
- The strategy needs historical data to initialize indicators
- Wait for initial data collection (usually 1-2 minutes)
- Check if selected instruments have sufficient trading volume

#### Permission Denied Errors
```
Error: Permission denied for futures trading
```
**Solution**:
- Enable Futures trading on your Testnet account
- Regenerate API keys with Futures permissions
- Verify account is US-compatible (for US users)

#### High Memory Usage
**Solution**:
- Reduce number of instruments (`--instruments` parameter)
- Increase system RAM
- Monitor log files for memory leaks

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
python main.py --mode demo --log-level DEBUG
```

This provides:
- Detailed API call logs
- Strategy decision explanations
- Risk management calculations
- Performance metrics

## 🔄 Migration to Mainnet

**⚠️ CRITICAL WARNING**: This section is for educational purposes only. Never trade with real money without proper testing and risk management.

To migrate from testnet to mainnet (EDUCATIONAL ONLY):

### Required Changes

1. **API Endpoints**: Update to mainnet URLs in `config.py`
   ```python
   # Change from testnet URLs
   futures_base_url: str = "https://fapi.binance.com"
   futures_api_url: str = "https://fapi.binance.com/fapi/v1"
   ```

2. **API Credentials**: Use real mainnet API keys
   ```env
   BINANCE_API_KEY=your_real_api_key
   BINANCE_API_SECRET=your_real_api_secret
   ```

3. **Risk Parameters**: Reduce risk for real trading
   ```yaml
   trading:
     max_position_size_pct: 0.01  # Reduce to 1%
     stop_loss_pct: 0.01          # Tighter stop loss
     max_open_positions: 1        # Reduce positions
     default_leverage: 2          # Lower leverage
   ```

4. **Account Type**: Change account type
   ```python
   account_type: BinanceAccountType.FUTURES_USDT  # Remove TESTNET
   ```

### Pre-Mainnet Checklist

- [ ] Extensive backtesting with historical data
- [ ] Minimum 30 days successful testnet operation
- [ ] Risk management thoroughly tested
- [ ] Emergency procedures documented
- [ ] Start with minimal position sizes
- [ ] 24/7 monitoring capability
- [ ] Legal/regulatory compliance verified

## 📚 Additional Resources

### Learning Materials

- [Nautilus Trader Documentation](https://docs.nautilustrader.io/)
- [Binance Futures API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [RSI Strategy Analysis](https://www.investopedia.com/terms/r/rsi.asp)
- [Cryptocurrency Trading Basics](https://academy.binance.com/)

### Community and Support

- [Nautilus Trader Discord](https://discord.gg/nautilus)
- [Binance API Community](https://dev.binance.vision/)
- [Algorithmic Trading Forums](https://www.reddit.com/r/algotrading/)

## 📄 Project Structure

```
bots/binance/testnet/
├── main.py                     # Main bot application
├── config.py                   # Configuration management
├── run_backtest.py            # Backtesting runner
├── .env.example               # Environment template
├── pyproject.toml             # Project dependencies
├── README.md                  # This file
├── config/
│   └── config.yaml           # Trading configuration
├── strategies/
│   └── rsi_mean_reversion.py # RSI strategy implementation
├── utils/
│   ├── __init__.py           # Utility functions
│   ├── coin_selector.py      # Instrument selection
│   └── risk_manager.py       # Risk management
├── tests/
│   ├── test_strategy.py      # Strategy tests
│   └── test_utils.py         # Utility tests
└── logs/                      # Log files directory
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Setup

```bash
# Clone repository
git clone <repository-url>

# Install development dependencies
uv install --dev

# Run tests
uv run pytest tests/ -v

# Run code formatting
uv run black .

# Run type checking
uv run mypy .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Disclaimer

This software is provided for educational and testing purposes only. The authors and contributors:

- Make no guarantees about the performance or profitability of any trading strategy
- Are not responsible for any financial losses incurred through use of this software
- Strongly recommend thorough testing before any real trading
- Advise consulting with qualified financial professionals before trading

Trading cryptocurrencies involves substantial risk of loss and is not suitable for all investors.

## 🆔 Version Information

- **Current Version**: 2.0.0
- **Nautilus Framework**: 1.200.0+
- **Python Requirement**: 3.11+
- **Last Updated**: 2024-12-18

---

**Remember**: This is a testnet-only educational tool. Never risk money you cannot afford to lose, and always thoroughly test any trading strategy before considering real implementation.
