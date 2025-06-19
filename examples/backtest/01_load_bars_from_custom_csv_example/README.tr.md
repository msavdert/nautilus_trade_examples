# CSV Verilerinden Bar Yükleme Backtest Örneği

Bu bot, NautilusTrader kullanarak özel CSV dosyalarından fiyat verilerini yükleyip backtest yapmanın nasıl gerçekleştirileceğini gösteren temel bir örnektir.

## 🎯 Amacı

Bu bot özellikle şu amaçlar için tasarlanmıştır:

- **CSV Veri Entegrasyonu**: Kendi fiyat verilerinizi NautilusTrader sistemine nasıl yükleyeceğinizi öğrenmek
- **Backtest Temellerini Öğrenmek**: En basit backtest engine kurulumunu görmek
- **Veri Wrangling**: Pandas kullanarak CSV verilerini NautilusTrader formatına dönüştürmeyi öğrenmek
- **Strateji Geliştirme Temelleri**: Basit bir strateji sınıfının nasıl oluşturulacağını anlamak

## 📁 Dosya Yapısı

```
example_01_load_bars_from_custom_csv/
├── README.md                    # Bu dosya
├── pyproject.toml              # Python proje konfigürasyonu
├── main.py                     # Basit giriş noktası
├── run_example.py              # Ana backtest çalıştırma scripti
├── strategy.py                 # Demo strateji sınıfı
└── 6EH4.XCME_1min_bars.csv    # Örnek EUR/USD futures 1-dakika bar verisi
```

## 🔧 Kullanım

### 1. Projeyi Çalıştırma

```bash
# Projeyi çalıştırmak için:
python run_example.py

# Veya uv kullanarak:
uv run run_example.py
```

### 2. Kendi Verilerinizi Kullanma

CSV dosyanızın şu formatta olması gerekir:

```csv
timestamp_utc;open;high;low;close;volume;pricetype
2024-01-01 23:01:00;1.1076;1.10785;1.1076;1.1078;205;Last
2024-01-01 23:02:00;1.10775;1.1078;1.1077;1.10775;86;Last
```

**Gerekli sütunlar:**
- `timestamp_utc`: UTC zaman damgası (YYYY-MM-DD HH:MM:SS formatında)
- `open`: Açılış fiyatı
- `high`: En yüksek fiyat
- `low`: En düşük fiyat
- `close`: Kapanış fiyatı
- `volume`: İşlem hacmi (opsiyonel)

## 📊 Kod Açıklaması

### Ana Bileşenler

#### 1. BacktestEngine Konfigürasyonu
```python
engine_config = BacktestEngineConfig(
    trader_id=TraderId("BACKTEST_TRADER-001"),
    logging=LoggingConfig(log_level="DEBUG"),
)
```

#### 2. Venue (Borsa) Tanımı
```python
XCME = Venue("XCME")
engine.add_venue(
    venue=XCME,
    oms_type=OmsType.NETTING,
    account_type=AccountType.MARGIN,
    starting_balances=[Money(1_000_000, USD)],
    base_currency=USD,
)
```

#### 3. CSV Veri Yükleme İşlemi
```python
# CSV'yi pandas DataFrame'e yükle
df = pd.read_csv(csv_file_path, sep=";", decimal=".")

# Veriyi NautilusTrader formatına dönüştür
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
df = df.rename(columns={"timestamp_utc": "timestamp"})
df = df.set_index("timestamp")

# BarDataWrangler ile Bar objelerine dönüştür
wrangler = BarDataWrangler(bar_type, instrument)
bars_list = wrangler.process(df)
```

#### 4. Strateji Tanımı (DemoStrategy)
```python
class DemoStrategy(Strategy):
    def on_start(self):
        # Başlangıçta bar'lara abone ol
        self.subscribe_bars(self.primary_bar_type)
    
    def on_bar(self, bar: Bar):
        # Her yeni bar geldiğinde çalışır
        self.bars_processed += 1
```

## 🎓 Öğrenme Noktaları

### 1. Veri Hazırlama
- CSV dosyalarını doğru formatta hazırlamak
- Pandas ile veri manipülasyonu
- Zaman damgası formatlarını dönüştürme

### 2. NautilusTrader Temelleri
- BacktestEngine nasıl kurulur
- Venue (borsa) tanımları
- Enstrüman (finansal araç) konfigürasyonu
- Para yönetimi ve başlangıç bakiyesi

### 3. Strateji Geliştirme
- Strategy sınıfından miras alma
- Bar verilerine abone olma
- Event-driven programlama yaklaşımı
- Loglama ve debugging

## 📈 Örnek Çıktı

Bot çalıştırıldığında şu tarzda loglar göreceksiniz:

```
2024-06-17 10:30:00 [INFO] Strategy started at: 2024-06-17 10:30:00
2024-06-17 10:30:00 [INFO] Processed bars: 1
2024-06-17 10:30:00 [INFO] Processed bars: 2
...
2024-06-17 10:30:05 [INFO] Strategy finished at: 2024-06-17 10:30:05
2024-06-17 10:30:05 [INFO] Total bars processed: 10
```

## 🛠 Geliştirme Önerileri

Bu temel örneği geliştirmek için şunları deneyebilirsiniz:

1. **Gerçek Bir Strateji Yazın**: Moving average crossover, RSI tabanlı sinyaller
2. **Risk Yönetimi Ekleyin**: Stop-loss, take-profit seviyeleri
3. **Çoklu Enstrüman**: Birden fazla döviz çifti veya hisse senedi
4. **Performans Analizi**: Sharpe ratio, maksimum drawdown hesaplamaları
5. **Farklı Veri Kaynakları**: Farklı CSV formatları, API'ler

## 🔗 İlgili Kaynaklar

- [NautilusTrader Dokümantasyonu](https://docs.nautilustrader.io/)
- [Backtest Engine Rehberi](https://docs.nautilustrader.io/guides/backtest.html)
- [Strategy Geliştirme](https://docs.nautilustrader.io/guides/strategy.html)
- [Veri Wrangling](https://docs.nautilustrader.io/guides/data.html)

## ⚠️ Notlar

- Bu örnek sadece eğitim amaçlıdır, gerçek ticaret için doğrudan kullanmayın
- Örnek veri seti çok küçüktür, gerçek backtestler için daha büyük veri setleri kullanın
- Strateji hiçbir ticaret emri vermez, sadece veri işlemeyi gösterir
- Gerçek strateji geliştirirken risk yönetimi mutlaka ekleyin

---

**Bu bot, NautilusTrader'da CSV veri entegrasyonu ve backtest temelleri için mükemmel bir başlangıç noktasıdır! 🚀**
