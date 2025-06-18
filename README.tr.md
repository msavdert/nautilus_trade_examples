# Nautilus Trader Örnekleri

Nautilus Trader ile farklı borsa ve stratejilerde trading botları geliştirme projesi.

## 📋 Proje Yapısı

```
nautilus_trade_examples/
├── docs/                           # Dokümantasyon
│   ├── trading-fundamentals.md     # Trading temel bilgileri
│   ├── risk-management.md          # Risk yönetimi
│   ├── LOGGING.md                  # Loglama rehberi
│   └── bot-guides/                 # Bot geliştirme rehberleri
│       └── binance-spot-testnet.md # Binance Spot Testnet bot rehberi
├── bots/                           # Trading botları
│   └── my-first-bot/               # İlk botunuz (kurulumdan sonra oluşur)
├── docker-compose.yml              # Nautilus Trader container
├── README.md                       # Bu dosya (İngilizce)
├── README.tr.md                    # Türkçe dokümantasyon
└── logs/                           # Uygulama logları
```

## 🚀 Hızlı Başlangıç

Bu proje, Nautilus Trader ile kendi trading botlarınızı sıfırdan geliştirmenizi sağlar.

### 1. Container'ı Başlat
```bash
docker-compose up -d
```

### 2. İlk Botunuzu Oluşturun
```bash
docker exec -it nautilus-trader bash -c "cd /workspace/bots/ && uv init my-first-bot"
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv add nautilus_trader"
```

### 3. Container'a Bağlan (İsteğe Bağlı)
```bash
docker exec -it nautilus-trader bash
```

### 4. Botunuzu Geliştirin
İlk botunuzu oluşturduktan sonra:
- Editörünüzde `bots/my-first-bot/` klasörüne gidin
- `docs/` klasöründeki adım adım dokümantasyonu takip edin
- Nautilus ile sıfırdan trading botu yazmayı öğrenin

## 📚 Dokümantasyon

İlk botunuzu oluşturduktan sonra, adım adım yeni başlayan rehberlerimizi takip edebilirsiniz:

### 🎯 Buradan Başlayın: İlk Botunuz
- **[İlk Botum - Tam Yeni Başlayan Rehberi](docs/bot-guides/my-first-bot.tr.md)** - Sıfırdan basit hareketli ortalama trading botu oluşturmayı öğrenin

### 📚 Ek Dokümantasyon
- Nautilus ile sıfırdan trading botları nasıl yazılır
- Adım adım bot geliştirme rehberleri
- En iyi uygulamalar ve örnekler

## 🛠️ Geliştirme İş Akışı

1. **Başlatma**: Yukarıdaki komutları kullanarak ilk botunuzu oluşturun
2. **Öğrenme**: [İlk Botum rehberini](docs/bot-guides/my-first-bot.tr.md) takip edin
3. **Geliştirme**: Trading stratejilerinizi yazın
4. **Test**: Güvenli test için testnet ortamları kullanın
5. **Dağıtım**: Hazır olduğunuzda canlı trading'e geçin

## 📝 Mevcut Dokümantasyon

- **[İlk Botum Rehberi](docs/bot-guides/my-first-bot.tr.md)** - Tam yeni başlayan eğitimi
- [Trading Temelleri](docs/trading-fundamentals.md)
- [Risk Yönetimi](docs/risk-management.md)
- [Loglama Rehberi](docs/LOGGING.md)
- [Bot Geliştirme Rehberleri](docs/bot-guides/)

## ⚠️ Önemli Notlar

- **Güvenlik**: API anahtarlarınızı asla git'e commit etmeyin
- **Test**: Canlı trading öncesi mutlaka testnet kullanın
- **Risk Yönetimi**: Her zaman stop-loss ve pozisyon büyüklüğü kullanın
- **Öğrenme**: Küçük miktarlarla başlayın ve adım adım öğrenin

## 🔗 Faydalı Linkler

- [Nautilus Trader Dokümantasyonu](https://nautilustrader.io/)
- [Binance API Dokümantasyonu](https://developers.binance.com/)
- [Binance Testnet](https://testnet.binance.vision/)

---

## 🔧 Redis Kurulumu

Redis, market verisi önbellekleme için Docker kurulumuna dahildir ve otomatik olarak yapılandırılır.

### Botunuza Redis Ekleme (İsteğe Bağlı)

Redis **sunucusu** zaten Docker'da çalışıyor. Eğer bot kodunuzda Redis'i direkt kullanmak istiyorsanız, Python Redis client'ını eklemeniz gerekir:

```bash
# Bot dizininize girin
docker exec -it nautilus-trader bash -c "cd /workspace/bots/my-first-bot && uv add redis"
```

Veya zaten container içindeyseniz:
```bash
cd /workspace/bots/my-first-bot
uv add redis
```

### Redis Paketi Ne Zaman Gerekli?

✅ **Redis paketi GEREKLİ:**
- Botunuzda özel önbellekleme mantığı yazıyorsanız
- Redis'ten direkt veri erişimi yapacaksanız
- Redis kullanan test scriptleri çalıştıracaksanız

❌ **Redis paketi GEREKLİ DEĞİL:**
- Temel Nautilus Trader kullanımı için
- Basit trading stratejileri için

> **Not:** Redis **sunucusu** zaten Docker'da çalışıyor. `uv add redis` sadece Python kodunun Redis'e bağlanması için gerekli.

### Redis Bağlantı Detayları
- **Host**: `redis` (container içinden) veya `localhost` (host'tan)
- **Port**: `6379`
- **Veritabanı**: `0` (varsayılan)

### Redis Yönetimi
```bash
# Redis CLI'ye bağlan
docker exec -it redis-server redis-cli

# Redis durumunu kontrol et
docker exec -it redis-server redis-cli ping

# Redis komutlarını izle
docker exec -it redis-server redis-cli monitor
```

### Redis Veri Kalıcılığı
Redis verileri Docker volume'lerinde saklanır ve container yeniden başlatmalarında korunur.

---
**Not**: Bu projeler eğitim amaçlıdır. Trading riskleri taşır, kendi sorumluluğunuzda kullanın.
