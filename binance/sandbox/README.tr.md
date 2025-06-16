# Binance Spot Trading Client

🚀 **Nautilus Trader mimarisinden ilham alınarak geliştirilmiş minimal, modüler ve tamamen dockerize edilmiş Binance Spot trading istemcisi.**

Bu proje, doğru ayrım prensibi ve Docker-öncelikli geliştirme yaklaşımı ile algoritmic ticaret için temiz bir temel sağlar.

## 🌟 Özellikler

- **🐳 Tamamen Dockerize**: Tüm geliştirme, test ve üretim işlemleri Docker container'ları ile
- **📦 Modüler Mimari**: Config, client, strategy ve test modüllerinin temiz ayrımı
- **🔧 Ortam Tabanlı Konfigürasyon**: Tüm gizli anahtarlar ve ayarlar `.env` dosyaları ile yönetilir
- **🎯 Çoklu Ortam Desteği**: Geliştirme, test ve üretim Docker hedefleri
- **📡 Tam Binance Entegrasyonu**: En güncel endpoint'ler ile WebSocket ve REST API
- **🧠 Strateji Framework'ü**: Yerleşik örnekler ile genişletilebilir strateji temel sınıfları
- **🧪 Kapsamlı Test**: Birim testler ve entegrasyon test framework'ü
- **💚 Sağlık İzleme**: Docker sağlık kontrolleri ve uygulama izleme
- **🛡️ Risk Yönetimi**: Pozisyon boyutlandırma, zarar durdurma ve risk kontrolleri

## 🏗️ Mimari

```
src/
├── config.py      # Ortam tabanlı konfigürasyon yönetimi
├── client.py      # Binance REST ve WebSocket API istemcisi
├── strategy.py    # Strateji framework'ü ve implementasyonları
└── main.py        # Ana uygulama giriş noktası

tests/
└── test_basic.py  # Birim ve entegrasyon testleri

Docker Servisleri:
├── binance-client # Üretim trading istemcisi
├── binance-dev    # Geliştirme ortamı
└── binance-test   # Test ortamı
```

## 🚀 Hızlı Başlangıç

### 1. İlk Kurulum

```bash
# Proje dizinine git
cd binance/sandbox

# Ortam şablonunu kopyala
cp .env.example .env

# Konfigürasyonunu düzenle (Binance API kimlik bilgilerini ekle)
nano .env
```

### 2. Temel Konfigürasyon

`.env` dosyanızı Binance API kimlik bilgileriniz ile düzenleyin:

```bash
# Gerekli API Kimlik Bilgileri
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here

# Güvenlik Ayarları (ÖNEMLİ!)
ENVIRONMENT=sandbox
TESTNET=true
STRATEGY_ENABLED=false  # Güvenlik için false ile başlayın

# Trading Konfigürasyonu
DEFAULT_SYMBOLS=BTCUSDT,ETHUSDT,ADAUSDT
MAX_POSITION_SIZE_PERCENT=10.0
STOP_LOSS_PERCENT=2.0
```

### 3. Geliştirme Ortamı

```bash
# Tüm Docker image'larını oluştur
make build
# veya: docker-compose build

# Geliştirme ortamını başlat
make dev
# veya: docker-compose up binance-dev

# Geliştirme shell'ine erişim
make dev-shell
# veya: docker-compose exec binance-dev bash
```

### 4. Test Etme

```bash
# Tüm testleri çalıştır
make test
# veya: docker-compose up binance-test

# Coverage ile testleri çalıştır
make test-cov

# Belirli testleri çalıştır
docker-compose run --rm binance-test python -m pytest tests/test_basic.py -v
```

### 5. Üretim

```bash
# Trading istemcisini başlat
make prod
# veya: docker-compose up binance-client

# Arka planda başlat
make prod-daemon
# veya: docker-compose up -d binance-client

# Logları izle
make prod-logs
# veya: docker-compose logs -f binance-client
```

## 📡 API Entegrasyonu

Bu istemci en güncel Binance Spot API endpoint'lerini kullanır (2024 itibariyle):

### Endpoint'ler
- **Testnet**: `https://testnet.binance.vision`
- **Üretim**: `https://api.binance.com`
- **WebSocket Testnet**: `wss://testnet.binance.vision`
- **WebSocket Üretim**: `wss://stream.binance.com:9443`

### Desteklenen Özellikler
- ✅ Piyasa verisi (ticker, orderbook, klines)
- ✅ Hesap bilgileri
- ✅ Emir yönetimi (ver, iptal et, sorgula)
- ✅ WebSocket akışları (gerçek zamanlı veri)
- ✅ HMAC-SHA256 ile kimlik doğrulama
- ✅ Hız sınırlandırma ve hata yönetimi

## 🎯 Strateji Geliştirme

### Özel Strateji Oluşturma

```python
from src.strategy import BaseStrategy, MarketData

class BenimStratejim(BaseStrategy):
    async def on_market_data(self, data: MarketData):
        # Trading mantığınız burada
        if self.should_buy(data):
            await self.place_order(
                symbol=data.symbol,
                side="BUY", 
                quantity=self.calculate_position_size(data.symbol, data.price)
            )
    
    async def on_order_update(self, order_data):
        # Emir durum güncellemelerini işle
        pass
```

