# Nautilus Trader - Sandbox Mode Hızlı Başlangıç

Bu klasör, Nautilus Trader ile sandbox (testnet) modunda live trading simulation yapmak için gerekli tüm dosyaları içerir.

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 2. API Anahtarlarını Ayarla
```bash
# Etkileşimli kurulum
python setup_env.py

# Veya manuel olarak .env dosyasını düzenle
# BINANCE_TESTNET_API_KEY=your_api_key_here
# BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

### 3. Kurulumu Test Et
```bash
python test_setup.py
```

### 4. Sandbox Trader'ı Başlat
```bash
# Direkt Python ile
python sandbox_trader.py

# Veya Docker ile
docker-compose up --build
```

## 📁 Dosya Açıklamaları

| Dosya | Açıklama |
|-------|----------|
| `sandbox_trader.py` | Ana trading botu - EMA Cross stratejisi |
| `test_setup.py` | Kurulum test scripti |
| `setup_env.py` | API anahtarı kurulum yardımcısı |
| `.env` | API anahtarları (GİT'E COMMIT ETMEYİN!) |
| `docker-compose.yml` | Docker Compose konfigürasyonu |
| `Dockerfile` | Docker image tanımı |
| `requirements.txt` | Python bağımlılıkları |
| `SANDBOX.md` | Detaylı dokümantasyon ve troubleshooting |

## ⚠️ Önemli Notlar

- **SADECE TESTNET**: Bu kodlar sadece Binance testnet ile çalışır
- **GERÇEK PARA KULLANILMAZ**: Tüm işlemler simulation'dır
- **API GÜVENLİĞİ**: .env dosyasını asla git'e commit etmeyin
- **BAŞLATMADAN ÖNCE**: Mutlaka `test_setup.py` çalıştırın

## 🔧 Sorun Giderme

### InstrumentId Hatası
```
❌ Hata: Error parsing InstrumentId from 'USD': missing '.' separator
```
**Çözüm**: Enstrümanlar `symbol.venue` formatında olmalı (örn: `BTCUSDT.BINANCE`)

### API Anahtarı Hatası
```
❌ API anahtarları bulunamadı!
```
**Çözüm**: `.env` dosyasını kontrol edin veya `python setup_env.py` çalıştırın

### Import Hatası
```
❌ nautilus_trader import edilemedi
```
**Çözüm**: `pip install -r requirements.txt` ile bağımlılıkları yükleyin

## 📚 Daha Fazla Bilgi

- **Detaylı Dokümantasyon**: `SANDBOX.md` dosyasını okuyun
- **Binance Testnet**: https://testnet.binance.vision/
- **Nautilus Trader Docs**: https://nautilustrader.io/docs/

## 🎯 Örnekle Test

```bash
# 1. Kurulumu test et
python test_setup.py

# 2. Eğer testler başarılıysa, trader'ı başlat
python sandbox_trader.py

# 3. Ctrl+C ile durdur
```

**Başarılı çıktı örneği:**
```
🚀 Nautilus Trader Sandbox başlatılıyor...
📡 Binance Testnet'e bağlanılıyor...
✅ Sandbox Trader başlatıldı!
📊 Market verileri alınıyor...
🤖 EMA Cross stratejisi aktif...
📈 Trading pair: BTCUSDT.BINANCE
💰 Trade size: 0.001 BTC
⏹️  Durdurmak için Ctrl+C basın
```

## 🐳 Docker ile Çalıştırma

```bash
# Tüm servisleri başlat (Redis + PostgreSQL + Nautilus)
docker-compose up --build

# Logları izle
docker-compose logs -f nautilus-sandbox-trader

# Durdur
docker-compose down
```

İyi tradeler! 🚀📈
