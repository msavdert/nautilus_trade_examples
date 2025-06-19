# One-Three-Melih: Gelişmiş Adım-Geri Risk Yönetimi Ticaret Botu

## Genel Bakış

**One-Three-Melih** ticaret botu, Nautilus Trader çerçevesi kullanarak gelişmiş adım-geri bakiye yönetimi stratejisi uygulayan sofistike bir EUR/USD forex ticaret sistemidir. Bu bot, karların sonraki işlemler için ticaret bakiyesini artırdığı, kayıpların ise önceki bakiye seviyelerine akıllı adım-geri dönüşleri tetiklediği disiplinli bir yaklaşım izler.

## 🚀 Ana Özellikler

### Gelişmiş Bakiye Yönetimi
- **Tam Bakiye Kullanımı**: Her işlem mevcut bakiyenin tamamını kullanır (kısmi pozisyon yok)
- **Kar Adımları**: %30 kar hedefi, sonraki işlem için bakiyeyi artırır
- **Dinamik Adım-Geri**: Kayıplar bakiyeyi önceki adım seviyesine döndürür
- **Martingale Yok**: Adım başına sabit risk, pozisyon ölçeklendirmesi yok

### Risk Yönetimi
- **Tek Pozisyon Ticareti**: Aynı anda sadece bir pozisyon açık
- **Dinamik Stop Loss**: Önceki bakiyeye kesin adım-geri dönüş sağlayacak şekilde hesaplanır
- **Ardışık Kayıp Koruması**: Maksimum ardışık kayıptan sonra otomatik duraklama
- **Şeffaf Kayıt**: Kapsamlı işlem ve bakiye takibi

### Nautilus Entegrasyonu
- **Tam Çerçeve Kullanımı**: Gelişmiş Nautilus Trader yeteneklerinden yararlanır
- **Çoklu Yürütme Modları**: Backtest, demo ve canlı ticaret desteği
- **Gerçek Zamanlı Piyasa Verisi**: Quote tick işleme ve emir yönetimi
- **Profesyonel Risk Kontrolleri**: Yerleşik pozisyon ve emir yönetimi

## 📊 Strateji Mantığı

### Bakiye İlerleme Örneği

```
İşlem 1: $100 ile başla → Kazan (%30) → Sonraki işlem $130 ile
İşlem 2: $130 → Kazan (%30) → Sonraki işlem $169 ile
İşlem 3: $169 → Kaybet (%23.08 kayıp) → Sonraki işlem $130 ile (adım geri)
İşlem 4: $130 → Kaybet (%23.08 kayıp) → Sonraki işlem $100 ile (adım geri)
```

### Dinamik Kayıp Hesaplaması

Bot, önceki bakiye seviyesine dönmek için gereken kesin kayıp yüzdesini hesaplar:

- **$169'da**: %23.08 kayıp $130'a döndürür
- **$130'da**: %23.08 kayıp $100'e döndürür
- **$100'de**: Sabit %30 kayıp $100'de kalır

## 🛠 Kurulum

### Ön Gereksinimler

- Python 3.11 veya üzeri
- pip paket yöneticisi

### Kurulum Adımları

1. **Projeyi klonlayın veya indirin**:
   ```bash
   cd bots/one_three_melih
   ```

2. **Bağımlılıkları yükleyin**:
   ```bash
   pip install -e .
   ```

3. **Geliştirme bağımlılıklarını yükleyin** (isteğe bağlı):
   ```bash
   pip install -e ".[dev]"
   ```

4. **Backtest bağımlılıklarını yükleyin** (gelişmiş analiz için):
   ```bash
   pip install -e ".[backtest]"
   ```

## 🚀 Kullanım

### Demo Modu (Test için Önerilen)

Botu simüle edilmiş piyasa verisiyle çalıştırın:

```bash
python main.py --mode demo --initial-balance 100
```

### Backtest Modu

Stratejiyi geçmiş verilerle test edin:

```bash
python main.py --mode backtest --start-date 2024-01-01 --end-date 2024-06-01 --initial-balance 100
```

### Özel Parametrelerle Gelişmiş Backtest

```bash
python main.py --mode backtest \
    --start-date 2024-01-01 \
    --end-date 2024-12-31 \
    --initial-balance 1000
```

### Komut Satırı Seçenekleri

| Seçenek | Açıklama | Varsayılan |
|---------|----------|------------|
| `--mode` | Yürütme modu: demo, backtest, live | demo |
| `--initial-balance` | Başlangıç bakiyesi (USD) | 100 |
| `--start-date` | Backtest başlangıç tarihi (YYYY-MM-DD) | 2024-01-01 |
| `--end-date` | Backtest bitiş tarihi (YYYY-MM-DD) | 2024-06-01 |
| `--config` | Konfigürasyon dosya yolu | None |

## 📝 Konfigürasyon

### Strateji Konfigürasyonu

Bot, `OneThreeMelihConfig` sınıfı aracılığıyla konfigüre edilebilir:

```python
config = OneThreeMelihConfig(
    instrument_id=InstrumentId.from_str("EUR/USD.SIM"),
    initial_balance=Decimal("100.00"),
    profit_target_percentage=Decimal("30.0"),
    trade_delay_seconds=5,
    max_consecutive_losses=10,
    log_level="INFO",
    enable_detailed_logging=True,
)
```

### Ana Parametreler

- **initial_balance**: Başlangıç ticaret bakiyesi
- **profit_target_percentage**: Kar hedefi (varsayılan: %30)
- **max_consecutive_losses**: Duraklama öncesi maksimum ardışık kayıp
- **trade_delay_seconds**: İşlemler arası gecikme
- **enable_detailed_logging**: Kapsamlı kayıt tutmayı etkinleştir

## 📈 İzleme ve Kayıt Tutma

### Gerçek Zamanlı İstatistikler

Bot, yürütme sırasında gerçek zamanlı istatistikler sağlar:

```
=== BAKİYE İSTATİSTİKLERİ ===
Mevcut Bakiye: $169.00
Mevcut Adım: 3
Toplam Getiri: %69.00
Toplam İşlem: 5
Kazanma Oranı: %60.0
Bakiye Geçmişi: [100.0, 130.0, 169.0]
```

### Log Dosyaları

- **one_three_melih.log**: Zaman damgalı tam ticaret kayıtları
- **Konsol Çıktısı**: Gerçek zamanlı işlem yürütme ve bakiye güncellemeleri

### İşlem Kayıtları

Her işlem kapsamlı detaylarla kaydedilir:

```
=== UZUN POZİSYON GİRİŞİ ===
Giriş Fiyatı: 1.10450
Pozisyon Boyutu: 153
Mevcut Bakiye: $169.00
Kar Al: 1.11234 (+$50.70)
Zarar Durdur: 1.09666 (-$39.00)
Zarar Durdur %: %23.08
```

## 🧪 Test Etme

### Birim Testlerini Çalıştırma

```bash
pytest test_strategy.py -v
```

### Test Kapsamı

Test paketi şunları kapsar:
- BalanceTracker mantığı ve hesaplamaları
- Adım-geri bakiye yönetimi
- Dinamik stop loss hesaplamaları
- Tam ticaret senaryoları
- Entegrasyon testi

### Örnek Test Senaryoları

```python
# Tam ticaret ilerlemesini test et
def test_complete_trading_scenario():
    tracker = BalanceTracker(Decimal("100.00"), Decimal("30.0"))
    
    # Kazan, Kazan, Kaybet, Kazan, Kaybet, Kaybet
    tracker.record_profit()  # $100 -> $130
    tracker.record_profit()  # $130 -> $169
    tracker.record_loss()    # $169 -> $130 (adım geri)
    # ... vs
```

## ⚡ Performans Özellikleri

