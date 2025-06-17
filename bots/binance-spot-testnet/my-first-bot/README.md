# My First Binance Spot Testnet Bot ✅

Bu bot Nautilus Trader ile Binance Spot Testnet'te çalışan basit bir trading bot'tur. Sandbox modu kullanarak gerçek para riski olmadan trading test edilebilir.

## ✅ Working Features

- ✅ Binance Spot Testnet connection
- ✅ Sandbox execution (simulated trading) 
- ✅ Instrument discovery (1445+ trading pairs loaded)
- ✅ Portfolio management (1000 USDT, 0.01 BTC başlangıç bakiyeleri)
- ✅ Strategy framework working
- ✅ Proper error handling and graceful shutdown
- ✅ Testnet WebSocket limitations handled correctly

## 🏃‍♂️ How to Run

### 1. Prerequisites
- Root dizindeki `.env` dosyasında Binance testnet API anahtarları olmalı
- Docker containers çalışır durumda

### 2. Start the Bot

```bash
# Root workspace directory'den
cd /path/to/workspace

# Docker containers'ı başlat
docker compose up -d

# Bot'u çalıştır
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance-spot-testnet/my-first-bot && uv run python main.py"
```

### 3. Expected Output

Bot başarıyla başladığında şunları göreceksiniz:

```
🚀 Starting Nautilus Trader bot...
📖 Press CTRL+C to stop the bot gracefully

2025-06-17T03:17:29.466809429Z [INFO] TESTER-001.TestStrategy: Spot balances
{
    "USDT": "AccountBalance(total=1_000.00000000 USDT, locked=0.00000000 USDT, free=1_000.00000000 USDT)",
    "BTC": "AccountBalance(total=0.01000000 BTC, locked=0.00000000 BTC, free=0.01000000 BTC)"
}
2025-06-17T03:17:29.466815804Z [INFO] TESTER-001.TestStrategy: 📊 Testnet Environment - Limited market data
2025-06-17T03:17:29.466816595Z [INFO] TESTER-001.TestStrategy: ℹ️  Real-time streams not available on testnet (this is normal)
2025-06-17T03:17:29.466817262Z [INFO] TESTER-001.TestStrategy: 🤖 Bot is running in simulation mode...
```

### 4. Stop the Bot

Bot'u durdurmak için `CTRL+C` tuşlayın. Graceful shutdown yapacak:

```
🔄 Shutting down bot...
✅ Bot shutdown complete
ℹ️  Bot shutdown completed (normal cleanup)
```

## � What This Bot Does

1. **Connects to Binance Testnet** - Gerçek Binance testnet API'sine bağlanır
2. **Loads Instruments** - ~1445 trading çiftini yükler
3. **Sandbox Trading** - Gerçek para kullanmadan simulated trading yapar
4. **Portfolio Tracking** - Anlık bakiye ve pozisyonları takip eder
5. **Simulation Mode** - Testnet limitasyonları nedeniyle simulation mode'da çalışır

## 🔧 Technical Details

- **Data Client**: BinanceDataClientConfig (testnet mode)
- **Execution Client**: SandboxExecutionClientConfig (simulated)
- **Strategy**: TestStrategy (basic logging and monitoring)
- **Instrument**: BTCUSDT.BINANCE
- **Starting Balance**: 1000 USDT + 0.01 BTC
- **Environment**: Testnet (no real money at risk)

## 🚀 Next Steps

1. **Add Trading Logic** - Strategy'ye gerçek trading logic'i ekleyin
2. **Risk Management** - Stop loss, take profit ekleyin
3. **Multiple Instruments** - Birden fazla trading çifti ekleyin
4. **Advanced Strategies** - SMA crossover, RSI, MACD gibi indikatörler
5. **Backtesting** - Tarihsel verilerle test yapın
6. **Production Migration** - Real Binance API'sine geçiş

## 📋 Understanding Testnet Limitations

**Normal ve Beklenen Davranışlar:**
- ⚠️ WebSocket real-time data streams testnet'te sınırlı 
- ✅ Instrument loading ve discovery çalışıyor
- ✅ Portfolio management tam çalışıyor  
- ✅ Order execution simulation çalışıyor
- ✅ Strategy framework tam operasyonel

Bu bot başarıyla Nautilus Trader'ın sandbox özelliklerini kullanarak Binance testnet integration'ını gösteriyor.

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate

# Dependencies yükle
pip install -e .

# Bot'u çalıştır
python main.py
```

## ⚠️ Güvenlik Notları

- Bu bot **TESTNET** modunda çalışır
- Gerçek para kullanmaz
- API anahtarlarınızı güvende tutun
- `.env` dosyasını Git'e commit etmeyin

## 📊 İzleme

Bot çalışırken şunları görürsünüz:
- Indicator değerleri (Fast/Slow SMA)
- Buy/Sell sinyalleri
- Order execution durumları
- Risk management kontrolleri

## 🔧 Parametreleri Değiştirme

`.env` dosyasında bu parametreleri ayarlayabilirsiniz:
- `BOT_FAST_SMA_PERIOD`: Hızlı SMA periyodu (default: 10)
- `BOT_SLOW_SMA_PERIOD`: Yavaş SMA periyodu (default: 20)
- `BOT_TRADE_SIZE`: Trade boyutu (default: 0.001 BTC)
- `BOT_INSTRUMENT_ID`: Trading çifti (default: BTCUSDT.BINANCE)

## 🐛 Hata Ayıklama

Common issues:
- **API Key Error**: Testnet API key'lerini kontrol edin
- **Connection Error**: Internet bağlantınızı kontrol edin
- **Insufficient Balance**: Testnet hesabınızda yeterli USDT olduğundan emin olun

## 📈 Sonraki Adımlar

Bu bot'u geliştirmek için:
1. Daha karmaşık indicator'lar ekleyin (RSI, MACD, etc.)
2. Risk yönetimi kuralları ekleyin (stop-loss, take-profit)
3. Multiple timeframe analizi
4. Notification sistemi (Discord, Telegram)
5. Backtesting sonuçları
