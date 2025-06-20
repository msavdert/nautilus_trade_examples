# Binance Testnet Automated Trading Bot

## Proje Açıklaması

Bu proje, Nautilus Trading Framework kullanarak Binance Testnet ortamında çalışan kapsamlı bir otomatik trading botu geliştirmektedir. Bot, Binance'te işlem hacmi en yüksek 50 kripto paranın ticaretini yapabilir ve **Volatility Breakout with Volume Confirmation** stratejisini kullanır.

## Seçilen Strateji: Volatility Breakout with Volume Confirmation

### Strateji Açıklaması
Bu strateji, fiyat volatilitesi ve işlem hacmi verilerini kullanarak güçlü momentum hareketlerini tespit eder ve sahte breakout'ları filtreler.

**Çalışma Prensibi:**
1. **ATR (Average True Range)** hesaplayarak volatilite seviyesini ölçer
2. **Bollinger Bands** ile dinamik destek/direnç seviyeleri belirler
3. **Volume confirmation** ile breakout'ların geçerliliğini doğrular
4. **RSI filtreleme** ile aşırı alım/satım seviyelerini kontrol eder

**Neden Bu Strateji Seçildi:**
- ✅ **Test edilebilir**: Basit parametrelerle kontrol edilebilir
- ✅ **Makul risk**: ATR tabanlı stop-loss ve position sizing
- ✅ **Volume validation**: Sahte sinyalleri filtreler
- ✅ **Trend following**: Güçlü momentum'u takip eder
- ✅ **Multi-timeframe**: Farklı zaman dilimlerinde çalışabilir

### Entry Koşulları
- Fiyat Bollinger Band üst/alt bandını kırmalı
- Volume, 20-dönem ortalamasının 1.5 katından fazla olmalı
- RSI aşırı alım/satım bölgesinde olmamalı (30-70 arası)
- ATR ile belirlenen volatilite eşiği aşılmalı

### Exit Koşulları
- Stop-loss: Entry fiyatından 2x ATR uzaklık
- Take-profit: Entry fiyatından 3x ATR hedef
- Trailing stop: ATR'nin 1.5 katı

## Teknik Özellikler

### Desteklenen Fonksiyonlar
- 🔸 **Top 50 Volume Coin Selection**: Binance'te en yüksek işlem hacmine sahip 50 coin otomatik seçimi
- 🔸 **Multi-Symbol Trading**: Eş zamanlı çoklu coin ticareti
- 🔸 **Risk Management**: ATR tabanlı position sizing ve stop-loss
- 🔸 **Real-time Data**: WebSocket ile anlık fiyat ve volume verileri
- 🔸 **Comprehensive Logging**: Detaylı işlem ve hata logları
- 🔸 **Environment Configuration**: Güvenli API key yönetimi

### API Endpoint'ler
```
Testnet Base URL: https://testnet.binance.vision/api
WebSocket URL: wss://stream.testnet.binance.vision/ws
```

## Kurulum ve Konfigürasyon

### 1. Gereksinimler
```bash
pip install nautilus_trader
pip install python-dotenv
pip install requests
```

### 2. API Key Ayarları
Binance Testnet'ten API key alın: https://testnet.binance.vision/

`.env` dosyası oluşturun:
```env
BINANCE_TESTNET_API_KEY=your_testnet_api_key
BINANCE_TESTNET_API_SECRET=your_testnet_api_secret
```

### 3. Konfigürasyon Dosyası
`config.yaml` dosyasında bot parametrelerini ayarlayın:
- İşlem yapılacak coin sayısı
- Risk parametreleri
- Strateji ayarları

## Kullanım

### Demo Modu
```bash
python main.py --mode demo
```

### Live Testnet Modu
```bash
python main.py --mode live
```

### Backtest Modu
```bash
python run_backtest.py
```

### Test Çalıştırma
```bash
python -m pytest tests/ -v
```

## Dosya Yapısı

```
binance/testnet/
├── main.py                    # Ana çalıştırma dosyası
├── strategy.py                # Volatility breakout stratejisi
├── coin_selector.py           # Top 50 volume coin seçici
├── risk_manager.py            # Risk ve para yönetimi
├── config.py                  # Konfigürasyon yönetimi
├── utils.py                   # Yardımcı fonksiyonlar
├── run_backtest.py            # Backtest çalıştırıcı
├── analyze_results.py         # Sonuç analizi
├── tests/
│   ├── test_strategy.py       # Strateji testleri
│   ├── test_coin_selector.py  # Coin seçici testleri
│   └── test_risk_manager.py   # Risk yönetimi testleri
├── config.yaml               # Bot konfigürasyonu
├── .env.example              # Örnek environment dosyası
├── requirements.txt          # Python gereksinimleri
├── pyproject.toml           # Proje konfigürasyonu
└── README.md                # Bu dosya
```

## Risk Uyarıları

⚠️ **ÖNEMLİ UYARILAR:**
- Bu bot test amaçlıdır ve gerçek para kullanılmamalıdır
- Testnet ortamında sanal para ile test edilmiştir
- Gerçek trading öncesi kapsamlı backtesting yapılmalıdır
- Risk yönetimi parametreleri dikkatli ayarlanmalıdır

## Gerçek Binance Ortamına Geçiş

Testnet'ten gerçek Binance'e geçiş için:

1. **API Endpoint'leri değiştirin:**
   ```python
   testnet=False  # config.py içinde
   ```

2. **API Key'leri güncelleyin:**
   - Gerçek Binance hesabından API key alın
   - `.env` dosyasını güncelleyin

3. **Risk parametrelerini gözden geçirin:**
   - Position sizing'ı düşürün
   - Stop-loss seviyelerini sıkılaştırın

4. **Kapsamlı test yapın:**
   - Küçük miktarlarla başlayın
   - İşlemleri yakından takip edin

## Lisans

MIT License - Eğitim ve test amaçlı kullanım içindir.

## Destek

Sorularınız için GitHub Issues kullanın veya dokümantasyonu inceleyin.

---
**⚡ Geliştirici Notu:** Bu bot sürekli geliştirilmekte olup, öneri ve katkılarınızı bekliyoruz!
