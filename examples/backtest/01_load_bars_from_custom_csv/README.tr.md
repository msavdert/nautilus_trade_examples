# CSV Veri Yükleme Backtest Örneği

Bu proje, NautilusTrader framework'ü kullanarak CSV finansal verilerini otomatik indirme, format dönüştürme ve backtest yapma işlemini göstermektedir.

## 🎯 Amaç

Bu örnek size şunları gösterir:

- **Otomatik Veri İndirme**: Yahoo Finance'den otomatik finansal veri indirme
- **CSV Veri Entegrasyonu**: Kendi fiyat verilerinizi NautilusTrader'a yükleme
- **Veri Format Dönüşümü**: İndirilen verilerin NautilusTrader formatına dönüştürülmesi
- **Backtest Temelleri**: Basit bir backtest motoru kurulumu
- **Strateji Geliştirme**: Moving average crossover ticaret stratejisi oluşturma

## 📁 Dosya Yapısı

```
01_load_bars_from_custom_csv/
├── README.md                    # İngilizce versiyonu
├── README.tr.md                 # Bu dosya (Türkçe)
├── pyproject.toml              # Python proje konfigürasyonu
├── main.py                     # Ana program (veri indirme + backtest)
├── strategy.py                 # Moving Average crossover stratejisi
├── download_data.py            # Bağımsız veri indirme araçları
└── data/                       # CSV dosyaları için dizin (otomatik oluşturulur)
    └── EURUSD_1min.csv        # İndirilen EUR/USD 1-dakika verisi
```

## 🚀 Hızlı Başlangıç (Tam Otomatik)

Bu örnek tamamen otomatik çalışacak şekilde tasarlanmıştır. Sadece şu komutu çalıştırın:

```bash
python main.py
```

Program otomatik olarak:
1. **Veri indirme**: Yahoo Finance'den son 7 günlük EUR/USD verilerini indirir
2. **Format dönüşümü**: Verileri NautilusTrader formatına dönüştürür
3. **Backtest çalıştırma**: Moving Average crossover stratejisini test eder
4. **Sonuçları gösterme**: Performans istatistiklerini yazdırır

## 📥 Otomatik Veri İndirme Sistemi

### main.py İçindeki Veri İndirme Fonksiyonu

`main.py` dosyasında bulunan `download_sample_data()` fonksiyonu şu işlemleri yapar:

```python
def download_sample_data():
    """Yahoo Finance üzerinden örnek EUR/USD verilerini indir."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)  # data klasörü oluştur
    
    csv_file = data_dir / "EURUSD_1min.csv"
    
    # Mevcut dosya varsa onu kullan
    if csv_file.exists():
        print(f"✅ Mevcut veri dosyası kullanılıyor: {csv_file}")
        return str(csv_file)
    
    print("📥 Yahoo Finance'den EUR/USD verileri indiriliyor...")
    
    import yfinance as yf
    
    # EUR/USD verilerini indir (son 7 gün, 1-dakika aralıkları)
    ticker = "EURUSD=X"
    data = yf.download(ticker, period="7d", interval="1m", progress=False)
    
    # NautilusTrader formatına dönüştür
    data.reset_index(inplace=True)
    data["timestamp_utc"] = data["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Gerekli sütunları seç ve yeniden adlandır
    result_data = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
    result_data.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
    
    # NaN değerleri temizle
    result_data = result_data.dropna()
    
    # CSV olarak kaydet (semicolon delimiter ile)
    result_data.to_csv(csv_file, sep=";", index=False)
    
    print(f"✅ {len(result_data)} bar indirildi: {csv_file}")
    return str(csv_file)
```

### Veri İndirme Süreci Detayları

