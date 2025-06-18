# My First Bot

A simple trading bot built with Nautilus Trader for learning purposes.

## 📋 What This Bot Does

This is a basic moving average strategy that:
- Monitors EUR/USD price movements
- Calculates a 10-period simple moving average
- Buys when price is above the moving average
- Sells when price is below the moving average

## 🚀 Quick Test

```bash
# Test the strategy definition
uv run python main.py
```

## 📚 Learn More

For a complete step-by-step tutorial, see:
- [English Guide](../../docs/bot-guides/my-first-bot.md)
- [Turkish Guide](../../docs/bot-guides/my-first-bot.tr.md)

## ⚠️ Important

This is a **learning example only**. Do not use this strategy with real money without proper testing and risk management.

## 📁 Files

- `main.py` - The main bot implementation
- `pyproject.toml` - Project dependencies
- `README.md` - This file

## 🔄 Next Steps

1. Read the complete tutorial in the docs
2. Learn how to backtest this strategy
3. Add risk management features
4. Test on a testnet environment
