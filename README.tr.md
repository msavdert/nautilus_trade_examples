# 🌊 Nautilus Trader - Profesyonel Trading Framework'ü

[![License](https://img.shields.io/badge/license-LGPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-compose-blue.svg)](https://docs.docker.com/compose/)

**Birden fazla ortam desteği ile profesyonel algoritmik trading framework'ü.**

> 🇺🇸 **For English documentation**: [README.md](README.md)

---

## 📁 Proje Yapısı

```
nautilus_trade/
├── README.md                   # İngilizce genel bakış
├── README.tr.md               # Bu dokümantasyon (Türkçe)
├── sandbox/                   # 🧪 Güvenli test ortamı
│   ├── README.md             #    Sandbox dokümantasyonu (İngilizce)
│   ├── README.tr.md          #    Sandbox dokümantasyonu (Türkçe)
│   ├── docker-compose.yml    #    Sandbox deployment
│   ├── sandbox_trader.py     #    Trading bot uygulaması
│   ├── .env                  #    Ortam değişkenleri
│   ├── Dockerfile            #    Container konfigürasyonu
│   └── requirements.txt      #    Python bağımlılıkları
└── live/                     # 🔴 Canlı trading ortamı
    └── (gelecek uygulama)
```

---

## 🧪 Sandbox Ortamı

**Sandbox** ortamı Binance Testnet kullanarak tamamen güvenli test ortamı sağlar:

- **Güvenli Test**: Sanal para kullanır, gerçek fon riski yok
- **Gerçek Market Verisi**: Binance Testnet'ten canlı veri
- **Profesyonel Mimari**: PostgreSQL + Redis + Nautilus Trader
- **EMA Cross Stratejisi**: Kanıtlanmış algoritmik trading stratejisi
- **Docker Container**: Tek komut deployment
- **Kapsamlı Dokümantasyon**: Detaylı kurulum ve kullanım kılavuzu

**👉 Sandbox trading'e başlayın:**

```bash
cd sandbox/
# sandbox dizinindeki detaylı README.tr.md'yi takip edin
```

---

## 🔴 Canlı Ortam

**Canlı** ortam gerçek fonlarla gerçek trading için tasarlanmıştır:

⚠️ **UYARI: Canlı trading gerçek para ve önemli risk içerir!**

- **Gerçek Trading**: Gerçek fonlarla canlı exchange API'leri kullanır
- **Production Mimarisi**: Ölçeklenebilir, izlenen, yedeklenen
- **Gelişmiş Risk Yönetimi**: Artırılmış güvenlik kontrolleri
- **Yasal Uyumluluk**: Trading düzenlemelerine uygun
- **Profesyonel Monitoring**: Gerçek zamanlı uyarılar ve dashboard'lar

**🚧 Durum: Geliştirme Aşamasında**

Canlı ortam şu anda geliştirme aşamasındadır. Şimdilik test ve geliştirme için sandbox ortamını kullanın.

---

## 🚀 Hızlı Başlangıç

### Sandbox Test İçin

```bash
# 1. Sandbox'a git
cd sandbox/

# 2. Tam kurulum kılavuzunu takip et
cat README.tr.md

# 3. Hızlı başlangıç (.env kurulumu gerekli)
docker-compose up -d
```

### Geliştirme İçin

```bash
# 1. Repository'yi klonla
git clone <repository-url>
cd nautilus_trade

# 2. Ortamınızı seçin
cd sandbox/     # Güvenli test için
# cd live/      # Gerçek trading için (gelecek)

# 3. Ortama özel dokümantasyonu takip edin
```

---

## 🛠️ Geliştirme Felsefesi

Bu proje **çoklu ortam yaklaşımı** takip eder:

1. **Önce Sandbox**: Canlı trading öncesi her zaman sandbox'ta test
2. **Manuel Kontrol**: Otomatik script yok - her şeyi siz kontrol ediyorsunuz
3. **Şeffaf Konfigürasyon**: Tüm ayarlar görünür ve yapılandırılabilir
4. **Profesyonel Mimari**: İlk günden production-ready
5. **Güvenlik Öncelikli**: Çoklu koruma ve doğrulama katmanları

---

## 📚 Dokümantasyon

### Tam Kılavuzlar

- **📖 Sandbox Kılavuzu**: `sandbox/README.tr.md` - Tam sandbox dokümantasyonu
- **🔧 API Referansı**: [Nautilus Trader Docs](https://docs.nautilustrader.io/)
- **📊 Strateji Geliştirme**: Sandbox'ta örnekler ve tutorials
- **🔒 Güvenlik Kılavuzu**: Güvenli trading en iyi uygulamaları

### Hızlı Referanslar

- **Docker Komutları**: `docker-compose up/down/logs`
- **Ortam Kurulumu**: `.env` dosya konfigürasyonu
- **Log İzleme**: Gerçek zamanlı sistem monitoring
- **Sorun Giderme**: Yaygın sorunlar ve çözümler

---

## 🤝 Katkıda Bulunma

Hem sandbox hem de canlı ortamlar için katkıları memnuniyetle karşılıyoruz:

1. **Sandbox ile Başlayın**: Değişikliklerinizi önce sandbox'ta test edin
2. **Mimariyi Takip Edin**: Ortamlar arası ayrımı koruyun
3. **Dokümantasyon Ekleyin**: İlgili README dosyalarını güncelleyin
4. **Kapsamlı Test**: Değişikliklerin Docker container'larında çalıştığından emin olun
5. **Güvenlik İncelemesi**: Güvenlik etkilerini değerlendirin

---

## ⚠️ Önemli Notlar

- **Her Zaman Sandbox ile Başlayın**: Asla canlı trading ile başlamayın
- **Manuel Operasyon**: Bu sistem manuel kurulum ve izleme gerektirir
- **Risk Yönetimi**: Tüm trading kararlarından siz sorumlusunuz
- **Otomasyon Yok**: Otomatik script yok - sadece manuel kontrol
- **Eğitim Amaçlı**: Öncelikle algoritmik trading öğrenmek için

---

## 📄 Lisans

Bu proje LGPL-3.0 Lisansı altında lisanslanmıştır.

---

## 🚀 Başlayın

**Algoritmik trading'e başlamaya hazır mısınız?**

```bash
cd sandbox/
cat README.tr.md  # Tam kılavuzu okuyun
```

**İyi Tradeler!** 📈🌊