1. **Dizin Kontrolü**: `data/` dizini yoksa oluşturur
2. **Dosya Kontrolü**: `EURUSD_1min.csv` varsa tekrar indirmez
3. **Yahoo Finance Bağlantısı**: `yfinance` kütüphanesi ile bağlanır
4. **Veri İndirme**: Son 7 günlük 1-dakika EUR/USD verilerini alır
5. **Format Dönüşümü**: NautilusTrader uyumlu formata çevirir
6. **Kaydetme**: Semicolon (`;`) ayırıcısı ile CSV'ye kaydeder

## 🛠️ download_data.py ile Gelişmiş Veri İndirme

`download_data.py` scripti farklı veri kaynakları ve formatlar için ek araçlar sağlar. Bu bağımsız script, `main.py`'deki temel indirme fonksiyonuna kıyasla daha fazla esneklik ve gelişmiş özellikler sunar.

### Kullanılabilir Komutlar

```bash
# Yahoo Finance'den özel parametrelerle indirme
python download_data.py yahoo EURUSD=X 7d 1m

# Alpha Vantage'den indirme (ücretsiz API anahtarı gerekli)
python download_data.py alphavantage EUR USD api_anahtariniz

# HistData.com formatını NautilusTrader formatına dönüştürme
python download_data.py convert histdata_raw.csv data/EURUSD_1min.csv

# NautilusTrader uyumluluğu için CSV format doğrulama
python download_data.py validate data/EURUSD_1min.csv
```

### download_data.py Script Özellikleri

Script şu yardımcı fonksiyonları içerir:

1. **`download_yahoo_data()`**: Hata yönetimi ile gelişmiş Yahoo Finance indirme
2. **`download_alpha_vantage_data()`**: Alpha Vantage API desteği
3. **`convert_histdata_format()`**: HistData.com tick verisini OHLC barlarına dönüştürme
4. **`validate_csv_format()`**: CSV dosyalarını NautilusTrader uyumluluğu için doğrulama

### Yahoo Finance İndirme Fonksiyonu

```python
def download_yahoo_data(symbol: str = "EURUSD=X", period: str = "7d", interval: str = "1m"):
    """
    Kapsamlı hata yönetimi ile Yahoo Finance'den veri indirme.
    
    Kullanılabilir semboller: EURUSD=X, GBPUSD=X, USDJPY=X, BTCUSD=X, AAPL, ^GSPC
    Kullanılabilir periyotlar: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    Kullanılabilir aralıklar: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo
    """
    import yfinance as yf
    
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    
    # Farklı tarih sütunu isimlerini işle
    datetime_col = "Datetime" if "Datetime" in data.columns else "Date"
    data.reset_index(inplace=True)
    data["timestamp_utc"] = data[datetime_col].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # Sütunları seç ve NautilusTrader formatına dönüştür
    result = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
    result.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
    
    return result.dropna()
```

### HistData.com Format Dönüşümü

Script, HistData.com tick verisini (`YYYYMMDD HHMMSSMMM,bid,ask` formatı) OHLC barlarına dönüştürebilir:

```python
def convert_histdata_format(input_file: str, output_file: str):
    """HistData.com tick formatını NautilusTrader OHLC formatına dönüştür."""
    
    # Tick verisini oku: YYYYMMDD HHMMSSMMM,bid_price,ask_price
    df = pd.read_csv(input_file, header=None, names=['timestamp', 'bid', 'ask'])
    
    # Zaman damgası formatını dönüştür ve orta fiyat hesapla
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d %H%M%S%f')
    df['mid'] = (df['bid'] + df['ask']) / 2
    
    # Tick verisini 1-dakika OHLC barlarına örnekle
    df.set_index('timestamp', inplace=True)
    ohlc = df['mid'].resample('1min').ohlc()
    ohlc['volume'] = 100  # Forex verisi için dummy volume ekle
    
    # NautilusTrader için formatla
    ohlc.reset_index(inplace=True)
    ohlc['timestamp_utc'] = ohlc['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # NautilusTrader formatında kaydet
    result = ohlc[['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']]
    result.to_csv(output_file, sep=';', index=False)
```

