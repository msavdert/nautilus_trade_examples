# İlk Botum - Nautilus Trader Yeni Başlayan Rehberi

Nautilus Trader ile algoritmik trading'e ilk adımınıza hoş geldiniz! Bu rehber sizi adım adım ilk trading botunuzu oluşturmaya yönlendirecek ve her şeyi sıfırdan açıklayacaktır.

## 🎯 Ne Yapacağız

Basit bir trading botu oluşturacağız:
- EUR/USD için piyasa verilerini izleyecek
- Basit hareketli ortalama stratejisi kullanacak
- Basit kurallara göre alım/satım emirleri verecek
- Tek bir `main.py` dosyasında çalışacak

## 📚 Ön Koşullar

Başlamadan önce aşağıdakilerin hazır olduğundan emin olun:
- [Hızlı Başlangıç kurulumunu](../../README.tr.md#hızlı-başlangıç) tamamladınız
- Bot projeniz oluşturuldu: `my-first-bot`
- Temel Python bilgisi

## 🧭 Nautilus Trader Temellerini Anlama

### Trading Stratejisi Nedir?

Nautilus Trader'da bir **Strategy** (Strateji), şunları yapan bir Python sınıfıdır:
1. **Piyasa verilerini alır** (fiyatlar, hacimler, vb.)
2. **Bu verilere dayanarak trading kararları verir**
3. **Enstrümanları almak veya satmak için emirler verir**

### Ana Bileşenler

- **Strategy**: Trading mantığınız (yapacağımız şey)
- **Instruments**: Neyi trade ediyorsunuz (EUR/USD, BTC/USD, vb.)
- **Market Data**: Fiyat bilgileri (kotasyonlar, işlemler, barlar)
- **Orders**: Alım veya satım talimatları
- **Portfolio**: Pozisyonlarınızı ve paranızı takip eder

## 🏗️ Adım 1: İlk Stratejinizi Oluşturun

Ana bot dosyamızı oluşturarak başlayalım. Bot dizininize gidin ve ana dosyayı oluşturun:

```bash
# Doğru dizinde olduğunuzdan emin olun
cd /workspace/bots/my-first-bot
```

`main.py` dosyasını oluşturun:

```python
# main.py - İlk Trading Botum

from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.objects import Quantity
from nautilus_trader.common.enums import LogColor


class IlkBotumConfig(StrategyConfig, frozen=True):
    """
    İlk trading botumuzun konfigürasyonu.
    Bu, botumuzun hangi ayarlara ihtiyacı olduğunu tanımlar.
    """
    # Trade etmek istediğimiz enstrüman (EUR/USD gibi)
    instrument_id: str = "EUR/USD.SIM"
    
    # Her seferinde ne kadar trade edeceğiz
    trade_size: int = 100_000  # 100.000 birim
    
    # Hareketli ortalama periyodu (kaç bar geriye bakacağız)
    ma_period: int = 10


class IlkBotum(Strategy):
    """
    İlk Trading Botum - Basit Hareketli Ortalama Stratejisi
    
    Bu bot şunları yapacak:
    1. Kapanış fiyatlarının basit hareketli ortalamasını hesaplayacak
    2. Fiyat hareketli ortalamanın üzerindeyken alım yapacak
    3. Fiyat hareketli ortalamanın altındayken satım yapacak
    """
    
    def __init__(self, config: IlkBotumConfig):
        # Her zaman önce parent class constructor'ını çağırın
        super().__init__(config)
        
        # Konfigürasyonumuzu saklayalım
        self.config = config
        
        # Trading değişkenlerimizi başlatalım
        self.fiyatlar = []  # Son kapanış fiyatlarını sakla
        self.pozisyon_acik = False  # Açık pozisyonumuz var mı takip et
        self.alinan_barlar = 0  # Kaç fiyat barı gördüğümüzü say
        
        # Trade boyutunu Nautilus Quantity nesnesine çevir
        self.trade_miktari = Quantity.from_int(config.trade_size)
    
    def on_start(self):
        """
        Bu metot botumuz başladığında çağrılır.
        Burada Nautilus'a hangi veriyi almak istediğimizi söyleriz.
        """
        self.log.info("🚀 İlk Botum başlıyor!", color=LogColor.GREEN)
        
        # Enstrümanımız için 1 dakikalık barlara abone ol
        # Bu, her dakika fiyat güncellemeleri alacağımız anlamına gelir
        from nautilus_trader.model.data import BarType
        bar_type = BarType.from_str(f"{self.config.instrument_id}-1-MINUTE-MID-EXTERNAL")
        self.subscribe_bars(bar_type)
        
        self.log.info(f"📊 {bar_type} için abone olundu")
    
    def on_bar(self, bar: Bar):
        """
        Bu metot her yeni fiyat barı aldığımızda çağrılır.
        Ana trading mantığımız burada yaşar.
        """
        self.alinan_barlar += 1
        
        # Bu barın kapanış fiyatını al
        kapanis_fiyati = float(bar.close)
        
        # Yeni fiyatı listemize ekle
        self.fiyatlar.append(kapanis_fiyati)
        
        # Sadece son 'ma_period' fiyatları tut
        if len(self.fiyatlar) > self.config.ma_period:
            self.fiyatlar.pop(0)  # En eski fiyatı kaldır
        
        self.log.info(
            f"📈 Bar #{self.alinan_barlar}: Fiyat = {kapanis_fiyati:.5f}",
            color=LogColor.BLUE
        )
        
        # Sadece yeterli verimiz olduktan sonra trading'e başla
        if len(self.fiyatlar) < self.config.ma_period:
            self.log.info(f"⏳ Daha fazla veri bekleniyor... ({len(self.fiyatlar)}/{self.config.ma_period})")
            return
        
        # Basit Hareketli Ortalama hesapla
        hareketli_ortalama = sum(self.fiyatlar) / len(self.fiyatlar)
        
        self.log.info(
            f"📊 Mevcut Fiyat: {kapanis_fiyati:.5f}, Hareketli Ortalama: {hareketli_ortalama:.5f}",
            color=LogColor.CYAN
        )
        
        # Trading Mantığı
        self.giris_kontrol_et(kapanis_fiyati, hareketli_ortalama)
    
    def giris_kontrol_et(self, mevcut_fiyat: float, hareketli_ortalama: float):
        """
        Stratejimize göre alım veya satım yapıp yapmayacağımızı kontrol et.
        """
        
        # Strateji Kuralı 1: Fiyat hareketli ortalamanın üzerindeyken al
        if mevcut_fiyat > hareketli_ortalama and not self.pozisyon_acik:
            self.alim_emri_ver()
            
        # Strateji Kuralı 2: Fiyat hareketli ortalamanın altındayken sat
        elif mevcut_fiyat < hareketli_ortalama and self.pozisyon_acik:
            self.satim_emri_ver()
    
    def alim_emri_ver(self):
        """
        Alım emri ver (long pozisyon aç).
        """
        try:
            # Alım için market emri oluştur
            emir = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.trade_miktari,
            )
            
            # Emri gönder
            self.submit_order(emir)
            self.pozisyon_acik = True
            
            self.log.info("🟢 ALIM EMRİ VERİLDİ!", color=LogColor.GREEN)
            
        except Exception as e:
            self.log.error(f"❌ Alım emri verirken hata: {e}")
    
    def satim_emri_ver(self):
        """
        Satım emri ver (pozisyonu kapat).
        """
        try:
            # Satım için market emri oluştur
            emir = self.order_factory.market(
                instrument_id=self.config.instrument_id,
                order_side=OrderSide.SELL,
                quantity=self.trade_miktari,
            )
            
            # Emri gönder
            self.submit_order(emir)
            self.pozisyon_acik = False
            
            self.log.info("🔴 SATIM EMRİ VERİLDİ!", color=LogColor.RED)
            
        except Exception as e:
            self.log.error(f"❌ Satım emri verirken hata: {e}")
    
    def on_stop(self):
        """
        Bu metot botumuz durduğunda çağrılır.
        Burada kaynakları temizle.
        """
        self.log.info("🛑 İlk Botum duruyor...", color=LogColor.YELLOW)
        self.log.info(f"📊 Toplam işlenen bar: {self.alinan_barlar}")


# Botumuzu test et (gerçek trade yapmaz)
if __name__ == "__main__":
    print("🤖 İlk Trading Botum")
    print("Bu sadece strateji tanımı.")
    print("Backtest veya canlı trading çalıştırmak için ek kurulum gerekir.")
    print("Dokümantasyondaki sonraki adımları kontrol edin!")
```

## 📖 Kodu Anlama

Her parçanın ne yaptığını açıklayalım:

### 1. Konfigürasyon Sınıfı (`IlkBotumConfig`)
```python
class IlkBotumConfig(StrategyConfig, frozen=True):
    instrument_id: str = "EUR/USD.SIM"
    trade_size: int = 100_000
    ma_period: int = 10
```

Bu, botumuzun ayarlarını tanımlar:
- **instrument_id**: Neyi trade etmek istiyoruz
- **trade_size**: Ne kadar trade edeceğiz
- **ma_period**: Hareketli ortalama için kaç fiyat barı kullanacağız

### 2. Strateji Sınıfı (`IlkBotum`)
```python
class IlkBotum(Strategy):
```

Bu, Nautilus'un `Strategy` sınıfından türeyen ana botumuz.

### 3. Ana Metodlar

- **`__init__`**: Bot oluşturulduğunda kurulum yapar
- **`on_start`**: Bot başladığında çağrılır - burada veriye abone oluruz
- **`on_bar`**: Her yeni fiyat barı için çağrılır - ana mantığımız
- **`on_stop`**: Bot durduğunda çağrılır - temizlik kodu

### 4. Trading Mantığı Akışı

1. **`on_bar`'da fiyat verisi al**
2. **Fiyatları bir listede sakla**
3. **Yeterli veri olduğunda hareketli ortalama hesapla**
4. **Mevcut fiyatı hareketli ortalama ile karşılaştır**
5. **Kurallarımıza göre emirler ver**

## 🎯 Adım 2: Ana Kavramları Anlama

### Piyasa Verisi Türleri

- **Bar**: Bir zaman periyodundaki fiyat verisi (açılış, yüksek, düşük, kapanış)
- **Quote**: En iyi alış/satış fiyatları
- **Trade**: Gerçek işlemler

### Emir Türleri

- **Market Order**: Mevcut fiyattan hemen al/sat
- **Limit Order**: Sadece belirli fiyattan veya daha iyisinden al/sat

### Strateji Yaşam Döngüsü

1. **Başlatma** (`__init__`)
2. **Başla** (`on_start`) - Veriye abone ol
3. **Veri İşle** (`on_bar`, `on_quote_tick`, vb.)
4. **Karar Ver** (trading mantığınız)
5. **Emir Ver** (`submit_order`)
6. **Dur** (`on_stop`) - Temizlik

## 🚀 Adım 3: Sonraki Adımlar

Artık ilk stratejiniz olduğuna göre, şunları yapmak isteyeceksiniz:

1. **Backtest ile test edin** - Geçmiş verilerde çalıştırın
2. **Daha gelişmiş mantık ekleyin** - Daha iyi giriş/çıkış kuralları
3. **Risk yönetimi ekleyin** - Stop loss, pozisyon büyüklüğü
4. **Testnet'te test edin** - Sahte para ile pratik yapın

### Hızlı Test

Yukarıdaki kodu `main.py`'ye kaydedin ve çalıştırın:

```bash
uv run python main.py
```

Şunu görmelisiniz:
```
🤖 İlk Trading Botum
Bu sadece strateji tanımı.
Backtest veya canlı trading çalıştırmak için ek kurulum gerekir.
Dokümantasyondaki sonraki adımları kontrol edin!
```

## 🎓 Öğrendikleriniz

Tebrikler! İlk trading botunuzu oluşturdunuz. Artık şunları anlıyorsunuz:

- ✅ Nautilus Strategy sınıfı nasıl oluşturulur
- ✅ Botunuzu ayarlarla nasıl konfigüre edersiniz
- ✅ Piyasa verisini nasıl alır ve işlersiniz
- ✅ Temel trading mantığı nasıl uygulanır
- ✅ Alım ve satım emirleri nasıl verilir
- ✅ Tam bir trading botunun yapısı

## 🔄 Nautilus'ta Yaygın Kalıplar

Çoğu trading stratejisi bu kalıbı takip eder:

1. **`on_start`'ta veriye abone ol**
2. **Olay işleyicilerinde veri işle** (`on_bar`, `on_quote_tick`)
3. **İndikatörleri hesapla** (hareketli ortalamalar, RSI, vb.)
4. **Trading koşullarını kontrol et** (strateji kurallarınız)
5. **Pozisyonları yönet** (giriş, çıkış, risk yönetimi)

## 🛡️ Önemli Notlar

- **Bu eğitim amaçlı**: Bu basit strateji sadece öğrenme içindir
- **Gerçek para yok**: Gerçek sermayeyi riske atmadan önce her zaman iyice test edin
- **Risk yönetimi**: Gerçek stratejiler stop loss ve pozisyon büyüklüğü gerektirir
- **Piyasa koşulları**: Hiçbir strateji tüm piyasa koşullarında çalışmaz

## 📚 İleri Okuma

- [Trading Temelleri](../trading-fundamentals.md)
- [Risk Yönetimi](../risk-management.md)
- [Nautilus Strateji Dokümantasyonu](https://nautilustrader.io/docs/latest/concepts/strategies)

---

**Sonraki**: Stratejinizi geçmiş verilerle nasıl backtest edeceğinizi öğrenin!

## 🔗 İlgili Rehberler

- [English Version (İngilizce)](my-first-bot.md)
- [Gelişmiş Strateji Kalıpları](advanced-patterns.tr.md) *(Çok Yakında)*
- [Stratejinizi Backtest Etme](backtesting-guide.tr.md) *(Çok Yakında)*