### Hesaplama Verimliliği
- **Hafif**: Minimal bellek kullanımı
- **Hızlı Yürütme**: Gerçek zamanlı ticaret için optimize edilmiş
- **Ölçeklenebilir**: Yüksek frekanslı quote güncellemelerini işler

### Risk Profili
- **Kontrollü Risk**: Adım başına maksimum kayıp önceden belirlenir
- **Kaldıraç Yok**: Saf bakiye tabanlı pozisyon boyutlandırma
- **Aşamalı Büyüme**: Sürdürülebilir kar biriktirme

## 🔧 Gelişmiş Özellikler

### Nautilus Çerçeve Entegrasyonu

Bot, gelişmiş Nautilus yeteneklerinden yararlanır:

- **Emir Yönetimi**: Market, limit ve stop emirleri
- **Pozisyon Takibi**: Gerçek zamanlı pozisyon izleme
- **Risk Kontrolleri**: Yerleşik risk yönetim sistemleri
- **Veri İşleme**: Yüksek performanslı tick veri işleme
- **Olay Odaklı Mimari**: Asenkron yürütme

### Genişletilebilirlik

Modüler tasarım kolay özelleştirmeye olanak tanır:

```python
# Özel bakiye ilerlemesi
class CustomBalanceTracker(BalanceTracker):
    def get_profit_target(self) -> Decimal:
        # Özel kar hesaplaması
        return self.current_balance * Decimal("0.25")  # %25 hedef
```

## 📊 Beklenen Performans

### Teorik Analiz

%50 kazanma oranı ve işlem başına %30 kar/kayıp ile:

- **Başabaş**: ~%50 kazanma oranı
- **Pozitif Beklenti**: Kazanma oranı > %50
- **Riske Göre Ayarlanmış Getiri**: Sınırlı aşağı yön, sınırsız yukarı adımlar

### Backtest Sonuçları

Sonuçlar piyasa koşulları ve kazanma oranına göre değişir:

```
Başlangıç Bakiyesi: $100.00
Final Bakiye: $169.00
Toplam Getiri: %69.00
Toplam İşlem: 10
Kazanma Oranı: %60.0
Ulaşılan Maksimum Adım: 3
```

## ⚠️ Önemli Hususlar

### Risk Uyarıları

1. **Geçmiş Performans**: Gelecekteki sonuçları garanti etmez
2. **Piyasa Riski**: Tüm ticaret kayıp riski içerir
3. **Test Gerekli**: Canlı ticaretten önce kapsamlı test yapın
4. **Sermaye Gereksinimleri**: Sadece kaybetmeyi göze alabileceğiniz sermaye ile ticaret yapın

### En İyi Uygulamalar

1. **Küçük Başlayın**: Test için küçük bakiyelerle başlayın
2. **Performansı İzleyin**: Ticaret istatistiklerini düzenli olarak gözden geçirin
3. **Risk Yönetimi**: Uygun maksimum kayıp limitleri belirleyin
4. **Piyasa Koşulları**: Piyasa volatilitesi ve koşullarını dikkate alın

## 🔄 Güncellemeler ve Bakım

### Sürüm Geçmişi

- **v1.0.0**: Adım-geri bakiye yönetimi ile ilk sürüm
- **Gelecek**: Canlı ticaret entegrasyonu, ek enstrümanlar

### Katkıda Bulunma

Projeye katkıda bulunmak için:

1. Repository'yi fork edin
2. Özellik dalı oluşturun
3. Yeni işlevsellik için testler ekleyin
4. Pull request gönderin

## 📞 Destek

Sorular, sorunlar veya öneriler için:

- Kod belgelerini inceleyin
- Kullanım örnekleri için test paketini kontrol edin
- Hata ayıklama bilgileri için log dosyalarını inceleyin

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için LICENSE dosyasına bakın.

---

**Sorumluluk Reddi**: Bu ticaret botu eğitim ve araştırma amaçlıdır. Gerçek para ile kullanmadan önce her zaman kapsamlı test yapın. Ticaret önemli kayıp riski içerir.