## 📋 NautilusTrader CSV Format Gereksinimleri

NautilusTrader, geçmiş veriler için belirli bir CSV formatı gerektirir:

```csv
timestamp_utc;open;high;low;close;volume
2024-12-01 23:01:00;1.1076;1.10785;1.1076;1.1078;205
2024-12-01 23:02:00;1.10775;1.1078;1.1077;1.10775;86
2024-12-01 23:03:00;1.10775;1.1079;1.1077;1.10785;142
```

### Format Gereksinimleri

- **Sütun Adları**: Tam olarak `timestamp_utc`, `open`, `high`, `low`, `close`, `volume`
- **Ayırıcı**: Alan ayırıcısı olarak semicolon (`;`) kullanın
- **Ondalık Ayırıcı**: Ondalık sayılar için nokta (`.`) kullanın
- **Zaman Damgası Formatı**: UTC zaman diliminde `YYYY-MM-DD HH:MM:SS`
- **Veri Sıralaması**: Zaman damgasına göre sıralı (artan) olmalı
- **Başlıklar**: İlk satır sütun adlarını içermeli

### Veri Doğrulama

`download_data.py` scripti bir doğrulama fonksiyonu içerir:

```python
def validate_csv_format(csv_file: str):
    """CSV dosyasını NautilusTrader uyumluluğu için doğrula."""
    
    df = pd.read_csv(csv_file, sep=';')
    
    # Gerekli sütunları kontrol et
    required_columns = ['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ Eksik sütunlar: {missing_columns}")
        return False
    
    # Zaman damgası formatını doğrula
    try:
        pd.to_datetime(df['timestamp_utc'])
    except:
        print("❌ Geçersiz zaman damgası formatı")
        return False
    
    # Sayısal sütunları kontrol et
    for col in ['open', 'high', 'low', 'close', 'volume']:
        if not pd.api.types.is_numeric_dtype(df[col]):
            print(f"❌ '{col}' sütunu sayısal değil")
            return False
    
    print("✅ CSV formatı NautilusTrader için geçerli")
    return True
```

## 🔄 Veri Format Dönüşüm Süreci

### Yahoo Finance'den NautilusTrader'a

Dönüşüm süreci Yahoo Finance veri yapısını dönüştürür:

```python
# Yahoo Finance ham formatı (indirme sonrası pandas DataFrame):
#    Datetime                   Open     High     Low      Close    Volume
# 0  2024-12-01 23:01:00+00:00  1.1076  1.10785  1.1076   1.1078   205
# 1  2024-12-01 23:02:00+00:00  1.10775 1.1078   1.1077   1.10775  86

# Adım 1: İndeksi sıfırla ve zaman damgasını formatla
data.reset_index(inplace=True)
data["timestamp_utc"] = data["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Adım 2: Sütunları seç ve yeniden adlandır
result = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
result.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]

# Adım 3: Veriyi temizle ve kaydet
result = result.dropna()  # NaN değerleri kaldır
result.to_csv("data/EURUSD_1min.csv", sep=";", index=False)

# Final NautilusTrader formatı:
# timestamp_utc;open;high;low;close;volume
# 2024-12-01 23:01:00;1.1076;1.10785;1.1076;1.1078;205
# 2024-12-01 23:02:00;1.10775;1.1078;1.1077;1.10775;86
```

### NautilusTrader'da Veri Yükleme

Dönüştürülen CSV verisi BarDataWrangler kullanılarak NautilusTrader'a yüklenir:

```python
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.model.data import BarType

# CSV dosyasını oku
df = pd.read_csv("data/EURUSD_1min.csv", sep=";")

# Zaman damgasını datetime'a dönüştür ve indeks olarak ayarla
df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"])
df = df.set_index("timestamp_utc")

# EUR/USD 1-dakika barları için bar tipi oluştur
bar_type = BarType.from_str(f"{instrument.id}-1-MINUTE-MID-EXTERNAL")

# Wrangler oluştur ve veriyi işle
wrangler = BarDataWrangler(bar_type, instrument)
bars: list[Bar] = wrangler.process(df)

# Barları backtest motoruna ekle
engine.add_data(bars)
```

