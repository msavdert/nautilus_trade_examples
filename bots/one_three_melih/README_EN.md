# One-Three-Melih: Advanced Step-Back Risk Management Trading Bot

## Overview

The **One-Three-Melih** trading bot is a sophisticated EUR/USD forex trading system that implements an advanced step-back balance management strategy using the Nautilus Trader framework. This bot follows a disciplined approach where profits increase the trading balance for subsequent trades, while losses trigger intelligent step-backs to previous balance levels.

## 🚀 Key Features

### Advanced Balance Management
- **Full Balance Usage**: Every trade uses the entire available balance (no partial positions)
- **Profit Steps**: +30% profit target increases balance for next trade
- **Dynamic Step-Back**: Losses return balance to previous step level
- **No Martingale**: Fixed risk per step, no position scaling

### Risk Management
- **Single Position Trading**: Only one position open at a time
- **Dynamic Stop Loss**: Calculated to ensure precise step-back to previous balance
- **Consecutive Loss Protection**: Automatic pause after maximum consecutive losses
- **Transparent Logging**: Comprehensive trade and balance tracking

### Nautilus Integration
- **Full Framework Utilization**: Leverages advanced Nautilus Trader capabilities
- **Multiple Execution Modes**: Backtest, demo, and live trading support
- **Real-time Market Data**: Quote tick processing and order management
- **Professional Risk Controls**: Built-in position and order management

## 📊 Strategy Logic

### Balance Progression Example

```
Trade 1: Start with $100 → Win (+30%) → Next trade with $130
Trade 2: $130 → Win (+30%) → Next trade with $169
Trade 3: $169 → Lose (23.08% loss) → Next trade with $130 (step back)
Trade 4: $130 → Lose (23.08% loss) → Next trade with $100 (step back)
```

### Dynamic Loss Calculation

The bot calculates the exact loss percentage needed to return to the previous balance level:

- **At $169**: Loss of 23.08% returns to $130
- **At $130**: Loss of 23.08% returns to $100
- **At $100**: Fixed 30% loss stays at $100

## 🛠 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation Steps

1. **Clone or download the project**:
   ```bash
   cd bots/one_three_melih
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Install development dependencies** (optional):
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install backtest dependencies** (for advanced analysis):
   ```bash
   pip install -e ".[backtest]"
   ```

## 🚀 Usage

### Demo Mode (Recommended for Testing)

Run the bot with simulated market data:

```bash
python main.py --mode demo --initial-balance 100
```

### Backtest Mode

Test the strategy against historical data:

```bash
python main.py --mode backtest --start-date 2024-01-01 --end-date 2024-06-01 --initial-balance 100
```

### Advanced Backtest with Custom Parameters

```bash
python main.py --mode backtest \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --initial-balance 1000
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--mode` | Execution mode: demo, backtest, live | demo |
| `--initial-balance` | Starting balance in USD | 100 |
| `--start-date` | Backtest start date (YYYY-MM-DD) | 2024-01-01 |
| `--end-date` | Backtest end date (YYYY-MM-DD) | 2024-06-01 |
| `--config` | Configuration file path | None |

## 📝 Configuration

### Strategy Configuration

The bot can be configured through the `OneThreeMelihConfig` class:

```python
config = OneThreeMelihConfig(
    instrument_id=InstrumentId.from_str("EUR/USD.SIM"),
    initial_balance=Decimal("100.00"),
    profit_target_percentage=Decimal("30.0"),
    trade_delay_seconds=5,
    max_consecutive_losses=10,
    log_level="INFO",
    enable_detailed_logging=True,
)
```

### Key Parameters

- **initial_balance**: Starting trading balance
- **profit_target_percentage**: Profit target (default: 30%)
- **max_consecutive_losses**: Maximum consecutive losses before pause
- **trade_delay_seconds**: Delay between trades
- **enable_detailed_logging**: Enable comprehensive logging

## 📈 Monitoring and Logging

### Real-time Statistics

The bot provides real-time statistics during execution:

```
=== BALANCE STATISTICS ===
Current Balance: $169.00
Current Step: 3
Total Return: 69.00%
Total Trades: 5
Win Rate: 60.0%
Balance History: [100.0, 130.0, 169.0]
```

### Log Files

- **one_three_melih.log**: Complete trading log with timestamps
- **Console Output**: Real-time trade execution and balance updates

### Trade Logging

Each trade is logged with comprehensive details:

```
=== ENTERING LONG POSITION ===
Entry Price: 1.10450
Position Size: 153
Current Balance: $169.00
Take Profit: 1.11234 (+$50.70)
Stop Loss: 1.09666 (-$39.00)
Stop Loss %: 23.08%
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest test_strategy.py -v
```

### Test Coverage

The test suite covers:
- BalanceTracker logic and calculations
- Step-back balance management
- Dynamic stop loss calculations
- Complete trading scenarios
- Integration testing

### Example Test Scenarios

```python
# Test complete trading progression
def test_complete_trading_scenario():
    tracker = BalanceTracker(Decimal("100.00"), Decimal("30.0"))
    
    # Win, Win, Loss, Win, Loss, Loss
    tracker.record_profit()  # $100 -> $130
    tracker.record_profit()  # $130 -> $169
    tracker.record_loss()    # $169 -> $130 (step back)
    # ... etc