### Yerleşik Stratejiler

- **SimpleBuyHoldStrategy**: Fiyat düşüşlerinde alır, pozisyonları tutar
- **ScalpingStrategy**: Demo scalping stratejisi (sadece eğitim amaçlı)

## 🛡️ Güvenlik ve Risk Yönetimi

### ⚠️ Kritik Güvenlik Notları

1. **Her zaman TESTNET ile başlayın**: `.env` dosyasında `TESTNET=true`
2. **Strateji devre dışı ile başlayın**: `STRATEGY_ENABLED=false`  
3. **Küçük pozisyon boyutları kullanın**: Minimal miktarlarla başlayın
4. **Sürekli izleyin**: Stratejileri hiç yalnız bırakmayın
5. **Kapsamlı kağıt ticaret**: Canlı ticaretten önce tüm mantığı test edin

### Risk Kontrolleri

- Bakiye yüzdesi olarak pozisyon boyutu limitleri
- Zarar durdurma ve kar alma seviyeleri
- Günlük zarar limitleri
- API çağrıları için hız sınırlandırma

## 🧪 Test Framework'ü

### Test Yapısı
```bash
tests/
├── test_basic.py       # Temel işlevsellik testleri
└── test_integration.py # Uçtan uca workflow testleri
```

### Testleri Çalıştırma
```bash
# Tüm testler
make test

# Belirli test kategorileri  
docker-compose run --rm binance-test python -m pytest tests/test_basic.py::TestConfig -v

# Coverage raporu ile
make test-cov

# Debug modu
docker-compose run --rm binance-test python -m pytest --pdb
```

## 📊 İzleme ve Loglama

### Log Yönetimi
- Container logları: `docker-compose logs -f`
- Uygulama logları: `./logs/trading_client.log`
- Yapılandırılabilir seviyelerle yapısal loglama

### Sağlık Kontrolleri
```bash
# Container sağlığını kontrol et
make health

# Kaynak kullanımını izle  
docker stats binance_client

# Uygulama durumu
docker inspect --format='{{.State.Health.Status}}' binance_client
```

## 🔧 Docker Komut Referansı

### Geliştirme İş Akışı
```bash
make dev           # Geliştirme ortamını başlat
make dev-shell     # Geliştirme shell'ine erişim  
make dev-logs      # Geliştirme loglarını görüntüle
```

### Test İş Akışı
```bash
make test          # Tüm testleri çalıştır
make test-unit     # Sadece birim testleri
make test-cov      # Coverage ile çalıştır
make test-debug    # Test hatalarını debug et
```

### Üretim İş Akışı  
```bash
make prod          # Üretim istemcisini başlat
make prod-daemon   # Arka planda başlat
make prod-logs     # Üretim loglarını görüntüle
make prod-stop     # Zarif bir şekilde durdur
```

### Bakım
```bash
make clean         # Container'ları ve volume'ları temizle
make format        # Kodu black ile formatla
make lint          # Flake8 ile lint
make syntax-check  # Python syntax'ını doğrula
```

## 📈 Geliştirme Yol Haritası

### Faz 1: Temel (✅ Tamamlandı)
- [x] Docker altyapısı
- [x] Binance API entegrasyonu
- [x] Temel strateji framework'ü
- [x] Test altyapısı
- [x] Dokümantasyon

### Faz 2: Geliştirme (Sonraki Adımlar)
- [ ] Gelişmiş risk yönetimi
- [ ] Performans analitiği  
- [ ] Veritabanı entegrasyonu
- [ ] Gerçek zamanlı dashboard'lar
- [ ] Uyarı sistemleri

### Faz 3: Gelişmiş Özellikler
- [ ] Makine öğrenmesi entegrasyonu
- [ ] Çoklu borsa desteği
- [ ] Portföy optimizasyonu
- [ ] Backtest framework'ü

## 🤝 Katkıda Bulunma

1. Repository'yi fork edin
2. Bir feature branch oluşturun
3. Yeni işlevsellik için testler ekleyin
4. Tüm testlerin geçtiğinden emin olun
5. Dokümantasyonu güncelleyin
6. Pull request gönderin

## 📚 Kaynaklar

- [Binance Spot API Docs](https://github.com/binance/binance-spot-api-docs)
- [Nautilus Trader](https://github.com/nautechsystems/nautilus_trader)
- [Docker Dokümantasyonu](https://docs.docker.com/)
- [Python Async Programming](https://docs.python.org/3/library/asyncio.html)

## ⚖️ Sorumluluk Reddi

**Bu yazılım sadece eğitim ve araştırma amaçlıdır.** Kripto para ticareti önemli zarar riski içerir. Yazarlar ve katkıda bulunanlar, bu yazılımın kullanımı sonucu oluşabilecek finansal kayıplardan sorumlu değildir.

**Herhangi bir canlı ticaret öncesinde testnet'te kapsamlı test yapın.**

## 📄 Lisans

Bu proje açık kaynak kodludur ve MIT Lisansı altında kullanılabilir.

---

**🎉 Algoritmik ticarete başlamaya hazır mısınız? `make setup` ve `make dev` ile başlayın!**

İngilizce dokümantasyon için [README.md](README.md) dosyasına bakın.