## 🎮 Ticaret Stratejisini Anlama

Örnek strateji (`strategy.py`) basit bir Moving Average crossover sistemi uygular:

### Strateji Bileşenleri

```python
class SimpleStrategy(Strategy):
    def __init__(self, bar_type, trade_size, fast_ma_period=10, slow_ma_period=20):
        super().__init__()
        
        # Strateji parametreleri
        self.bar_type = bar_type
        self.instrument_id = bar_type.instrument_id
        self.trade_size = trade_size
        
        # Teknik göstergeler
        self.fast_ma = SimpleMovingAverage(fast_ma_period)  # 10-periyot MA
        self.slow_ma = SimpleMovingAverage(slow_ma_period)  # 20-periyot MA
        
        # Strateji durumu takibi
        self.last_signal = None
        self.trades_count = 0
```

### Ticaret Mantığı

Strateji şu kuralları uygular:

```python
def on_bar(self, bar: Bar):
    """Her yeni fiyat barı için çağrılır."""
    
    # Hareketli ortalamaları yeni fiyat verisi ile güncelle
    self.fast_ma.update_raw(bar.close)
    self.slow_ma.update_raw(bar.close)
    
    # Göstergelerin başlatılmasını bekle (en az 20 bar gerekli)
    if not (self.fast_ma.initialized and self.slow_ma.initialized):
        return
    
    # Mevcut piyasa sinyalini belirle
    fast_value = self.fast_ma.value
    slow_value = self.slow_ma.value
    
    if fast_value > slow_value:
        current_signal = "BUY"    # Hızlı MA yavaş MA'nın üstünde = yükseliş
    elif fast_value < slow_value:
        current_signal = "SELL"   # Hızlı MA yavaş MA'nın altında = düşüş
    else:
        current_signal = None     # Net sinyal yok
    
    # Sadece sinyal değişikliklerinde işlem yap
    if current_signal != self.last_signal and current_signal is not None:
        self._execute_signal(current_signal, bar)
        self.last_signal = current_signal
```

### Pozisyon Yönetimi

```python
def _execute_signal(self, signal: str, bar: Bar):
    """Pozisyon yönetimi ile ticaret sinyali uygula."""
    
    # Mevcut pozisyonu kontrol et
    positions = self.cache.positions_open(instrument_id=self.instrument_id)
    position = positions[0] if positions else None
    
    if signal == "BUY":
        if position is None or position.is_closed:
            # Yeni long pozisyon aç
            self._place_market_order(OrderSide.BUY, bar.close)
        elif position.is_short:
            # Short'u kapat ve long aç
            self._close_position(position)
            self._place_market_order(OrderSide.BUY, bar.close)
    
    elif signal == "SELL":
        if position is None or position.is_closed:
            # Yeni short pozisyon aç
            self._place_market_order(OrderSide.SELL, bar.close)
        elif position.is_long:
            # Long'u kapat ve short aç
            self._close_position(position)
            self._place_market_order(OrderSide.SELL, bar.close)
```

## 🔧 Kurulum ve Ayarlar

### Ön Gereksinimler

```bash
# Gerekli paketleri yükle
pip install nautilus_trader pandas yfinance requests

# Alternatif: uv kullanarak (daha hızlı paket yöneticisi)
uv add nautilus_trader pandas yfinance requests
```

### Örneği Çalıştırma

