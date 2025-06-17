# Nautilus Trader Examples

Bu proje, Nautilus Trader ile farklı borsa ve stratejilerde trading botları geliştirme örneklerini içerir.

## 📋 Proje Yapısı

```
nautilus_trade_examples/
├── docs/                           # Dokümantasyon
│   ├── trading-fundamentals.md     # Trading temel bilgileri
│   ├── risk-management.md          # Risk yönetimi
│   └── bot-guides/                 # Bot geliştirme rehberleri
│       └── binance-spot-testnet.md # Binance Spot Testnet bot rehberi
├── bots/                           # Trading botları
│   ├── binance-spot-testnet/       # Binance Spot Testnet bot
│   ├── binance-futures-testnet/    # (Gelecek)
│   └── arbitrage-bot/              # (Gelecek)
├── docker-compose.yml              # Nautilus Trader container
├── .env.example                    # Environment variables template
└── README.md                       # Bu dosya
```

## 🚀 Hızlı Başlangıç

### 1. Container'ı Başlat
```bash
docker-compose up -d
```

### 2. Container'a Bağlan
```bash
docker exec -it nautilus-trader bash
```

### 3. Bot Projesi Oluştur
```bash
cd /workspace/bots/binance-spot-testnet
uv init my-spot-bot
cd my-spot-bot
uv add nautilus_trader
```

### 4. Environment Variables Ayarla
```bash
cp .env.example .env
# .env dosyasını düzenle ve API keys ekle
```

### 2. İnteraktif Shell

```bash
docker-compose exec nautilus-trader bash
```

### 3. Nautilus Trader Kurulumu (Container içinde)

Container içinde trading projesi oluşturun ve Nautilus Trader'ı ekleyin:

```bash
# Container içinde çalıştır

# 1. YENİ PROJE OLUŞTUR (gerekli!)
uv init my-trading-project

# 2. PROJE DİZİNİNE GİR
cd my-trading-project

# 3. NAUTILUS TRADER EKLE
uv add nautilus_trader

# 4. (İSTEĞE BAĞLI) Redis direct access için
uv add redis

# 5. KURULUMU TEST ET
uv run python -c "import nautilus_trader; print('Nautilus Trader kurulumu başarılı!')"
```

**ÖNEMLİ:** `uv add` komutunu kullanmadan önce mutlaka `uv init` ile proje oluşturmalısınız!

#### Alternatif: Tek Komutla

```bash
# Tek seferde proje oluştur + Nautilus Trader ekle
uv init trading-project && cd trading-project && uv add nautilus_trader
```

### 4. Servisleri Durdurma

```bash
docker-compose down
```

## Yapı

- **Redis**: Market data caching için
- **Nautilus Trader**: Ana trading engine (minimal kurulum)
- **Volumes**: Redis data persistence

## Notlar

- PostgreSQL dahil değildir (isteğiniz üzerine)
- Sadece Redis ile minimal bir kurulum
- Development için hazır
- Orijinal Nautilus .docker yapısına uygun

## Sonraki Adımlar

1. Nautilus repository'den gerekli dosyaları kopyalayın
2. Trading script'lerinizi ekleyin
3. İhtiyaçlarınıza göre genişletin

## Yaygın Hatalar ve Çözümleri

### ❌ Hata: `No pyproject.toml found`
```bash
uv add nautilus_trader
# error: No `pyproject.toml` found in current directory
```

**Çözüm:** Önce proje oluşturun
```bash
uv init my-project
cd my-project
uv add nautilus_trader
```

### ❌ Hata: Container'a bağlanamama
```bash
docker-compose exec nautilus-trader bash
# Error: No such container
```

**Çözüm:** Container'ın çalışıp çalışmadığını kontrol edin
```bash
docker-compose ps
docker-compose up -d  # Eğer çalışmıyorsa
```

### ❌ Hata: `No module named 'redis'`
```bash
# Test script çalıştırırken
python test_setup.py
# ❌ ModuleNotFoundError: No module named 'redis'
```

**Çözüm:** Redis Python client'ını ekleyin
```bash
uv add redis
```

### ✅ Doğru Adım Sırası
1. `docker-compose up -d` - Container'ları başlat
2. `docker exec -it nautilus-trader bash` - Container'a bağlan  
3. `uv init my-project` - Yeni proje oluştur
4. `cd my-project` - Proje dizinine gir
5. `uv add nautilus_trader` - Nautilus Trader ekle
6. `uv run python your_script.py` - Script çalıştır

### 💡 İpuçları

**Test Projeleri İçin:**
```bash
# Git sorunlarını önlemek için geçici test klasörü oluşturun
cd /tmp && uv init test-project && cd test-project
```

**Production Projeleri İçin:**
```bash
# Ana workspace'de gerçek projelerinizi oluşturun
cd /workspace && uv init my-trading-bot && cd my-trading-bot
```

**Paket Açıklamaları:**
- `nautilus_trader`: Ana trading framework (zorunlu)
- `redis`: Redis veritabanına direct erişim için (isteğe bağlı)

### Redis Ne Zaman Gerekli?

✅ **Redis paketi GEREKLİ:**
- Custom caching logic yazıyorsanız
- Redis'ten direkt veri okuyacaksanız  
- Test script'lerini çalıştıracaksanız

❌ **Redis paketi GEREKLİ DEĞİL:**
- Sadece Nautilus Trader kullanıyorsanız
- Basic trading yapıyorsanız

> **Not:** Redis **server** zaten Docker'da çalışıyor. `uv add redis` sadece Python'dan Redis'e bağlanmak için gerekli.

## 📚 Dokümantasyon

- [Trading Bot Geliştirme Temelleri](docs/trading-fundamentals.md)
- [Risk Yönetimi](docs/risk-management.md)
- [Binance Spot Testnet Bot Rehberi](docs/bot-guides/binance-spot-testnet.md)

## ⚠️ Önemli Notlar

- **Güvenlik**: API anahtarlarınızı asla git'e commit etmeyin
- **Testnet**: Gerçek para ile test etmeden önce mutlaka testnet kullanın
- **Risk Yönetimi**: Her zaman stop-loss ve position sizing kullanın
- **Öğrenme**: Küçük miktarlarla başlayın ve adım adım öğrenin

## 🔗 Faydalı Linkler

- [Nautilus Trader Docs](https://nautilustrader.io/)
- [Binance API Docs](https://developers.binance.com/)
- [Binance Testnet](https://testnet.binance.vision/)

---
**Not**: Bu projeler eğitim amaçlıdır. Trading riskleri taşır, kendi sorumluluğunuzda kullanın.
