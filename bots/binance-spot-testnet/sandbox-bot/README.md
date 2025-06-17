# 🌊 Nautilus Trader - Sandbox EMA Cross Bot

## 📋 Özet

Professional EMA Cross Trading Bot - Binance Spot Testnet üzerinde çalışan tam özellikli sandbox trading botu.

## ✅ Test Sonuçları

### 🎉 Başarıyla Çalışan Özellikler:
- ✅ **Binance Testnet Bağlantısı**: WebSocket ve HTTP bağlantıları çalışıyor
- ✅ **Instrument Loading**: BTCUSDT.BINANCE başarıyla yüklendi (1 instrument loaded)
- ✅ **Market Data Stream**: Gerçek zamanlı trade tick'leri alınıyor
- ✅ **Historical Data**: 1439 adet historical bar verisi alındı
- ✅ **EMA Cross Strategy**: Strateji aktif ve çalışıyor
- ✅ **API Authentication**: Direct API calls çalışıyor (test edildi)

### ⚠️ Bilinen Sorun:
- **API Key Format Issue**: Nautilus Trader'ın internal validation'ında "API-key format invalid" hatası
- **Impact**: Sadece private endpoints (account queries, order placement) etkileniyor
- **Market Data**: Public data tamamen çalışıyor (prices, trades, historical data)

## 🚀 Kullanım

### Container'da Çalıştırma:
```bash
# Container'ı başlat
docker-compose up -d

# Bot'u çalıştır
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance-spot-testnet/sandbox-bot && python main.py"
```

### Yerel Çalıştırma:
```bash
cd bots/binance-spot-testnet/sandbox-bot
python main.py
```

## 📊 Bot Özellikleri

### 📈 Trading Strategy:
- **Strategy**: EMA Cross (Exponential Moving Average Crossover)
- **Timeframe**: 1 dakika
- **Fast EMA**: 10 periyot
- **Slow EMA**: 20 periyot
- **Trade Size**: 0.001 BTC
- **Instrument**: BTCUSDT.BINANCE

### 🛡️ Risk Management:
- **Max Order Submit Rate**: 100/second
- **Max Order Modify Rate**: 100/second
- **Position Management**: Automatic position closing on stop
- **Order Management**: Automatic order cancellation on stop

### 📊 Data Handling:
- **Real-time Data**: Trade ticks, order book updates
- **Historical Data**: 1 gün geriye dönük bar data
- **Cache**: Redis-based high-performance cache
- **Storage**: PostgreSQL for historical data

### 🔐 Security:
- **API Keys**: Testnet-only credentials
- **Environment**: Sandbox mode (no real money)
- **Validation**: Multiple layers of safety checks

## 🔧 Konfigürasyon

### API Credentials (`.env`):
```bash
BINANCE_API_KEY=your_testnet_api_key
BINANCE_SECRET_KEY=your_testnet_secret_key
```

### Trading Parameters:
```bash
BOT_TRADER_ID=SANDBOX-TRADER-001
BOT_INSTRUMENT_ID=BTCUSDT.BINANCE
BOT_TRADE_SIZE=0.001
BOT_FAST_EMA_PERIOD=10
BOT_SLOW_EMA_PERIOD=20
```

### Database Configuration:
```bash
# Redis (Cache & Message Bus)
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL (Historical Data)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=nautilus_trader
```

## 📈 Gerçek Zamanlı Çıktı Örneği

```
🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊
   NAUTILUS TRADER - SANDBOX MODE
🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊🌊

📊 EMA Cross stratejisi ekleniyor...
📈 Trading Pair: BTCUSDT.BINANCE
⏱️ Timeframe: 1 dakika
🔄 Hızlı EMA: 10 periyot
🔄 Yavaş EMA: 20 periyot
💰 Trade Size: 0.001 BTC

🎉 SANDBOX TRADER BAŞARIYLA BAŞLATILDI!
📊 Market verileri alınıyor...
🤖 EMA Cross stratejisi aktif...

[INFO] SANDBOX-TRADER-001.EMACross: Received <Bar[1439]> data for BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL
[INFO] SANDBOX-TRADER-001.EMACross: TradeTick(BTCUSDT.BINANCE,107395.35000000,0.07296000,BUYER,1149302,1750135092192000000)
[INFO] SANDBOX-TRADER-001.EMACross: TradeTick(BTCUSDT.BINANCE,107395.36000000,0.01322000,BUYER,1149303,1750135092192000000)
```

## 🐛 Troubleshooting

### API Key Format Error:
Bu sorun Nautilus Trader'ın internal validation'ında oluşuyor. API anahtarları Binance'de çalışıyor ancak Nautilus Trader'ın validasyonunu geçemiyor.

**Geçici Çözüm**: Market data tamamen çalışıyor, sadece private endpoints etkileniyor.

### Connection Issues:
```bash
# Container'ları yeniden başlat
docker-compose down && docker-compose up -d

# Logs'ları kontrol et
docker logs nautilus-trader
```

### Dependencies:
```bash
# Container'da eksik paketleri kur
docker exec -it nautilus-trader pip install python-dotenv requests
```

## 📁 Dosya Yapısı

```
sandbox-bot/
├── main.py          # Ana bot dosyası
├── pyproject.toml   # Python dependencies
├── .env             # Environment variables
└── README.md        # Bu dosya
```

## 🔄 Next Steps

1. **API Key Issue**: Nautilus Trader repository'sine issue açılabilir
2. **Alternative Testing**: Mock data ile test yapılabilir
3. **Strategy Enhancement**: EMA parameters optimize edilebilir
4. **Risk Management**: Stop-loss ve take-profit eklenebilir
5. **Monitoring**: Grafana dashboard eklenebilir

## 📞 Support

Bu sandbox bot, Nautilus Trader framework'ü üzerinde geliştirilmiştir. Daha fazla bilgi için:
- [Nautilus Trader Documentation](https://nautilustrader.io/)
- [Binance Testnet](https://testnet.binance.vision/)
- [Docker Documentation](https://docs.docker.com/)

---

**⚠️ UYARI**: Bu bot sadece **TESTNET** modu için tasarlanmıştır. Gerçek para ile işlem yapmaz.