```bash
# Örnek dizinine git
cd examples/backtest/01_load_bars_from_custom_csv/

# Seçenek 1: Tam otomatik örneği çalıştır
python main.py

# Seçenek 2: Özel veri indirme için download_data.py kullan
python download_data.py yahoo EURUSD=X 1mo 5m  # 1 aylık 5-dakika verisi indir
python main.py                                  # Sonra backtest çalıştır

# Seçenek 3: HistData indir ve dönüştür
python download_data.py convert histdata_file.csv data/converted.csv
python main.py
```

## 📊 Alternatif Veri Kaynakları

### 1. Yahoo Finance (Ücretsiz, Varsayılan)

**Desteklenen Enstrümanlar:**
```python
# Forex çiftleri
"EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"

# Kripto paralar  
"BTC-USD", "ETH-USD", "LTC-USD"

# Hisse senedi endeksleri
"^GSPC"    # S&P 500
"^IXIC"    # NASDAQ
"^DJI"     # Dow Jones

# Bireysel hisse senetleri
"AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"
```

**Zaman Periyotları ve Aralıkları:**
```python
# Kullanılabilir periyotlar
periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]

# Kullanılabilir aralıklar  
intervals = ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo"]
```

### 2. Alpha Vantage (API Anahtarı ile Ücretsiz)

```bash
# Ücretsiz API anahtarını al: https://www.alphavantage.co/support/#api-key
# Günde 500 istek, dakikada 5 istek limiti

python download_data.py alphavantage EUR USD api_anahtariniz_buraya
```

### 3. HistData.com (Ücretsiz Manuel İndirme)

1. Ziyaret et: https://www.histdata.com/download-free-forex-historical-data/
2. Döviz çifti ve zaman periyodu seç
3. ZIP dosyasını indir ve CSV'yi çıkart
4. Formatı dönüştür: `python download_data.py convert indirilen_dosya.csv data/output.csv`

## 📈 Backtest Sonuçları Analizi

Backtest kapsamlı performans istatistikleri sağlar:

```
🚀 CSV Veri Yükleme Backtest Örneği Başlatılıyor
==================================================
📥 Yahoo Finance'den EUR/USD verileri indiriliyor...
✅ 2016 bar indirildi: data/EURUSD_1min.csv
📊 Veri aralığı: 2024-12-01 23:01:00 to 2024-12-07 22:59:00

🔧 Backtest motoru kuruluyor...
🔄 Veriler NautilusTrader formatına dönüştürülüyor...
✅ 2016 bar dönüştürüldü
📈 Ticaret stratejisi kuruluyor...

🏃 Backtest çalıştırılıyor...
==================================================

📊 Backtest Sonuçları
==================================================
💰 Başlangıç Bakiyesi: $100,000.00
💰 Bitiş Bakiyesi: $101,250.00
📈 Toplam Getiri: $1,250.00
📊 Getiri %: 1.25%
🔄 Toplam Emirler: 24
✅ Gerçekleşen Emirler: 24
📅 İlk İşlem: 2024-12-01 08:15:00+00:00
📅 Son İşlem: 2024-12-07 22:45:00+00:00

✅ Backtest başarıyla tamamlandı!
```

### Performans Metrikleri Açıklaması

- **Başlangıç/Bitiş Bakiyesi**: Backtest periyodu öncesi ve sonrası hesap bakiyesi
- **Toplam Getiri**: Temel para biriminde (USD) mutlak kar/zarar
- **Getiri %**: İlk sermaye üzerinden yüzdelik getiri
- **Toplam Emirler**: Strateji tarafından verilen tüm emirler
- **Gerçekleşen Emirler**: Başarıyla gerçekleştirilen emirler (piyasa emirleri için toplam ile eşleşmeli)
- **İşlem Zamanlaması**: İlk ve son işlem gerçekleştirme zaman damgaları

## 🔍 Sorun Giderme

### Yaygın Sorunlar ve Çözümler

**1. Kurulum Sorunları**
```bash
# pip başarısız olursa, önce pip'i güncelle
python -m pip install --upgrade pip
pip install nautilus_trader pandas yfinance requests

# M1/M2 Mac'ler için gerekebilir:
pip install --no-binary=nautilus_trader nautilus_trader
```