```

## ⚡ Performance Characteristics

### Computational Efficiency
- **Lightweight**: Minimal memory footprint
- **Fast Execution**: Optimized for real-time trading
- **Scalable**: Handles high-frequency quote updates

### Risk Profile
- **Controlled Risk**: Maximum loss per step is predetermined
- **No Leverage**: Pure balance-based position sizing
- **Progressive Growth**: Sustainable profit compounding

## 🔧 Advanced Features

### Nautilus Framework Integration

The bot leverages advanced Nautilus capabilities:

- **Order Management**: Market, limit, and stop orders
- **Position Tracking**: Real-time position monitoring
- **Risk Controls**: Built-in risk management systems
- **Data Processing**: High-performance tick data handling
- **Event-Driven Architecture**: Asynchronous execution

### Extensibility

The modular design allows for easy customization:

```python
# Custom balance progression
class CustomBalanceTracker(BalanceTracker):
    def get_profit_target(self) -> Decimal:
        # Custom profit calculation
        return self.current_balance * Decimal("0.25")  # 25% target
```

## 📊 Expected Performance

### Theoretical Analysis

With a 50% win rate and 30% profit/loss per trade:

- **Break-even**: ~50% win rate
- **Positive expectancy**: Win rate > 50%
- **Risk-adjusted returns**: Limited downside, unlimited upside steps

### Backtesting Results

Results will vary based on market conditions and win rate:

```
Initial Balance: $100.00
Final Balance: $169.00
Total Return: 69.00%
Total Trades: 10
Win Rate: 60.0%
Max Step Reached: 3
```

## ⚠️ Important Considerations

### Risk Warnings

1. **Past Performance**: Does not guarantee future results
2. **Market Risk**: All trading involves risk of loss
3. **Testing Required**: Thoroughly test before live trading
4. **Capital Requirements**: Only trade with capital you can afford to lose

### Best Practices

1. **Start Small**: Begin with small balances for testing
2. **Monitor Performance**: Regularly review trading statistics
3. **Risk Management**: Set appropriate maximum loss limits
4. **Market Conditions**: Consider market volatility and conditions

## 🔄 Updates and Maintenance

### Version History

- **v1.0.0**: Initial release with step-back balance management
- **Future**: Live trading integration, additional instruments

### Contributing

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

For questions, issues, or suggestions:

- Review the code documentation
- Check the test suite for usage examples
- Examine log files for debugging information

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Disclaimer**: This trading bot is for educational and research purposes. Always test thoroughly before using with real money. Trading involves substantial risk of loss.
