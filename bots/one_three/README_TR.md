# One-Three Risk Yönetimi Trading Bot'u

<div align="center">

![Nautilus Trader](https://img.shields.io/badge/Nautilus_Trader-1.218.0+-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Trading](https://img.shields.io/badge/Asset-EUR%2FUSD-orange.svg)

**Nautilus Trader framework'ü kullanarak sabit kar al ve zararı durdur seviyeli disiplinli risk yönetimi uygulayan gelişmiş bir EUR/USD trading bot'u.**

</div>

## 🎯 Strateji Genel Bakış

One-Three Bot, EUR/USD forex ticareti için sistematik bir risk yönetimi yaklaşımı uygular:

- **Sabit Risk Yönetimi**: Her işlemde tam olarak +1.3 pip kar al ve -1.3 pip zararı durdur
- **Pozisyon Büyütme Yok**: Martingale veya ortalama stratejisi olmadan sabit pozisyon boyutları
- **Tek Pozisyon Ticareti**: Kontrolü korumak için aynı anda sadece bir açık işlem
- **Adım Adım Yaklaşım**: Her işlem bağımsız, önceki kayıpları telafi etme girişimi yok
- **Kapsamlı Loglama**: Detaylı performans analizi ile tam işlem geçmişi

### Bu Strateji Neden?

Bu strateji, karı maksimize etmek yerine **tutarlılık ve risk kontrolüne** odaklanır. 1:1 risk-ödül oranı ile sabit seviyeler şunları sağlar:

1. **Öngörülebilir Risk**: Her zaman tam olarak ne kadar kaybedebileceğinizi bilirsiniz
2. **Duygusal Kontrol**: Çıkış noktaları hakkında tahmin yapmama psikolojik baskıyı azaltır
3. **Kolay Analiz**: Basit metrikler performans değerlendirmesini kolay hale getirir
4. **Ölçeklenebilir Framework**: Farklı zaman dilimlerine ve enstrümanlara uyarlanabilir

## 🚀 Hızlı Başlangıç

### Ön Koşullar

- Python 3.11 veya üzeri
- Nautilus Trader 1.218.0+
- En az 8GB RAM (büyük veri setleri ile backtesting için)

### Kurulum

1. **Bu projeyi klonlayın veya indirin:**
   ```bash
   cd /path/to/your/nautilus_trade_examples/bots/
   # one_three klasörü burada olmalı
   ```

2. **Bağımlılıkları yükleyin:**
   ```bash
   cd one_three
   uv sync  # veya pip install -r requirements.txt
   ```

3. **Kurulumu doğrulayın:**
   ```bash
   python one_three_strategy.py
   ```

### İlk Backtest'inizi Çalıştırın

```bash
# Üretilen örnek veri ile backtest çalıştırın
python run_backtest.py

# Script şunları yapacak:
# 1. Gerçekçi EUR/USD tick verisi üretir
# 2. One-Three stratejisini çalıştırır
# 3. Performans sonuçlarını gösterir
# 4. Detaylı logları kaydeder
```

## 📊 Stratejiyi Anlamak

### Giriş Mantığı

Mevcut implementasyon basit bir giriş tetikleyicisi kullanır (demo amaçlı):
- EUR/USD'yi mevcut piyasa fiyatından alır
- İşlemler arası yapılandırılabilir bekleme süresini bekler
- Günlük işlem limitlerini takip eder

**🔧 Özelleştirme Noktası**: `check_entry_conditions()` fonksiyonundaki giriş mantığını tercih ettiğiniz sinyal ile değiştirin:
- Teknik göstergeler (RSI, MACD, Hareketli Ortalamalar)
- Temel analiz tetikleyicileri
- Haber tabanlı sinyaller
- Fiyat aksiyonu kalıpları

### Çıkış Mantığı

**Kar Al**: Kar +1.3 pip'e ulaştığında pozisyonu kapatır
**Zararı Durdur**: Kayıp -1.3 pip'e ulaştığında pozisyonu kapatır

Her iki çıkış da tam risk parametrelerinin korunması için anında gerçekleşme amacıyla piyasa emirleri kullanır.

### Risk Yönetimi Özellikleri

- **Pozisyon Boyutu Kontrolü**: Sabit lot boyutları (yapılandırılabilir)
- **Günlük İşlem Limitleri**: Günde maksimum işlem sayısı
- **Zaman Filtreleri**: İsteğe bağlı işlem saatleri kısıtlamaları
- **Kayma Toleransı**: Yapılandırılabilir maksimum kabul edilebilir kayma
- **Bağlantı İzleme**: Otomatik yeniden bağlanma ve hata yönetimi

## 🛠️ Yapılandırma

### Strateji Yapılandırması

`run_backtest.py` veya `run_live.py` dosyalarında strateji parametrelerini düzenleyin:

```python
strategy_config = OneThreeConfig(
    # Temel ayarlar
    instrument_id="EUR/USD.SIM",
    trade_size=Decimal("100_000"),  # Temel para biriminde pozisyon boyutu
    
    # Risk yönetimi
    take_profit_pips=1.3,  # Kar al seviyesi
    stop_loss_pips=1.3,    # Zararı durdur seviyesi
    
    # İşlem limitleri
    max_daily_trades=20,        # Günde max işlem
    entry_delay_seconds=60,     # İşlemler arası minimum bekleme
    
    # Piyasa zamanlaması (isteğe bağlı)
    enable_time_filter=True,
    trading_start_hour=8,       # İşleme başlama (UTC)
    trading_end_hour=18,        # İşlemi durdurma (UTC)
    
    # Gelişmiş özellikler
    use_tick_data=True,         # Tick seviyesi hassasiyet kullan
    slippage_tolerance=0.5,     # Max kabul edilebilir kayma (pip)
)
```

### Backtesting Yapılandırması

Backtest parametrelerini özelleştirin:

```python
# Veri üretimi
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)
num_ticks = 100_000  # Fiyat tick sayısı

# Hesap ayarları
starting_balance = 100_000  # USD
leverage = 30  # 30:1 kaldıraç
```

## 📈 Backtest Çalıştırma

### Temel Backtest

```bash
python run_backtest.py
```

Bu işlem:
1. Gerçekçi EUR/USD piyasa verisi üretir
2. Stratejiyi varsayılan ayarlarla çalıştırır
3. Performans özetini gösterir
4. Detaylı logları `logs/one_three_backtest.log` dosyasına kaydeder

### Gelişmiş Backtesting

Daha sofistike backtesting için:

1. **Tarihsel Veri Kullanın**: Örnek veri üretimini gerçek tarihsel veri ile değiştirin
2. **Parametre Optimizasyonu**: Farklı pip seviyeleri ve işlem frekanslarını test edin
3. **Çoklu Zaman Dilimleri**: Farklı piyasa koşullarında test edin
4. **Walk-Forward Analizi**: Sağlamlığı doğrulamak için kayan zaman periyotları kullanın

### Beklenen Backtest Sonuçları

1:1 risk-ödül oranı ile, strateji karlı olmak için %50'nin üzerinde kazanma oranına ihtiyaç duyar:

- **%55 Kazanma Oranı**: ~%10 yıllık getiri (maliyetler sonrası)
- **%60 Kazanma Oranı**: ~%20 yıllık getiri (maliyetler sonrası)
- **%65 Kazanma Oranı**: ~%30 yıllık getiri (maliyetler sonrası)

**Not**: Bunlar teorik örneklerdir. Gerçek sonuçlar piyasa koşulları, gerçekleştirme kalitesi ve giriş sinyali etkinliğine bağlıdır.

## 🔴 Canlı İşlem

⚠️ **ÖNEMLİ**: Canlı işlem gerçek para riski içerir. Her zaman önce demo modda kapsamlı test yapın.

### Canlı İşlem Kurulumu

1. **Veri Sağlayıcısını Yapılandırın**: Veri beslenizi eklemek için `run_live.py` dosyasını düzenleyin
2. **Broker'ı Yapılandırın**: Gerçekleştirme venue yapılandırmanızı ekleyin
3. **API Kimlik Bilgilerini Ayarlayın**: API anahtarlarınızı güvenli şekilde saklayın
4. **Demo Modda Test Edin**: Her zaman önce demo hesaplarla test edin

### Desteklenen Broker'lar

Nautilus framework, adaptörler aracılığıyla birçok broker'ı destekler:

- **Interactive Brokers**: Profesyonel seviye gerçekleştirme
- **OANDA**: İyi API'si olan perakende forex broker'ı
- **Binance**: Crypto işlemleri için
- **Diğer Birçoğu**: Tam liste için Nautilus dokümantasyonunu kontrol edin

### Canlı İşlem Komutu

```bash
python run_live.py
```

**Güvenlik Kontrol Listesi**:
- [ ] Demo modda kapsamlı test yapıldı
- [ ] Uygun pozisyon boyutları ayarlandı
- [ ] Günlük kayıp limitleri yapılandırıldı
- [ ] Sistem kararlılığı izlendi
- [ ] Bağlantı sorunları için yedek planlar mevcut

## 📊 Performans Analizi

### Sonuçları Analiz Edin

```bash
python analyze_results.py
```

Bu, şunları üretir:
- **Performans Özeti**: Kazanma oranı, kar faktörü, Sharpe oranı
- **Görsel Grafikler**: Equity eğrisi, K&Z dağılımı, drawdown analizi
- **Detaylı Rapor**: İşlem bazında döküm
- **Risk Metrikleri**: Maksimum drawdown, riske göre ayarlanmış getiriler

### İzlenecek Anahtar Metrikler

1. **Kazanma Oranı**: 1:1 R:R ile karlılık için >%50 olmalı
2. **Kar Faktörü**: Brüt kar ve brüt kayıp oranı (>1.0 gerekli)
3. **Maksimum Drawdown**: En büyük tepe-çukur kayıp periyodu
4. **Sharpe Oranı**: Riske göre ayarlanmış getiri ölçüsü
5. **Ortalama İşlem Süresi**: Pozisyonların ne kadar süre tutulduğu

### Örnek Analiz Çıktısı

```
📊 İŞLEM ÖZETİ
──────────────────────────────
Toplam İşlem:           250
Kazanan İşlem:          152 (%60.8)
Kaybeden İşlem:         98 (%39.2)

💰 KAR & ZARAR
──────────────────────────────
Toplam K&Z:             $5,420.00
Ortalama Kazanç:        $13.00
Ortalama Kayıp:         -$13.00
Kar Faktörü:            1.55

📈 PERFORMANS METRİKLERİ
──────────────────────────────
Sharpe Oranı:           1.82
Max Drawdown:           -$156.00
Kazanma Oranı Hedefi:   >%50 (Gerçek: %60.8) ✅
```

## 🔧 Özelleştirme Kılavuzu

### Giriş Sinyalinizi Ekleme

Basit giriş mantığını tercih ettiğiniz sinyal ile değiştirin:

```python
def check_entry_conditions(self, tick) -> None:
    """Burada özel giriş mantığınız"""
    
    # Örnek: RSI tabanlı giriş
    if self.rsi.value < 30:  # Aşırı satım
        self.enter_long_position()
    elif self.rsi.value > 70:  # Aşırı alım
        self.enter_short_position()
        
    # Örnek: Hareketli ortalama geçişi
    if self.fast_ma.value > self.slow_ma.value:
        self.enter_long_position()
        
    # Örnek: Haber tabanlı giriş
    if self.news_sentiment > 0.7:
        self.enter_long_position()
```

### Teknik Gösterge Ekleme

Nautilus framework birçok yerleşik gösterge sağlar:

```python
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.indicators.ema import ExponentialMovingAverage

# Strateji __init__ metodunuzda:
self.rsi = RelativeStrengthIndex(period=14)
self.fast_ema = ExponentialMovingAverage(period=12)
self.slow_ema = ExponentialMovingAverage(period=26)

# on_bar metodunuzda:
self.rsi.update_raw(bar.close)
self.fast_ema.update_raw(bar.close)
self.slow_ema.update_raw(bar.close)
```

### Risk Parametrelerini Değiştirme

```python
# Volatiliteye dayalı dinamik zararı durdur
def calculate_dynamic_stop_loss(self, current_volatility):
    base_stop = self.config.stop_loss_pips
    volatility_multiplier = min(2.0, current_volatility / 0.0001)
    return base_stop * volatility_multiplier

# Takip eden stop implementasyonu
def update_trailing_stop(self, current_price):
    if self.current_position and self.config.enable_trailing_stop:
        new_stop = current_price - self.config.trailing_stop_distance * self.pip_size
        if new_stop > self.current_stop_loss:
            self.modify_stop_loss(new_stop)
```

## 🐛 Sorun Giderme

### Yaygın Sorunlar

**Sorun**: Strateji veri almıyor
- **Çözüm**: Veri beslemesi yapılandırması ve ağ bağlantısını kontrol edin
- **Debug**: Veri akışını görmek için debug logging'i etkinleştirin

**Sorun**: Emirler gerçekleşmiyor
- **Çözüm**: Broker bağlantısı ve hesap izinlerini doğrulayın
- **Debug**: Loglarda emir red nedenlerini kontrol edin

**Sorun**: Beklenmeyen K&Z hesaplamaları
- **Çözüm**: Broker'ınız için pip değerlerini ve pozisyon boyutlandırmayı doğrulayın
- **Debug**: Giriş/çıkış fiyatlarını logla ve broker beyanları ile karşılaştır

**Sorun**: Yüksek kayma sonuçları etkiliyor
- **Çözüm**: Kayma toleransını ayarlayın veya piyasa emirleri yerine limit emirleri kullanın
- **Debug**: Farklı piyasa seanslarında gerçekleştirme kalitesini izleyin

### Debug Modu

Sorun giderme için detaylı loglama etkinleştirin:

```python
# Yapılandırmanızda:
logging=LoggingConfig(
    log_level="DEBUG",  # "INFO"dan değiştirildi
    log_level_file="DEBUG",
    log_colors=True,
)
```

### Performans Optimizasyonu

Yüksek frekanslı işlem için:

1. **Tick Verisi Kullanın**: En iyi hassasiyet için `use_tick_data=True` ayarlayın
2. **Göstergeleri Optimize Edin**: Yerleşik Nautilus göstergelerini kullanın (pandas'tan daha hızlı)
3. **Loglama Azaltın**: Üretim için "ERROR" seviyesi kullanın
4. **Veritabanı Backend**: Üretimde durum kalıcılığı için Redis kullanın

## 📚 İleri Öğrenme

### Nautilus Trader Kaynakları

- **Resmi Dokümantasyon**: [nautilustrader.io/docs](https://nautilustrader.io/docs)
- **GitHub Repository**: [github.com/nautechsystems/nautilus_trader](https://github.com/nautechsystems/nautilus_trader)
- **Discord Topluluğu**: [discord.gg/NautilusTrader](https://discord.gg/NautilusTrader)
- **Örnekler**: Ana repository'deki `examples/` dizinini kontrol edin

### İşlem Stratejisi Geliştirme

- **Backtesting En İyi Pratikleri**: Aşırı uydurmadan kaçının, sample dışı test kullanın
- **Risk Yönetimi**: Pozisyon boyutlandırma, korelasyon analizi, portföy yönetimi
- **Piyasa Mikroyapısı**: Spread'leri, kaymayı ve piyasa etkisini anlamak
- **Algoritma Geliştirme**: Olay güdümlü programlama, durum yönetimi

### Önerilen Okumalar

- "Algorithmic Trading" - Ernie Chan
- "Quantitative Trading" - Ernie Chan
- "The Elements of Statistical Learning" - Hastie, Tibshirani, ve Friedman
- "Building Winning Algorithmic Trading Systems" - Kevin Davey

## 🤝 Katkıda Bulunma

One-Three stratejisini geliştirmek için katkıları memnuniyetle karşılıyoruz:

1. **Hata Düzeltmeleri**: Sorunları bildirin veya düzeltmeler gönderin
2. **Özellik Eklemeleri**: Yeni risk yönetimi özellikleri, göstergeler veya analiz araçları
3. **Dokümantasyon**: Açıklamaları geliştirin veya örnekler ekleyin
4. **Test**: Test vakaları ekleyin veya farklı piyasalarda doğrulayın

### Geliştirme Kurulumu

```bash
# Geliştirme bağımlılıklarını yükle
uv sync --dev

# Testleri çalıştır
pytest tests/

# Kod formatlama
black *.py
ruff check *.py
```

## ⚠️ Sorumluluk Reddi

**Önemli Risk Uyarısı**:

- Forex ticareti önemli risk taşır ve tüm yatırımcılar için uygun olmayabilir
- Geçmiş performans gelecekteki sonuçların göstergesi değildir
- Bu yazılım eğitim amaçlı sağlanmıştır
- Gerçek sermayeyi riske atmadan önce stratejileri her zaman kapsamlı test edin
- Kalifiye finansal profesyonellerden tavsiye almayı düşünün
- Yazarlar herhangi bir finansal kayıptan sorumlu değildir

**Yazılım Lisansı**: Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.

## 📞 Destek

- **GitHub Issues**: Hata raporları ve özellik istekleri için
- **Discord**: Tartışma için Nautilus Trader topluluğuna katılın
- **E-posta**: Ticari destek için geliştirme ekibi ile iletişime geçin

---

<div align="center">

**[Nautilus Trader](https://nautilustrader.io) kullanarak ❤️ ile inşa edildi**

*İyi Ticaret! 📈*

</div>