**2. Veri İndirme Sorunları**
```bash
# İnternet bağlantısını ve Yahoo Finance erişimini test et
python -c "import yfinance as yf; print(yf.download('EURUSD=X', period='1d'))"

# Veri dönmezse, farklı sembol veya zaman periyodu dene
python download_data.py yahoo GBPUSD=X 5d 5m
```

**3. CSV Format Sorunları**
```bash
# CSV dosyanızı doğrula
python download_data.py validate data/dosyaniz.csv

# Dosya içeriğini manuel kontrol et
head -5 data/EURUSD_1min.csv
```

**4. Strateji Sorunları**
```python
# main.py'de debug loglarını etkinleştir
engine_config = BacktestEngineConfig(
    trader_id=TraderId("BACKTEST-001"),
    logging=LoggingConfig(log_level="DEBUG"),  # INFO'dan değiştirildi
)
```

**5. AttributeError Sorunları (Düzeltildi)**
- `order.is_filled` ile ilgili orijinal sorun çözüldü
- Mevcut kod doğru şekilde emir durumu kontrolü için `order.status` kullanıyor

### Debug Modu

Detaylı yürütme bilgisi için:

```python
# main.py'de loglama seviyesini değiştir
logging=LoggingConfig(log_level="DEBUG")

# Bu şunları gösterecek:
# - Bireysel bar işleme
# - Gösterge hesaplamaları  
# - Emir verme ve gerçekleştirme
# - Pozisyon değişiklikleri
```

## 📚 Sonraki Adımlar ve Geliştirmeler

### 1. Parametre Optimizasyonu

```python
# Farklı hareketli ortalama periyotları dene
fast_periods = [5, 8, 10, 12, 15]
slow_periods = [20, 25, 30, 35, 40]

# Farklı zaman dilimlerini test et
timeframes = ["1m", "5m", "15m", "30m", "1h"]

# Farklı enstrümanları test et
instruments = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "BTCUSD=X"]
```

### 2. Strateji Geliştirmeleri

```python
# Daha fazla gösterge ekle
from nautilus_trader.indicators.rsi import RelativeStrengthIndex
from nautilus_trader.indicators.macd import MACD

# Risk yönetimi uygula
stop_loss_percent = 0.02    # %2 stop loss
take_profit_percent = 0.04  # %4 take profit

# Pozisyon boyutlandırma ekle
risk_per_trade = 0.01  # İşlem başına hesabın %1'ini riske at
```

### 3. Gelişmiş Veri Kaynakları

- **Profesyonel Veri**: Databento, Polygon.io, IEX Cloud
- **Yüksek Frekans**: Daha hassas girişler için tick verisi
- **Çoklu Varlık**: Korelasyon analizi ile portföy backtesti
- **Alternatif Veri**: Haber duyarlılığı, ekonomik göstergeler

### 4. Prodüksiyon Hususları

- **Kağıt Ticaret**: Canlı veri ile ama simüle edilmiş işlemlerle strateji testi
- **Risk Yönetimi**: Maksimum düşüş limitleri, pozisyon boyutu limitleri
- **Portföy Yönetimi**: Çoklu varlık stratejileri, korelasyon analizi
- **Performans Analitikleri**: Sharpe oranı, maksimum düşüş, kazanma oranı

## 📖 Ek Kaynaklar

- **NautilusTrader Dokümantasyonu**: https://nautilustrader.io/
- **API Referansı**: https://nautilustrader.io/docs/api_reference/
- **Strateji Örnekleri**: https://github.com/nautechsystems/nautilus_trader/tree/develop/examples
- **Teknik Göstergeler**: https://nautilustrader.io/docs/api_reference/indicators/
- **Topluluk Discord**: https://discord.gg/nautilustrader
