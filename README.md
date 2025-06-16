# Nautilus Trader - Algoritmik Trading Platform

Bu proje, Nautilus Trader kullanarak algoritmik trading sistemleri geliştirmek için hazırlanmış kapsamlı bir framework'tür.

## 📁 Proje Yapısı

```
nautilus_trade/
├── sandbox/          # Testnet/Sandbox trading ortamı
│   ├── sandbox_trader.py
│   ├── test_setup.py
│   ├── setup_env.py
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env
│   ├── README.md
│   └── SANDBOX.md    # Detaylı sandbox dokümantasyonu
├── live/            # Production/Live trading ortamı (geliştirme aşamasında)
└── .gitignore       # Git güvenlik ayarları
```

## 🎯 Modüller

### 🧪 Sandbox Mode
**Dizin**: `sandbox/`  
**Amaç**: Risk almadan testnet ortamında algoritmik trading stratejilerini test etme

**Özellikler:**
- ✅ Binance Testnet entegrasyonu
- ✅ EMA Cross stratejisi
- ✅ Risk yönetimi
- ✅ Docker desteği
- ✅ Comprehensive logging
- ✅ InstrumentId format düzeltmeleri

**Başlangıç:**
```bash
cd sandbox/
python setup_env.py  # API anahtarlarını ayarla
python test_setup.py  # Kurulumu test et
python sandbox_trader.py  # Sandbox trader'ı başlat
```

### 🚀 Live Mode
**Dizin**: `live/`  
**Amaç**: Production ortamında gerçek para ile trading (geliştirme aşamasında)

**Planlanan Özellikler:**
- 🔄 Gerçek broker entegrasyonları
- 🔄 Gelişmiş risk yönetimi
- 🔄 Multi-strategy support
- 🔄 Portfolio management
- 🔄 Performance analytics
- 🔄 Alert sistemi

## 🚀 Hızlı Başlangıç

### 1. Sandbox Mode ile Başlayın
```bash
# Sandbox klasörüne geçin
cd sandbox/

# Bağımlılıkları yükleyin
pip install -r requirements.txt

# API anahtarlarını ayarlayın
python setup_env.py

# Kurulumu test edin
python test_setup.py

# Trading bot'u başlatın
python sandbox_trader.py
```

### 2. Docker ile Çalıştırma
```bash
cd sandbox/
docker-compose up --build
```

## 📚 Dokümantasyon

- **[sandbox/SANDBOX.md](sandbox/SANDBOX.md)** - Sandbox mode için detaylı rehber
- **[sandbox/README.md](sandbox/README.md)** - Sandbox hızlı başlangıç
- **Nautilus Trader Docs**: https://nautilustrader.io/docs/

## 🔧 Sistem Gereksinimleri

- **Python**: 3.11+
- **Nautilus Trader**: 1.198.0+
- **Docker**: 20.10+ (isteğe bağlı)
- **Redis**: 7.0+ (caching için)
- **PostgreSQL**: 15+ (veritabanı için, isteğe bağlı)

## ⚠️ Güvenlik Notları

- **API Anahtarları**: Asla kodda saklamayın, `.env` dosyası kullanın
- **Testnet**: İlk olarak sandbox mode'da test edin
- **Risk Yönetimi**: Production'da mutlaka risk limitleri ayarlayın
- **Git Güvenliği**: `.gitignore` dosyası hassas bilgileri korur

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 Destek

- **Issues**: GitHub Issues kullanın
- **Dokümantasyon**: [SANDBOX.md](SANDBOX.md) dosyasını kontrol edin
- **Community**: Nautilus Trader Discord topluluğuna katılın

---

**İyi tradeler! 🚀📈**
