# One-Three Risk Management Trading Bot

<div align="center">

![Nautilus Trader](https://img.shields.io/badge/Nautilus_Trader-1.218.0+-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Trading](https://img.shields.io/badge/Asset-EUR%2FUSD-orange.svg)

**A sophisticated EUR/USD trading bot implementing disciplined risk management with fixed take profit and stop loss levels using the Nautilus Trader framework.**

</div>

## 🎯 Strategy Overview

The One-Three Bot implements a systematic risk management approach for EUR/USD forex trading:

- **Fixed Risk Management**: Every trade has exactly +1.3 pips take profit and -1.3 pips stop loss
- **No Position Scaling**: Fixed position sizes with no martingale or averaging strategies  
- **Single Position Trading**: Only one trade open at a time to maintain control
- **Step-by-Step Approach**: Each trade is independent, no attempt to recover previous losses
- **Comprehensive Logging**: Complete trade history with detailed performance analytics

### Why This Strategy?

This strategy focuses on **consistency and risk control** rather than maximizing profits. The 1:1 risk-reward ratio with fixed levels provides:

1. **Predictable Risk**: You always know exactly how much you can lose
2. **Emotional Control**: No guessing about exit points reduces psychological pressure
3. **Easy Analysis**: Simple metrics make performance evaluation straightforward
4. **Scalable Framework**: Can be adapted to different timeframes and instruments

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Nautilus Trader 1.218.0+
- At least 8GB RAM (for backtesting with large datasets)

### Installation

1. **Clone or download this project:**
   ```bash
   cd /path/to/your/nautilus_trade_examples/bots/
   # The one_three folder should be here
   ```

2. **Install dependencies:**
   ```bash
   cd one_three
   uv sync  # or pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python one_three_strategy.py
   ```

### Run Your First Backtest

```bash
# Run backtest with generated sample data
python run_backtest.py

# The script will:
# 1. Generate realistic EUR/USD tick data
# 2. Run the One-Three strategy
# 3. Display performance results
# 4. Save detailed logs
```

## 📊 Understanding the Strategy

### Entry Logic

The current implementation uses a simple entry trigger (for demonstration):
- Buys EUR/USD at current market price
- Waits for configurable delay between trades
- Respects daily trade limits

**🔧 Customization Point**: Replace the entry logic in `check_entry_conditions()` with your preferred signal:
- Technical indicators (RSI, MACD, Moving Averages)
- Fundamental analysis triggers
- News-based signals
- Price action patterns

### Exit Logic

**Take Profit**: Closes position when profit reaches +1.3 pips
**Stop Loss**: Closes position when loss reaches -1.3 pips

Both exits use market orders for immediate execution to ensure the exact risk parameters are maintained.

### Risk Management Features

- **Position Size Control**: Fixed lot sizes (configurable)
- **Daily Trade Limits**: Maximum number of trades per day
- **Time Filters**: Optional trading hours restrictions
- **Slippage Tolerance**: Configurable maximum acceptable slippage
- **Connection Monitoring**: Automatic reconnection and error handling

## 🛠️ Configuration

### Strategy Configuration

Edit the strategy parameters in `run_backtest.py` or `run_live.py`:

```python
strategy_config = OneThreeConfig(
    # Core settings
    instrument_id="EUR/USD.SIM",
    trade_size=Decimal("100_000"),  # Position size in base currency
    
    # Risk management
    take_profit_pips=1.3,  # Take profit level
    stop_loss_pips=1.3,    # Stop loss level
    
    # Trading limits
    max_daily_trades=20,        # Max trades per day
    entry_delay_seconds=60,     # Minimum delay between trades
    
    # Market timing (optional)
    enable_time_filter=True,
    trading_start_hour=8,       # Start trading (UTC)
    trading_end_hour=18,        # Stop trading (UTC)
    
    # Advanced features
    use_tick_data=True,         # Use tick-level precision
    slippage_tolerance=0.5,     # Max acceptable slippage (pips)
)
```

### Backtesting Configuration

Customize backtest parameters:

```python
# Data generation
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
num_ticks = 100_000  # Number of price ticks

# Account settings
starting_balance = 100_000  # USD
leverage = 30  # 30:1 leverage
```

## 📈 Running Backtests

### Basic Backtest

```bash
python run_backtest.py
```

This will:
1. Generate realistic EUR/USD market data
2. Run the strategy with default settings
3. Display performance summary
4. Save detailed logs to `logs/one_three_backtest.log`

### Advanced Backtesting

For more sophisticated backtesting:

1. **Use Historical Data**: Replace the sample data generation with real historical data
2. **Parameter Optimization**: Test different pip levels and trade frequencies
3. **Multiple Timeframes**: Test across different market conditions
4. **Walk-Forward Analysis**: Use rolling time periods to validate robustness

### Expected Backtest Results

With a 1:1 risk-reward ratio, the strategy needs a win rate above 50% to be profitable:

- **55% Win Rate**: ~10% annual return (after costs)
- **60% Win Rate**: ~20% annual return (after costs)  
- **65% Win Rate**: ~30% annual return (after costs)

**Note**: These are theoretical examples. Actual results depend on market conditions, execution quality, and entry signal effectiveness.

## 🔴 Live Trading

⚠️ **IMPORTANT**: Live trading involves real money risk. Always test thoroughly in demo mode first.

### Setup for Live Trading

1. **Configure Data Provider**: Edit `run_live.py` to add your data feed
2. **Configure Broker**: Add your execution venue configuration
3. **Set API Credentials**: Securely store your API keys
4. **Test in Demo Mode**: Always test with demo accounts first

### Supported Brokers

The Nautilus framework supports many brokers through adapters:

- **Interactive Brokers**: Professional-grade execution
- **OANDA**: Retail forex broker with good API
- **Binance**: For crypto trading
- **Many Others**: Check Nautilus documentation for full list

### Live Trading Command

```bash
python run_live.py
```

**Security Checklist**:
- [ ] Tested thoroughly in demo mode
- [ ] Set appropriate position sizes
- [ ] Configured daily loss limits
- [ ] Monitored system stability
- [ ] Have backup plans for connection issues

## 📊 Performance Analysis

### Analyze Results

```bash
python analyze_results.py
```

This generates:
- **Performance Summary**: Win rate, profit factor, Sharpe ratio
- **Visual Charts**: Equity curve, P&L distribution, drawdown analysis
- **Detailed Report**: Trade-by-trade breakdown
- **Risk Metrics**: Maximum drawdown, risk-adjusted returns

### Key Metrics to Monitor

1. **Win Rate**: Should be >50% for profitability with 1:1 R:R
2. **Profit Factor**: Ratio of gross profit to gross loss (>1.0 required)
3. **Maximum Drawdown**: Largest peak-to-trough loss period
4. **Sharpe Ratio**: Risk-adjusted return measure
5. **Average Trade Duration**: How long positions are held

### Sample Analysis Output

```
📊 TRADING SUMMARY
──────────────────────────────
Total Trades:           250
Winning Trades:         152 (60.8%)
Losing Trades:          98 (39.2%)

💰 PROFIT & LOSS
──────────────────────────────
Total P&L:              $5,420.00
Average Win:            $13.00
Average Loss:           -$13.00
Profit Factor:          1.55

📈 PERFORMANCE METRICS
──────────────────────────────
Sharpe Ratio:           1.82
Max Drawdown:           -$156.00
Win Rate Target:        >50% (Actual: 60.8%) ✅
```

## 🔧 Customization Guide

### Adding Your Entry Signal

Replace the simple entry logic with your preferred signal:

```python
def check_entry_conditions(self, tick) -> None:
    """Your custom entry logic here"""
    
    # Example: RSI-based entry
    if self.rsi.value < 30:  # Oversold
        self.enter_long_position()
    elif self.rsi.value > 70:  # Overbought
        self.enter_short_position()
        
    # Example: Moving average crossover
    if self.fast_ma.value > self.slow_ma.value:
        self.enter_long_position()
        
    # Example: News-based entry
    if self.news_sentiment > 0.7:
        self.enter_long_position()
```

### Adding Technical Indicators

The Nautilus framework provides many built-in indicators:

```python
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.indicators.ema import ExponentialMovingAverage

# In your strategy __init__ method:
self.rsi = RelativeStrengthIndex(period=14)
self.fast_ema = ExponentialMovingAverage(period=12)
self.slow_ema = ExponentialMovingAverage(period=26)

# In your on_bar method:
self.rsi.update_raw(bar.close)
self.fast_ema.update_raw(bar.close)
self.slow_ema.update_raw(bar.close)
```

### Modifying Risk Parameters

```python
# Dynamic stop loss based on volatility
def calculate_dynamic_stop_loss(self, current_volatility):
    base_stop = self.config.stop_loss_pips
    volatility_multiplier = min(2.0, current_volatility / 0.0001)
    return base_stop * volatility_multiplier

# Trailing stop implementation
def update_trailing_stop(self, current_price):
    if self.current_position and self.config.enable_trailing_stop:
        new_stop = current_price - self.config.trailing_stop_distance * self.pip_size
        if new_stop > self.current_stop_loss:
            self.modify_stop_loss(new_stop)
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Strategy not receiving data
- **Solution**: Check data feed configuration and network connection
- **Debug**: Enable debug logging to see data flow

**Issue**: Orders not executing
- **Solution**: Verify broker connection and account permissions
- **Debug**: Check order rejection reasons in logs

**Issue**: Unexpected P&L calculations
- **Solution**: Verify pip values and position sizing for your broker
- **Debug**: Log entry/exit prices and compare with broker statements

**Issue**: High slippage affecting results
- **Solution**: Adjust slippage tolerance or use limit orders instead of market orders
- **Debug**: Monitor execution quality during different market sessions

### Debug Mode

Enable detailed logging for troubleshooting:

```python
# In your configuration:
logging=LoggingConfig(
    log_level="DEBUG",  # Changed from "INFO"
    log_level_file="DEBUG",
    log_colors=True,
)
```

### Performance Optimization

For high-frequency operation:

1. **Use Tick Data**: Set `use_tick_data=True` for best precision
2. **Optimize Indicators**: Use built-in Nautilus indicators (faster than pandas)
3. **Reduce Logging**: Use "ERROR" level for production
4. **Database Backend**: Use Redis for state persistence in production

## 📚 Further Learning

### Nautilus Trader Resources

- **Official Documentation**: [nautilustrader.io/docs](https://nautilustrader.io/docs)
- **GitHub Repository**: [github.com/nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)
- **Discord Community**: [discord.gg/NautilusTrader](https://discord.gg/NautilusTrader)
- **Examples**: Check the `examples/` directory in the main repository

### Trading Strategy Development

- **Backtesting Best Practices**: Avoid overfitting, use out-of-sample testing
- **Risk Management**: Position sizing, correlation analysis, portfolio management
- **Market Microstructure**: Understanding spreads, slippage, and market impact
- **Algorithm Development**: Event-driven programming, state management

### Recommended Reading

- "Algorithmic Trading" by Ernie Chan
- "Quantitative Trading" by Ernie Chan  
- "The Elements of Statistical Learning" by Hastie, Tibshirani, and Friedman
- "Building Winning Algorithmic Trading Systems" by Kevin Davey

## 🤝 Contributing

We welcome contributions to improve the One-Three strategy:

1. **Bug Fixes**: Report issues or submit fixes
2. **Feature Additions**: New risk management features, indicators, or analysis tools
3. **Documentation**: Improve explanations or add examples
4. **Testing**: Add test cases or validate on different markets

### Development Setup

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest tests/

# Code formatting
black *.py
ruff check *.py
```

## ⚠️ Disclaimer

**Important Risk Warning**: 

- Trading forex involves substantial risk and may not be suitable for all investors
- Past performance is not indicative of future results
- This software is provided for educational purposes
- Always test strategies thoroughly before risking real capital
- Consider seeking advice from qualified financial professionals
- The authors are not responsible for any financial losses

**Software License**: This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

- **GitHub Issues**: For bug reports and feature requests
- **Discord**: Join the Nautilus Trader community for discussion
- **Email**: Contact the development team for commercial support

---

<div align="center">

**Built with ❤️ using [Nautilus Trader](https://nautilustrader.io)**

*Happy Trading! 📈*

</div>
