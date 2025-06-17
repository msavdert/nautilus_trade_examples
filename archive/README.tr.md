# 🌊 Nautilus Trader - Profesyonel Sandbox Trading Sistemi

[![License](https://img.shields.io/badge/license-LGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)
[![Binance](https://img.shields.io/badge/exchange-Binance%20Testnet-yellow.svg)](https://testnet.binance.vision/)

**Nautilus Trader framework'ü üzerine kurulmuş profesyonel algoritmik trading sistemi. EMA Cross stratejisi, PostgreSQL veri saklama ve Redis cache ile Binance Testnet üzerinde tamamen güvenli test ortamı.**

> 🇺🇸 **For English documentation**: [README.md](README.md)

---

## 🌟 Özellikler

- **Güvenli Test Ortamı**: Binance Testnet kullanır - gerçek para riski yok
- **Profesyonel Mimari**: Endüstri standardı Nautilus Trader framework'ü üzerine kurulu
- **EMA Cross Stratejisi**: 10/20 periyot üssel hareketli ortalama ile kanıtlanmış algoritma
- **Tam Altyapı**: PostgreSQL ile historical data, Redis ile real-time cache
- **Docker Container**: docker-compose ile tek komut deployment
- **Risk Yönetimi**: Kayıpları önleyen yerleşik güvenlik kontrolleri
- **Gerçek Zamanlı Market Data**: Binance Testnet'ten canlı veri akışı
- **Kapsamlı Loglama**: Monitoring ve debugging için detaylı loglar
- **Production Hazır**: Gerçek trading için uygun ölçeklenebilir mimari

---

## 🚀 Hızlı Başlangıç

### Gereksinimler

- **Docker & Docker Compose** yüklü
- **Binance Testnet Hesabı**
- **Git** repository'yi klonlamak için

### 1. Binance Testnet API Kurulumu

1. [Binance Testnet](https://testnet.binance.vision/) sitesine gidin
2. Hesap oluşturun veya giriş yapın
3. API Key ve Secret oluşturun
4. Bu dizinde `.env` dosyası oluşturun:

```bash
# .env
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_api_secret_here
```

### 2. Trading Sistemini Başlat

```bash
# Tüm servisleri başlat (PostgreSQL, Redis, Trading Bot)
docker-compose up -d

# Logları gerçek zamanlı izle
docker-compose logs -f nautilus-sandbox-trader
```

### 3. Sistemi İzle

```bash
# Servis durumunu kontrol et
docker-compose ps

# PostgreSQL loglarını görüntüle
docker-compose logs -f nautilus-postgres

# Redis loglarını görüntüle
docker-compose logs -f nautilus-redis

# Tüm servisleri durdur
docker-compose stop

# Tüm container'ları kaldır (data korunur)
docker-compose down
```

---

## 📊 Trading Stratejisi

### EMA Cross Stratejisi

Sistem kanıtlanmış **EMA Cross Stratejisi** kullanır:

**Strateji Bileşenleri:**
- **Hızlı EMA**: 10 periyot üssel hareketli ortalama (kısa vadeli trengler)
- **Yavaş EMA**: 20 periyot üssel hareketli ortalama (uzun vadeli trengler)
- **Zaman Dilimi**: Hızlı tepki için 1 dakikalık mumlar
- **Trading Çifti**: BTCUSDT.BINANCE (en likit çift)

**Trading Sinyalleri:**
- **ALIŞ Sinyali**: Hızlı EMA, Yavaş EMA'nın üzerine geçer (Golden Cross)
- **SATIŞ Sinyali**: Hızlı EMA, Yavaş EMA'nın altına geçer (Death Cross)

**Risk Yönetimi:**
- **Trade Büyüklüğü**: Trade başına 0.001 BTC (~$30-50 test miktarı)
- **Maksimum Emir**: Saniyede 10 emir limiti
- **Pozisyon Limiti**: Emir başına maksimum $1000
- **Stop Loss**: Nautilus risk engine ile otomatik

---

## 🏗️ Mimari

### Sistem Bileşenleri

```
┌─────────────────────────────────────────────────────────────┐
│                 Nautilus Trader Sandbox                    │
├─────────────────────────────────────────────────────────────┤
│  📊 Trading Bot (sandbox_trader.py)                        │
│  ├── EMA Cross Stratejisi                                  │
│  ├── Risk Yönetim Motoru                                   │
│  ├── Emir Yönetim Sistemi                                  │
│  └── Gerçek Zamanlı Market Data İşleme                     │
├─────────────────────────────────────────────────────────────┤
│  🏦 PostgreSQL Veritabanı                                  │
│  ├── Historik OHLCV Verisi                                 │
│  ├── Emir & Trade Geçmişi                                  │
│  ├── Pozisyon & Portföy Verisi                             │
│  └── Strateji Performans Metrikleri                        │
├─────────────────────────────────────────────────────────────┤
│  🚀 Redis Cache                                             │
│  ├── Gerçek Zamanlı Market Verisi                          │
│  ├── Order Book Snapshot'ları                              │
│  ├── Son Trade Verileri                                    │
│  └── Sistem Durum Cache'i                                  │
├─────────────────────────────────────────────────────────────┤
│  📡 Binance Testnet API                                     │
│  ├── Market Data WebSocket                                 │
│  ├── Emir Execution REST API                               │
│  ├── Hesap Bilgileri                                       │
│  └── Gerçek Zamanlı Fiyat Akışı                            │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Konfigürasyon

### Ortam Değişkenleri

Tüm konfigürasyon maksimum şeffaflık ve kontrol için `sandbox_trader.py` içinde merkezileştirilmiştir. Sistem hassas veriler için ortam değişkenleri kullanır:

```bash
# Binance Testnet API
BINANCE_TESTNET_API_KEY=your_api_key
BINANCE_TESTNET_API_SECRET=your_api_secret

# Veritabanı (Docker otomatik ayarlar)
NAUTILUS_DATABASE_HOST=nautilus-postgres
NAUTILUS_DATABASE_PORT=5432
NAUTILUS_DATABASE_NAME=nautilus
NAUTILUS_DATABASE_USER=nautilus
NAUTILUS_DATABASE_PASSWORD=nautilus123

# Cache (Docker otomatik ayarlar)
NAUTILUS_CACHE_DATABASE_HOST=nautilus-redis
NAUTILUS_CACHE_DATABASE_PORT=6379
```

### Strateji Parametreleri

Ana trading parametreleri `sandbox_trader.py` içinde değiştirilebilir:

```python
# EMA Periyotları
fast_ema_period = 10        # Hızlı EMA
slow_ema_period = 20        # Yavaş EMA

# Trading Büyüklüğü
trade_size = Decimal("0.001")  # Trade başına 0.001 BTC

# Trading Çifti
instrument_id = "BTCUSDT.BINANCE"

# Zaman Dilimi
bar_type = "BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL"

# Risk Limitleri
max_order_submit_rate = "10/00:00:01"      # Saniyede 10 emir
max_notional_per_order = Decimal("1000.0") # Emir başına max $1000
```

---

## 📊 İzleme & Loglar

### Log Dosyaları

Sistem izleme için kapsamlı loglar üretir:

```bash
logs/
├── nautilus_trader.log         # Ana trading logları
├── database.log               # Veritabanı operasyonları  
├── redis.log                  # Cache operasyonları
└── errors.log                 # Hata logları
```

### Gerçek Zamanlı İzleme

```bash
# Trading aktivitesini izle
docker-compose logs -f nautilus-sandbox-trader

# Tüm servisleri izle
docker-compose logs -f

# Sistem kaynaklarını kontrol et
docker stats

# PostgreSQL'e doğrudan erişim
docker exec -it nautilus-postgres psql -U nautilus -d nautilus

# Redis'e doğrudan erişim
docker exec -it nautilus-redis redis-cli
```

### Performans Metrikleri

İzlenecek ana metrikler:

- **Emir Gerçekleşme Oranı**: Gerçekleşen vs verilen emirler
- **Strateji Performansı**: Kar/Zarar takibi
- **Gecikme**: Emir gerçekleşme hızı
- **Sistem Sağlığı**: CPU, Bellek, Ağ
- **Veri Kalitesi**: Market data tamlığı

---

## 🛠️ Özelleştirme

### Yeni Strateji Ekleme

Özel strateji uygulamak için:

1. `Strategy` sınıfından türeyen yeni strateji sınıfı oluşturun
2. Gerekli methodları uygulayın: `on_start()`, `on_stop()`, `on_bar()`
3. `sandbox_trader.py` içindeki `create_strategy()` methodunu güncelleyin
4. Strateji parametrelerini yapılandırın

### Yeni Trading Çiftleri Ekleme

```python
# create_config() methodunda
load_ids=frozenset([
    InstrumentId.from_str("BTCUSDT.BINANCE"),
    InstrumentId.from_str("ETHUSDT.BINANCE"),    # Ethereum ekle
    InstrumentId.from_str("ADAUSDT.BINANCE"),    # Cardano ekle
]),
```

### Veritabanı Şema Özelleştirme

Nautilus gerekli tabloları otomatik oluşturur. Özel tablolar için:

```sql
-- data/postgres_init/custom.sql içinde özel tablolar oluşturun
CREATE TABLE IF NOT EXISTS custom_metrics (
    id SERIAL PRIMARY KEY,
    strategy_id VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value DECIMAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔒 Güvenlik En İyi Uygulamaları

**API Güvenliği:**
- ✅ Geliştirme için her zaman Testnet kullanın
- ✅ API anahtarlarını asla version control'e eklemeyin
- ✅ Hassas veriler için ortam değişkenleri kullanın
- ✅ API anahtarlarını düzenli değiştirin
- ✅ Binance'de IP whitelisting'i etkinleştirin

**Sistem Güvenliği:**
- ✅ İzolasyon için Docker kullanın
- ✅ Veritabanını düzenli yedekleyin
- ✅ Olağandışı aktivite için logları izleyin
- ✅ Bağımlılıkları güncel tutun
- ✅ Production için güçlü şifreler kullanın

---

## 🐛 Sorun Giderme

### Yaygın Sorunlar

**1. Container başlamıyor**
```bash
# Docker servisini kontrol et
sudo systemctl status docker

# Logları kontrol et
docker-compose logs nautilus-sandbox-trader

# Container'ları yeniden oluştur
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**2. API Bağlantı Sorunları**
```bash
# .env dosyasındaki API anahtarlarını doğrula
cat .env

# API bağlantısını test et
curl -X GET "https://testnet.binance.vision/api/v3/time"

# Ağ bağlantısını kontrol et
docker exec nautilus-sandbox-trader ping testnet.binance.vision
```

**3. Veritabanı Bağlantı Sorunları**
```bash
# PostgreSQL durumunu kontrol et
docker-compose ps nautilus-postgres

# Veritabanı bağlantısını test et
docker exec -it nautilus-postgres psql -U nautilus -d nautilus -c "SELECT 1;"

# Veritabanını sıfırla
docker-compose down
docker volume rm sandbox_postgres_data
docker-compose up -d
```

**4. Redis Bağlantı Sorunları**
```bash
# Redis durumunu kontrol et
docker-compose ps nautilus-redis

# Redis bağlantısını test et
docker exec -it nautilus-redis redis-cli ping

# Redis cache'ini temizle
docker exec -it nautilus-redis redis-cli FLUSHALL
```

### Debug Modu

```python
# sandbox_trader.py içinde log seviyesini değiştir
logging_config = LoggingConfig(
    log_level="DEBUG",  # INFO'dan DEBUG'a değiştir
    log_colors=True,
)
```

---

## 🔄 Production Deployment

**⚠️ Önemli: Bu sandbox sadece test içindir. Production deployment için:**

1. **Live API'ye Geçiş**: Testnet'ten canlı Binance API'sine geçiş
2. **Güvenliği Artırma**: Güvenli secret yönetimi kullanın
3. **Altyapıyı Ölçeklendirme**: Kubernetes veya Docker Swarm kullanın
4. **Monitoring Ekleme**: Prometheus, Grafana uygulayın
5. **Yedekleme Stratejisi**: Otomatik veritabanı yedekleme
6. **Load Balancing**: Redundancy için çoklu trading node'ları
7. **Yasal Uyumluluk**: Düzenleyici uyumluluğu sağlayın

---

## 📚 Öğrenme Kaynakları

**Nautilus Trader:**
- [Resmi Dokümantasyon](https://nautilustrader.io/)
- [API Referansı](https://docs.nautilustrader.io/)
- [GitHub Repository](https://github.com/nautechsystems/nautilus_trader)

**Algoritmik Trading:**
- [Quantitative Trading Stratejileri](https://www.quantstart.com/)
- [Finans için Python](https://pypi.org/project/yfinance/)
- [Risk Yönetimi](https://www.investopedia.com/terms/r/riskmanagement.asp)

**Teknik Analiz:**
- [Hareketli Ortalamalar](https://www.investopedia.com/terms/m/movingaverage.asp)
- [EMA vs SMA](https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp)

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Repository'yi fork edin
2. Feature branch oluşturun
3. Değişikliklerinizi yapın
4. Gerekirse test ekleyin
5. Pull request gönderin

**İyileştirme alanları:**
- Ek trading stratejileri
- Gelişmiş risk yönetimi
- UI/Dashboard geliştirme
- Performans optimizasyonları
- Dokümantasyon iyileştirmeleri

---

## 📄 Lisans

Bu proje LGPL-3.0 Lisansı altında lisanslanmıştır - detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## ⚠️ Sorumluluk Reddi

**Bu yazılım sadece eğitim ve test amaçlıdır. Trading önemli kayıp riski içerir ve tüm yatırımcılar için uygun değildir. Geçmiş performans gelecekteki sonuçları garanti etmez. Kendi riskinizle kullanın.**

- Bu sanal fonlar kullanan bir Testnet uygulamasıdır
- Bu sandbox'ta gerçek para söz konusu değildir
- Canlı trading öncesi her zaman kapsamlı test yapın
- Yatırım kararları için finansal danışmanlara başvurun
- Yazarlar hiçbir finansal kayıptan sorumlu değildir

---

## 📞 Destek

Destek ve sorular için:

- **Issues**: Bug raporları için GitHub Issues kullanın
- **Discussions**: Sorular için GitHub Discussions kullanın
- **Dokümantasyon**: Resmi Nautilus dokümantasyonunu kontrol edin
- **Topluluk**: Trading ve Python topluluklarına katılın

---

**İyi Tradeler!** 🚀📈
