# My First Binance Spot Testnet Bot 🚀

Bu klasör Nautilus Trader ile Binance Spot Testnet'te çalışan basit bir trading bot içerir. Sandbox modu kullanarak **gerçek para riski olmadan** trading test edilebilir.

## ✅ Working Features

- ✅ Binance Spot Testnet connection
- ✅ Sandbox execution (simulated trading) 
- ✅ Instrument discovery (1445+ trading pairs loaded)
- ✅ Portfolio management (1000 USDT, 0.01 BTC başlangıç bakiyeleri)
- ✅ Strategy framework working
- ✅ Proper error handling and graceful shutdown
- ✅ Testnet WebSocket limitations handled correctly
- ✅ UV package management

## 📋 Prerequisites

Bu bot'u çalıştırmadan önce:

1. **Docker ve Docker Compose** yüklü olmalı
2. **Binance Testnet hesabı** olmalı
3. **Binance Testnet API Keys** alınmış olmalı

## 🚀 Step-by-Step Setup

### 1. Binance Testnet API Keys Alın

1. [Binance Testnet](https://testnet.binance.vision/) sitesine gidin
2. GitHub ile login olun
3. "Generate HMAC_SHA256 Key" butonuna tıklayın
4. API Key ve Secret Key'i kopyalayın

### 2. Environment Variables Setup

Root workspace dizininde `.env` dosyası oluşturun:

```bash
# Root workspace dizinine git
cd /path/to/nautilus_trade_examples

# .env.example dosyasını kopyala
cp .env.example .env

# .env dosyasını edit edin
nano .env  # veya tercih ettiğiniz editor
```

`.env` dosyasında şu değerleri güncelleyin:

```bash
# Binance Testnet API Credentials
BINANCE_TESTNET_API_KEY=your_actual_testnet_api_key_here
BINANCE_TESTNET_SECRET_KEY=your_actual_testnet_secret_key_here

# Bot Configuration (isteğe bağlı değiştirilebilir)
BOT_INSTRUMENT_ID=BTCUSDT.BINANCE
BOT_TRADE_SIZE=0.001
```

⚠️ **ÖNEMLİ**: Bu gerçek API key'leriniz olmalı, "your_actual_*" yazısını değiştirin!

### 3. Docker Environment'ı Başlatın

```bash
# Docker containers'ı başlat
docker-compose up -d

# Container'ların çalıştığını kontrol edin
docker ps
```

Şunları görmelisiniz:
- `nautilus-trader` (main container)
- `nautilus-redis` (cache)

### 4. Bot'u Çalıştırın

```bash
# Bot'u container içinde çalıştır
docker exec -it nautilus-trader bash -c "cd /workspace/bots/binance-spot-testnet/my-first-bot && uv run main.py"
```

## 📊 Expected Output

Bot başarıyla başladığında şunları göreceksiniz:

```bash
🚀 Starting Nautilus Trader bot...
📖 Press CTRL+C to stop the bot gracefully

Initialized tracing logs with RUST_LOG=off
2025-06-17T03:17:29.466809429Z [INFO] TESTER-001.TestStrategy: Spot balances
{
    "USDT": "AccountBalance(total=1_000.00000000 USDT, locked=0.00000000 USDT, free=1_000.00000000 USDT)",
    "BTC": "AccountBalance(total=0.01000000 BTC, locked=0.00000000 BTC, free=0.01000000 BTC)"
}
2025-06-17T03:17:29.466815804Z [INFO] TESTER-001.TestStrategy: 📊 Testnet Environment - Limited market data
2025-06-17T03:17:29.466816595Z [INFO] TESTER-001.TestStrategy: ℹ️  Real-time streams not available on testnet (this is normal)
2025-06-17T03:17:29.466817262Z [INFO] TESTER-001.TestStrategy: 🤖 Bot is running in simulation mode...
```

Bu output **normal ve beklenen** davranıştır!

## 🛑 Bot'u Durdurma

Bot'u durdurmak için `CTRL+C` tuşlayın:

```bash
^C🛑 Shutdown requested by user (CTRL+C)
🔄 Shutting down bot...
✅ Bot shutdown complete
ℹ️  Bot shutdown completed (normal cleanup)
```

## 🔧 File Structure

```
my-first-bot/
├── main.py           # Ana bot dosyası
├── config.py         # Konfigürasyon yöneticisi  
├── strategy.py       # Trading stratejisi (TestStrategy)
├── mock_data.py      # Mock data generator (gelecek için)
├── pyproject.toml    # UV project configuration
├── uv.lock          # UV lock file
└── README.md        # Bu dosya
```

## 📈 What This Bot Does

1. **Connects to Binance Testnet** - Güvenli testnet API'sine bağlanır
2. **Loads Instruments** - ~1445 trading çiftini yükler (BTCUSDT, ETHUSDT, etc.)
3. **Sandbox Trading** - Gerçek para kullanmadan simulated orders
4. **Portfolio Tracking** - Anlık bakiye ve pozisyonları monitor eder
5. **Simulation Mode** - Testnet limitasyonları nedeniyle simulation mode

## ⚙️ Bot Configuration

`.env` dosyasında değiştirebileceğiniz parametreler:

```bash
# Trading Instrument
BOT_INSTRUMENT_ID=BTCUSDT.BINANCE    # Hangi coin pair

# Trading Size  
BOT_TRADE_SIZE=0.001                 # Order boyutu (BTC cinsinden)

# Testnet API (zorunlu)
BINANCE_TESTNET_API_KEY=...          # Your testnet API key
BINANCE_TESTNET_SECRET_KEY=...       # Your testnet secret
```

## 🐛 Troubleshooting

### Common Issues:

**1. API Key Error:**
```bash
[ERROR] Invalid API credentials
```
➡️ **Çözüm**: `.env` dosyasında API key'leri kontrol edin

**2. Docker Container Not Found:**
```bash
Error response from daemon: No such container: nautilus-trader
```
➡️ **Çözüm**: `docker-compose up -d` komutunu çalıştırın

**3. UV Command Not Found:**
```bash
uv: command not found
```
➡️ **Çözüm**: Container içinde çalıştırdığınızdan emin olun

## 🚀 Next Development Steps

1. **Real Trading Logic**: Strategy'ye SMA, RSI, MACD ekleyin
2. **Risk Management**: Stop-loss, take-profit implementasyonu
3. **Multiple Instruments**: Birden fazla coin pair'i monitor edin
4. **Backtesting**: Historical data ile strategy test
5. **Production Migration**: Real Binance API'sine geçiş

## 📋 Understanding Testnet

**Normal ve Beklenen Davranışlar:**
- ⚠️ WebSocket real-time data streams sınırlı (normal)
- ✅ Instrument loading çalışıyor
- ✅ Portfolio management çalışıyor  
- ✅ Order simulation çalışıyor
- ✅ Strategy framework operasyonel

**Testnet vs Production:**
- Testnet: Fake money, limited features, safe testing
- Production: Real money, full features, real trading

## ⚠️ Security & Safety

- ✅ Bu bot **sadece TESTNET** kullanır
- ✅ **Gerçek para riski YOK**
- ⚠️ API key'lerinizi kimseyle paylaşmayın
- ⚠️ `.env` dosyasını Git'e commit etmeyin (`.gitignore`'da)

---

🎯 **Bu bot Nautilus Trader ecosystem'ini öğrenmek ve trading strategy geliştirme için mükemmel bir başlangıç noktasıdır!**
