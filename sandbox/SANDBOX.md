# Nautilus Trader - Sandbox Mode Live Trading Simulation

Bu döküman, Nautilus Trader kullanarak sandbox (test) ortamında live trading simülasyonu nasıl yapılacağını detaylı olarak açıklar.

## İçindekiler

1. [Sandbox Mode Nedir?](#sandbox-mode-nedir)
2. [Gereksinimler](#gereksinimler)
3. [Desteklenen Broker ve Exchange'ler](#desteklenen-broker-ve-exchangeler)
4. [API Anahtarları ve Kimlik Doğrulama](#api-anahtarlari-ve-kimlik-dogrulama)
5. [Ortam Değişkenleri Kurulumu](#ortam-degiskenleri-kurulumu)
6. [Sandbox Trading Bot Yapılandırması](#sandbox-trading-bot-yapilandirmasi)
7. [Live Trading Engine Kurulumu](#live-trading-engine-kurulumu)
8. [Risk Yönetimi ve Güvenlik](#risk-yonetimi-ve-guvenlik)
9. [Monitoring ve Logging](#monitoring-ve-logging)
10. [Troubleshooting](#troubleshooting)
11. [Örnek Kod ve Yapılandırmalar](#ornek-kod-ve-yapilandirmalar)

## Sandbox Mode Nedir?

Sandbox mode, gerçek para kullanmadan live market verilerini kullanarak trading algoritmalarınızı test etmenizi sağlayan bir simülasyon ortamıdır. Bu modda:

- **Gerçek market verileri** kullanılır (real-time price feeds)
- **Sanal para** ile işlem yapılır (paper trading)
- **Gerçek broker API'leri** üzerinden bağlantı kurulur ancak gerçek emirler gönderilmez
- **Latency ve slippage** gerçekçi şekilde simüle edilir
- **Risk management** ve **portfolio management** gerçek koşullarda test edilir

## Gereksinimler

### Sistem Gereksinimleri
- **Python 3.11+**
- **Nautilus Trader 1.198.0+**
- **Docker** (isteğe bağlı, önerilen)
- **Redis** (caching ve session management için)
- **PostgreSQL** (veritabanı, isteğe bağlı)

### Python Paket Gereksinimleri
```bash
pip install nautilus_trader[all]
pip install redis
pip install psycopg2-binary  # PostgreSQL için (isteğe bağlı)
pip install python-dotenv    # Ortam değişkenleri için
```

### Ek Gereksinimler (Broker/Exchange'e göre)
```bash
# Binance için
pip install python-binance

# Interactive Brokers için
pip install ib-insync

# Bybit için
pip install pybit

# Databento için (market data)
pip install databento
```

## Desteklenen Broker ve Exchange'ler

### Test/Sandbox Desteği Olan Platformlar

#### 1. **Binance Spot & Futures Testnet**
- **Spot Testnet:** `https://testnet.binance.vision/`
- **Futures Testnet:** `https://testnet.binancefuture.com/`
- **Ücretsiz test fonları** sağlanır
- **Gerçek market verileri** kullanılır

#### 2. **Bybit Testnet**
- **Testnet URL:** `https://testnet.bybit.com/`
- **Demo hesap** ile başlangıç
- **Spot ve derivatives** trading desteklenir

#### 3. **Interactive Brokers Paper Trading**
- **TWS Demo Account** gerekli
- **Gerçek market verileri** (market data subscription gerekebilir)
- **En gerçekçi simulation** ortamı

#### 4. **FTX Sandbox** (Kapatıldı - sadece referans)
- FTX kapatıldığı için artık kullanılamaz

#### 5. **Deribit Testnet**
- **Options ve Futures** trading
- **Bitcoin/Ethereum** derivatives

## API Anahtarları ve Kimlik Doğrulama

### Binance Testnet API Anahtarı

1. **Binance Testnet'e kayıt olun:**
   - Spot: https://testnet.binance.vision/
   - Futures: https://testnet.binancefuture.com/

2. **API Key oluşturun:**
   ```
   - API Management sayfasına gidin
   - "Create API" butonuna basın
   - API Key ve Secret Key'i not alın
   - IP restriction ayarlayın (güvenlik için)
   ```

3. **Permissions ayarlayın:**
   - Enable Spot & Margin Trading ✓
   - Enable Futures Trading ✓ (futures için)
   - Enable Reading ✓
   - Withdraw fonksiyonunu KAPATIK bırakın ✗

### Bybit Testnet API Anahtarı

1. **Bybit Testnet hesabı oluşturun:**
   - https://testnet.bybit.com/

2. **API Management:**
   ```
   - Account & Security > API Management
   - Create New Key
   - System-generated API keys seçin
   - Permissions: Contract Trading, Spot Trading, Wallet
   ```

### Interactive Brokers Paper Trading

1. **TWS Demo hesabı oluşturun:**
   - https://www.interactivebrokers.com/en/trading/tws-demo.php

2. **TWS Gateway kurulumu:**
   ```
   - TWS Gateway'i indirin ve yükleyin
   - Demo hesap bilgileriyle giriş yapın
   - API Settings: Enable ActiveX and Socket Clients ✓
   - Port: 7497 (Paper Trading), 7496 (Live Trading)
   ```

## Ortam Değişkenleri Kurulumu

Güvenlik için API anahtarlarınızı ortam değişkenleri olarak saklayın.

### `.env` Dosyası Oluşturma

Projenizin ana dizininde `.env` dosyası oluşturun:

```bash
# .env
# BINANCE TESTNET
BINANCE_TESTNET_API_KEY=your_binance_testnet_api_key_here
BINANCE_TESTNET_API_SECRET=your_binance_testnet_secret_here

# BYBIT TESTNET
BYBIT_TESTNET_API_KEY=your_bybit_testnet_api_key_here
BYBIT_TESTNET_API_SECRET=your_bybit_testnet_secret_here

# INTERACTIVE BROKERS
IB_GATEWAY_HOST=127.0.0.1
IB_GATEWAY_PORT=7497
IB_CLIENT_ID=1

# DATABENTO (Market Data)
DATABENTO_API_KEY=your_databento_api_key_here

# REDIS (isteğe bağlı)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# LOGGING
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/nautilus_trader.log
```

### Ortam Değişkenlerini Yükleme

Python kodunuzda ortam değişkenlerini yükleyin:

```python
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API anahtarlarını al
BINANCE_API_KEY = os.getenv("BINANCE_TESTNET_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_TESTNET_API_SECRET")
```

## Sandbox Trading Bot Yapılandırması

### 1. Temel Imports

```python
import asyncio
import os
from decimal import Decimal
from dotenv import load_dotenv

from nautilus_trader.config import InstrumentProviderConfig
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import LiveRiskEngineConfig  # RiskEngineConfig yerine LiveRiskEngineConfig

from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.binance.config import BinanceExecClientConfig
# Factory imports kaldırıldı - artık gerekli değil
# from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
# from nautilus_trader.adapters.binance.factories import BinanceLiveExecClientFactory

from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.identifiers import TraderId
```

### 2. Strateji Yapılandırması

```python
# Kendi stratejinizi import edin veya EMACross örneğini kullanın
from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig

# Strateji konfigürasyonu
strategy_config = EMACrossConfig(
    instrument_id="BTCUSDT.BINANCE",  # Trading pair
    bar_type="BTCUSDT.BINANCE-1-MINUTE-LAST-EXTERNAL",
    fast_ema_period=10,
    slow_ema_period=20,
    trade_size=Decimal("0.001"),  # BTC miktarı (dikkatli olun!)
)
```

### 3. Trading Node Konfigürasyonu

```python
def create_sandbox_config():
    # Ortam değişkenlerini yükle
    load_dotenv()
    
    return TradingNodeConfig(
        trader_id=TraderId("SANDBOX-TRADER-001"),
        logging=LoggingConfig(
            log_level="INFO",
            log_file_format="json",  # Yapılandırılmış logging
            log_to_file=True,
        ),
        exec_engine=ExecEngineConfig(
            allow_cash_positions=True,  # Nakit pozisyonlarına izin ver
        ),
        risk_engine=RiskEngineConfig(
            bypass=False,  # Risk kontrollerini etkinleştir
            max_order_submit_rate="100/00:00:01",  # Saniyede max 100 emir
            max_order_modify_rate="100/00:00:01",
            max_notional_per_order={
                "USD": 1000,  # Emir başına max $1000
                "BTC": 0.1,   # Emir başına max 0.1 BTC
            },
        ),
        data_engine=DataEngineConfig(
            validate_data_sequence=True,  # Veri sırasını doğrula
        ),
        # Binance adapter yapılandırması
        data_clients={
            "BINANCE": BinanceDataClientConfig(
                api_key=os.getenv("BINANCE_TESTNET_API_KEY"),
                api_secret=os.getenv("BINANCE_TESTNET_API_SECRET"),
                account_type=BinanceAccountType.SPOT,  # SPOT hesap türü
                testnet=True,  # Testnet modunu etkinleştir
                base_url_http="https://testnet.binance.vision",  # Testnet URL
                base_url_ws="wss://testnet.binance.vision",
            ),
        },
        exec_clients={
            "BINANCE": BinanceExecClientConfig(
                api_key=os.getenv("BINANCE_TESTNET_API_KEY"),
                api_secret=os.getenv("BINANCE_TESTNET_API_SECRET"),
                account_type=BinanceAccountType.SPOT,  # SPOT hesap türü
                testnet=True,  # Testnet modunu etkinleştir
                base_url_http="https://testnet.binance.vision",  # Testnet URL
                base_url_ws="wss://testnet.binance.vision",
            ),
        },
        timeout_connection=20.0,
        timeout_reconciliation=10.0,
        timeout_portfolio=10.0,
        timeout_disconnection=10.0,
    )
```

## Live Trading Engine Kurulumu

### Ana Trading Loop

```python
async def main():
    # Konfigürasyon oluştur
    config = create_sandbox_config()
    
    # Trading node'u oluştur
    node = TradingNode(config=config)
    
    # Strateji ekle
    strategy = EMACross(config=strategy_config)
    node.trader.add_strategy(strategy)
    
    try:
        # Node'u başlat
        await node.start_async()
        
        print("✅ Sandbox trading bot başlatıldı!")
        print("📊 Market verisi alınıyor...")
        print("🤖 Stratejiler aktif...")
        print("⏹️  Durdurmak için Ctrl+C basın")
        
        # Sonsuz döngüde çalışır (manuel durdurulana kadar)
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        # Temiz kapatma
        await node.stop_async()
        print("🔄 Trading bot kapatıldı")

if __name__ == "__main__":
    asyncio.run(main())
```

## Risk Yönetimi ve Güvenlik

### 1. Risk Kontrollerini Ayarlama

```python
risk_config = LiveRiskEngineConfig(  # RiskEngineConfig yerine LiveRiskEngineConfig
    bypass=False,  # Risk kontrollerini etkinleştir
    
    # Emir limitleri
    max_order_submit_rate="50/00:00:01",  # Saniyede max 50 emir
    max_order_modify_rate="50/00:00:01",
    
    # Pozisyon limitleri (Currency formatında)
    max_notional_per_order={
        "USDT": 500,   # Emir başına max 500 USDT
        "BTC": 0.05,   # Emir başına max 0.05 BTC
        "ETH": 0.5,    # Emir başına max 0.5 ETH
    },
    
    # Toplam pozisyon limitleri (Currency formatında)
    max_notionals={
        "USDT": 5000,  # Toplam pozisyon max 5000 USDT
        "BTC": 0.5,    # Toplam BTC pozisyonu max 0.5
    },
)
```

### 2. Güvenlik Best Practices

#### API Key Güvenliği
- **Hiçbir zaman** API anahtarlarınızı kod içine yazmayın
- **Ortam değişkenleri** veya **güvenli vault** kullanın
- **IP restriction** ayarlayın
- **Withdraw permission** vermeyin
- **Testnet anahtarları** kullanın

#### Kod Güvenliği
```python
# ✅ DOĞRU
api_key = os.getenv("BINANCE_TESTNET_API_KEY")
if not api_key:
    raise ValueError("API key bulunamadı! .env dosyasını kontrol edin.")

# ❌ YANLIŞ - Asla böyle yapmayın!
# api_key = "your_actual_api_key_here"
```

### 3. Position Sizing ve Risk Management

```python
from nautilus_trader.risk.engine import RiskEngine

class CustomRiskEngine(RiskEngine):
    def check_order_risk(self, order):
        # Özel risk kontrolleri
        if order.quantity * order.price > 1000:  # $1000'dan fazla
            self.log.warning(f"Büyük emir tespit edildi: {order}")
            return False  # Emri reddet
            
        return super().check_order_risk(order)
```

## Monitoring ve Logging

### 1. Detaylı Logging Yapılandırması

```python
import logging
from nautilus_trader.config import LoggingConfig

logging_config = LoggingConfig(
    log_level="INFO",
    # log_level_file="DEBUG",  # Bu parametre mevcut versiyonda desteklenmiyor
    # log_file_format="json",  # Bu parametre mevcut versiyonda desteklenmiyor
    # log_to_file=True,        # Bu parametre mevcut versiyonda desteklenmiyor
    # log_file_path="./logs/sandbox_trading_{date}.log",
    log_colors=True,  # Renkli console output
)
```

### 2. Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self, trader):
        self.trader = trader
        self.start_time = time.time()
        
    def print_stats(self):
        """Trading istatistiklerini yazdır"""
        portfolio = self.trader.portfolio
        
        print("\n📊 PERFORMANS RAPORU")
        print("=" * 50)
        print(f"🕐 Çalışma süresi: {time.time() - self.start_time:.0f} saniye")
        print(f"💰 Toplam PnL: {portfolio.net_position()}")
        print(f"📈 Açık pozisyonlar: {len(portfolio.positions_open())}")
        print(f"📋 Toplam emirler: {len(self.trader.orders())}")
        print(f"✅ Doldurulmuş emirler: {len([o for o in self.trader.orders() if o.is_filled])}")
        
# Kullanım
monitor = PerformanceMonitor(node.trader)

# Her 60 saniyede bir istatistikleri göster
async def stats_loop():
    while True:
        await asyncio.sleep(60)
        monitor.print_stats()

# Ana loop'a ekle
asyncio.create_task(stats_loop())
```

### 3. Real-time Alerting

```python
import requests
import json

class AlertManager:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url  # Slack/Discord webhook
        
    def send_alert(self, message, level="INFO"):
        """Alarm gönder"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "trader_id": "SANDBOX-TRADER-001"
        }
        
        # Console'a yazdır
        print(f"🚨 [{level}] {message}")
        
        # Webhook'a gönder (isteğe bağlı)
        if self.webhook_url:
            try:
                requests.post(self.webhook_url, json=alert)
            except Exception as e:
                print(f"Webhook gönderimi başarısız: {e}")

# Event handler'lara bağla
alert_manager = AlertManager()

def on_order_filled(event):
    alert_manager.send_alert(
        f"✅ Emir dolduruldu: {event.order_id} - {event.fill_qty} @ {event.fill_price}",
        level="SUCCESS"
    )

def on_position_opened(event):
    alert_manager.send_alert(
        f"📈 Pozisyon açıldı: {event.position.instrument_id} - {event.position.quantity}",
        level="INFO"
    )
```

## Troubleshooting

### Yaygın Sorunlar ve Çözümleri

#### 1. **LoggingConfig Parametreleri Hatası**

**Sorun:** `Unexpected keyword argument 'log_to_file'`
```
❌ Hata: Unexpected keyword argument 'log_to_file'
```

**Çözüm:**
Nautilus Trader'ın farklı versiyonlarında `LoggingConfig` parametreleri değişebilir. Eğer bu hatayı alıyorsanız:

```python
# ✅ DOĞRU - Temel LoggingConfig
logging_config = LoggingConfig(
    log_level="INFO",
    log_colors=True,
)

# ❌ YANLIŞ - Desteklenmeyen parametreler
# logging_config = LoggingConfig(
#     log_level="INFO",
#     log_to_file=True,        # Bu parametre eski versiyonlarda yok
#     log_file_path="./logs/", # Bu parametre eski versiyonlarda yok
# )
```

Alternatif olarak, Python'ın standart logging modülünü kullanabilirsiniz:

```python
import logging

# Dosyaya loglama için
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/nautilus_trader.log'),
        logging.StreamHandler()  # Console'a da yazdır
    ]
)
```

#### 2. **BinanceAccountType Hatası**

**Sorun:** `❌ Hata: SPOT_TESTNET`
```
❌ Hata: SPOT_TESTNET
💥 Beklenmeyen hata: SPOT_TESTNET
```

**Çözüm:**
Nautilus Trader'ın farklı versiyonlarında `BinanceAccountType` enum değerleri değişebilir. Eğer `SPOT_TESTNET` desteklenmiyorsa:

```python
# ✅ DOĞRU - Güncel yaklaşım
config=BinanceDataClientConfig(
    api_key=api_key,
    api_secret=api_secret,
    account_type=BinanceAccountType.SPOT,  # SPOT kullanın
    testnet=True,  # Ayrı bir testnet parametresi kullanın
    base_url_http="https://testnet.binance.vision",
    base_url_ws="wss://testnet.binance.vision",
)

# ❌ YANLIŞ - Eski versiyonda desteklenmeyen
# account_type=BinanceAccountType.SPOT_TESTNET,  # Bu enum değeri yok
```

Alternatif olarak, mevcut enum değerlerini kontrol etmek için:

```python
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
print(dir(BinanceAccountType))  # Mevcut enum değerlerini göster
```

#### 3. **Client Factory Hatası**

**Sorun:** `Unexpected keyword argument 'client_factory'`
```
❌ Hata: Unexpected keyword argument 'client_factory'
💥 Beklenmeyen hata: Unexpected keyword argument 'client_factory'
```

**Çözüm:**
Nautilus Trader'ın bu versiyonunda `LiveDataClientConfig` ve `LiveExecClientConfig` sınıfları `client_factory` parametresini kabul etmiyor. Doğrudan config sınıflarını kullanın:

```python
# ✅ DOĞRU - Doğrudan config kullanımı
data_clients={
    "BINANCE": BinanceDataClientConfig(
        api_key=api_key,
        api_secret=api_secret,
        account_type=BinanceAccountType.SPOT,
        testnet=True,
        base_url_http="https://testnet.binance.vision",
        base_url_ws="wss://testnet.binance.vision",
    ),
}

# ❌ YANLIŞ - client_factory parametresi desteklenmiyor
# data_clients={
#     "BINANCE": LiveDataClientConfig(
#         client_factory=BinanceLiveDataClientFactory,  # Bu desteklenmiyor
#         config=BinanceDataClientConfig(...),
#     ),
# }
```

Aynı durum `exec_clients` için de geçerlidir.

#### 4. **InstrumentId Parsing Hatası**

**Sorun:** `❌ Hata: Error parsing InstrumentId from 'USD': missing '.' separator between symbol and venue components`

```
❌ Hata: Error parsing `InstrumentId` from 'USD': missing '.' separator between symbol and venue components
❌ Hata: Error parsing `InstrumentId` from 'BTC': missing '.' separator between symbol and venue components
```

**Çözüm:**
Nautilus Trader'da tüm enstrümanlar `symbol.venue` formatında tanımlanmalıdır. Sadece `USD`, `BTC` gibi kısaltmalar kullanılamaz.

```python
# ✅ DOĞRU - InstrumentId formatları
from nautilus_trader.model.identifiers import InstrumentId

# Trading çiftleri için
instrument_id = InstrumentId.from_str("BTCUSDT.BINANCE")
symbol = "BTCUSDT.BINANCE"

# Para birimleri için (Currency kod olarak kullanılır)
base_currency = "USDT"  # InstrumentId değil, Currency
quote_currency = "BTC"

# Risk management'te para birimleri Currency olarak kullanılır
max_notional_per_order={
    "USDT": 500,   # Currency kod
    "BTC": 0.05,   # Currency kod
    "ETH": 0.5,    # Currency kod
}

# ❌ YANLIŞ - ExamplerInstrumentId formatları
# instrument_id = InstrumentId.from_str("USD")      # Venue eksik
# instrument_id = InstrumentId.from_str("BTC")      # Venue eksik  
# instrument_id = InstrumentId.from_str("BTCUSDT")  # Venue eksik
```

**Doğru kullanım örnekleri:**

```python
# Strateji konfigürasyonunda
strategy_config = EMACrossConfig(
    instrument_id="BTCUSDT.BINANCE",  # symbol.venue formatı
    bar_type="BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL",
    fast_ema_period=10,
    slow_ema_period=20,
    trade_size=Decimal("0.01"),
)

# Veri subscription'da
instruments = [
    "BTCUSDT.BINANCE",
    "ETHUSDT.BINANCE", 
    "ADAUSDT.BINANCE",
]

# Bar subscription'da
bars = [
    "BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL",
    "ETHUSDT.BINANCE-5-MINUTE-LAST-INTERNAL",
]
```

**Binance için geçerli venue isimleri:**
- `BINANCE` - Spot trading
- `BINANCE_FUTURES` - Futures trading  
- `BINANCE_OPTIONS` - Options trading (nadir kullanılır)

**Popüler trading çiftleri:**
```python
# Major cryptocurrency pairs
"BTCUSDT.BINANCE"   # Bitcoin/Tether
"ETHUSDT.BINANCE"   # Ethereum/Tether  
"BNBUSDT.BINANCE"   # Binance Coin/Tether
"ADAUSDT.BINANCE"   # Cardano/Tether
"DOTUSDT.BINANCE"   # Polkadot/Tether
"SOLUSDT.BINANCE"   # Solana/Tether

# BTC pairs
"ETHBTC.BINANCE"    # Ethereum/Bitcoin
"BNBBTC.BINANCE"    # Binance Coin/Bitcoin
"ADABTC.BINANCE"    # Cardano/Bitcoin
```

#### 4. **RiskEngineConfig Hatası**

**Sorun:** `Cannot use 'RiskEngineConfig' in a 'live' environment. Try using a 'LiveRiskEngineConfig'.`
```
❌ Hata: Cannot use `RiskEngineConfig` in a 'live' environment. Try using a `LiveRiskEngineConfig`.
```

**Çözüm:**
Live trading environment'ta `RiskEngineConfig` yerine `LiveRiskEngineConfig` kullanmanız gerekir:

```python
# ✅ DOĞRU - Live environment için
from nautilus_trader.config import LiveRiskEngineConfig

risk_engine=LiveRiskEngineConfig(
    bypass=False,
    max_order_submit_rate="10/00:00:01",
    max_notional_per_order={"USD": 100},
)

# ❌ YANLIŞ - Live environment'ta desteklenmiyor
# from nautilus_trader.config import RiskEngineConfig  # Bu live'da çalışmaz
# risk_engine=RiskEngineConfig(...)  # Bu live'da çalışmaz
```

`LiveRiskEngineConfig` genellikle `RiskEngineConfig` ile aynı parametreleri kabul eder, ancak live trading ortamına özel ek kontroller içerir.

#### 5. **Bağlantı Sorunları**

**Sorun:** `ConnectionError` veya `TimeoutError`
```
ERROR: Failed to connect to Binance WebSocket
```

**Çözüm:**
- İnternet bağlantınızı kontrol edin
- Testnet URL'lerinin doğru olduğunu onaylayın
- Firewall/proxy ayarlarını kontrol edin
- API rate limitlerini aşmadığınızdan emin olun

#### 2. **API Key Sorunları**

**Sorun:** `Invalid API Key` veya `Permission denied`
```
ERROR: 401 Unauthorized - Invalid API Key
```

**Çözüm:**
- API anahtarının doğru kopyalandığından emin olun
- Testnet anahtarını mainnet URL'leriyle kullanmıyor olduğunuzdan emin olun
- IP restriction ayarlarını kontrol edin
- API key permissions'ları kontrol edin

#### 3. **Veri Alma Sorunları**

**Sorun:** Market data alınamıyor
```
WARNING: No market data received for BTCUSDT.BINANCE
```

**Çözüm:**
- Symbol'ün testnet'te mevcut olduğunu kontrol edin
- WebSocket bağlantısının aktif olduğunu onaylayın
- Subscribe edilmiş enstrümanları kontrol edin

#### 4. **Emir Gönderme Sorunları**

**Sorun:** Emirler doldurulmuyor
```
ERROR: Order rejected - Insufficient balance
```

**Çözüm:**
- Testnet hesabınızda yeterli test bakiyesi olduğundan emin olun
- Minimum order size gereksinimlerini kontrol edin
- Risk limitlerinizi kontrol edin

### Debug Mode Etkinleştirme

```python
import logging

# Tüm modüller için debug logging
logging.basicConfig(level=logging.DEBUG)

# Nautilus Trader için özel debug
logging.getLogger("nautilus_trader").setLevel(logging.DEBUG)

# Network trafiğini izleme
logging.getLogger("websockets").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
```

## Örnek Kod ve Yapılandırmalar

### Tam Çalışan Örnek: `sandbox_trader.py`

```python
#!/usr/bin/env python3
"""
Nautilus Trader Sandbox Mode Live Trading Example
Bu script Binance Testnet'te sandbox trading yapar.
"""

import asyncio
import os
import signal
import sys
from decimal import Decimal
from dotenv import load_dotenv

from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.config import LiveRiskEngineConfig  # RiskEngineConfig yerine LiveRiskEngineConfig
# LiveDataClientConfig ve LiveExecClientConfig kaldırıldı
# from nautilus_trader.config import LiveDataClientConfig
# from nautilus_trader.config import LiveExecClientConfig

from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
from nautilus_trader.adapters.binance.config import BinanceExecClientConfig
# Factory imports artık gerekli değil
# from nautilus_trader.adapters.binance.factories import BinanceLiveDataClientFactory
# from nautilus_trader.adapters.binance.factories import BinanceLiveExecClientFactory

from nautilus_trader.examples.strategies.ema_cross import EMACross
from nautilus_trader.examples.strategies.ema_cross import EMACrossConfig

from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.identifiers import TraderId


class SandboxTrader:
    def __init__(self):
        self.node = None
        self.running = False
        
    def create_config(self):
        """Trading node konfigürasyonu oluştur"""
        load_dotenv()
        
        # API anahtarlarını kontrol et
        api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError(
                "Binance Testnet API anahtarları bulunamadı!\n"
                ".env dosyasında BINANCE_TESTNET_API_KEY ve BINANCE_TESTNET_API_SECRET "
                "değişkenlerini ayarlayın."
            )
        
        return TradingNodeConfig(
            trader_id=TraderId("SANDBOX-001"),
            logging=LoggingConfig(
                log_level="INFO",
                log_colors=True,
                # log_to_file parametresi mevcut versiyonda desteklenmiyor
                # log_file_path="./logs/sandbox_trader.log",
            ),        risk_engine=LiveRiskEngineConfig(  # RiskEngineConfig yerine LiveRiskEngineConfig
            bypass=False,  # Risk kontrollerini etkinleştir
            max_order_submit_rate="10/00:00:01",  # Saniyede max 10 emir
            max_notional_per_order={"USD": 100},  # Küçük emirler
        ),
            data_clients={
                "BINANCE": BinanceDataClientConfig(
                    api_key=api_key,
                    api_secret=api_secret,
                    account_type=BinanceAccountType.SPOT,  # SPOT hesap türü
                    testnet=True,  # Testnet modunu etkinleştir
                    base_url_http="https://testnet.binance.vision",
                    base_url_ws="wss://testnet.binance.vision",
                ),
            },
            exec_clients={
                "BINANCE": BinanceExecClientConfig(
                    api_key=api_key,
                    api_secret=api_secret,
                    account_type=BinanceAccountType.SPOT,  # SPOT hesap türü
                    testnet=True,  # Testnet modunu etkinleştir
                    base_url_http="https://testnet.binance.vision",
                    base_url_ws="wss://testnet.binance.vision",
                ),
            },
        )
    
    def create_strategy(self):
        """EMA Cross stratejisi oluştur"""
        return EMACross(
            config=EMACrossConfig(
                instrument_id="BTCUSDT.BINANCE",
                bar_type="BTCUSDT.BINANCE-1-MINUTE-LAST-EXTERNAL",
                fast_ema_period=10,
                slow_ema_period=20,
                trade_size=Decimal("0.001"),  # 0.001 BTC
            )
        )
    
    async def run(self):
        """Ana trading loop"""
        try:
            # Konfigürasyon oluştur
            config = self.create_config()
            
            # Trading node oluştur
            self.node = TradingNode(config=config)
            
            # Strateji ekle
            strategy = self.create_strategy()
            self.node.trader.add_strategy(strategy)
            
            # Signal handler'ları ayarla
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Node'u başlat
            await self.node.start_async()
            self.running = True
            
            print("🚀 Sandbox Trader başlatıldı!")
            print("📊 Market verileri alınıyor...")
            print("🤖 EMA Cross stratejisi aktif...")
            print("📈 Trading pair: BTCUSDT")
            print("⏹️  Durdurmak için Ctrl+C basın\n")
            
            # Ana döngü
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu")
        except Exception as e:
            print(f"❌ Hata: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Trading node'u durdur"""
        if self.node:
            print("🔄 Trading node kapatılıyor...")
            await self.node.stop_async()
            print("✅ Trading node kapatıldı")
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Signal handler (Ctrl+C vs)"""
        print(f"\n📶 Signal alındı: {signum}")
        self.running = False


async def main():
    """Ana fonksiyon"""
    # Log dizini oluştur
    os.makedirs("./logs", exist_ok=True)
    
    # Trader'ı başlat
    trader = SandboxTrader()
    await trader.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Güle güle!")
    except Exception as e:
        print(f"💥 Beklenmeyen hata: {e}")
        sys.exit(1)
```

### Yapılandırma Dosyası: `config.yaml`

```yaml
# config.yaml
trader_id: "SANDBOX-TRADER-001"

# Logging
logging:
  log_level: "INFO"
  log_colors: true
  # log_to_file: true        # Bu parametre mevcut versiyonda desteklenmiyor
  # log_file_path: "./logs/nautilus_trader.log"

# Risk Engine
risk_engine:
  bypass: false
  max_order_submit_rate: "10/00:00:01"
  max_order_modify_rate: "10/00:00:01"
  max_notional_per_order:
    USDT: 1000  # Currency kodu kullanın
    BTC: 0.1

# Data clients
data_clients:
  BINANCE:
    # factory referansı kaldırıldı - artık gerekli değil
    account_type: "SPOT"  # SPOT hesap türü
    testnet: true         # Testnet modunu etkinleştir
    base_url_http: "https://testnet.binance.vision"
    base_url_ws: "wss://testnet.binance.vision"

# Execution clients
exec_clients:
  BINANCE:
    # factory referansı kaldırıldı - artık gerekli değil
    account_type: "SPOT"  # SPOT hesap türü
    testnet: true         # Testnet modunu etkinleştir
    base_url_http: "https://testnet.binance.vision"
    base_url_ws: "wss://testnet.binance.vision"

# Strategies
strategies:
  - strategy_path: "nautilus_trader.examples.strategies.ema_cross:EMACross"
    config_path: "nautilus_trader.examples.strategies.ema_cross:EMACrossConfig"
    config:
      instrument_id: "BTCUSDT.BINANCE"
      bar_type: "BTCUSDT.BINANCE-1-MINUTE-LAST-EXTERNAL"
      fast_ema_period: 10
      slow_ema_period: 20
      trade_size: "0.001"
```

### Docker Compose Setup: `docker-compose.yml`

```yaml
# docker-compose.yml
version: '3.8'

services:
  nautilus-sandbox:
    build: .
    container_name: nautilus-sandbox-trader
    environment:
      - BINANCE_TESTNET_API_KEY=${BINANCE_TESTNET_API_KEY}
      - BINANCE_TESTNET_API_SECRET=${BINANCE_TESTNET_API_SECRET}
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./.env:/app/.env
    restart: unless-stopped
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    container_name: nautilus-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  postgres:
    image: postgres:15-alpine
    container_name: nautilus-postgres
    environment:
      POSTGRES_DB: nautilus_trader
      POSTGRES_USER: nautilus
      POSTGRES_PASSWORD: password123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Log dizini oluştur
RUN mkdir -p /app/logs

# Uygulamayı çalıştır
CMD ["python", "sandbox_trader.py"]
```

### Requirements: `requirements.txt`

```txt
# requirements.txt
nautilus_trader[all]>=1.198.0
python-dotenv>=1.0.0
redis>=4.5.0
psycopg2-binary>=2.9.0
pyyaml>=6.0
requests>=2.28.0
websockets>=11.0
```

---

## Son Notlar

### ⚠️ Önemli Uyarılar

1. **Sadece Testnet Kullanın:** Bu döküman sadece sandbox/testnet ortamları için tasarlanmıştır.
2. **Gerçek Para Riski Yok:** Testnet'te gerçek para kaybı riski yoktur.
3. **Production'a Geçmeden Test Edin:** Stratejinizi iyice test etmeden gerçek paraya geçmeyin.
4. **API Limitleri:** Testnet'in de rate limitleri vardır, bunlara dikkat edin.
5. **Veri Kalitesi:** Testnet verileri bazen mainnet'ten farklı olabilir.

### 📚 Daha Fazla Kaynak

- **Nautilus Trader Documentation:** https://nautilustrader.io/docs/
- **Binance Testnet:** https://testnet.binance.vision/
- **Bybit Testnet:** https://testnet.bybit.com/
- **Interactive Brokers Paper Trading:** https://www.interactivebrokers.com/en/trading/tws-demo.php

### 🤝 Yardım ve Destek

- **GitHub Issues:** https://github.com/nautechsystems/nautilus_trader/issues
- **Discord Community:** Nautilus Trader Discord sunucusu
- **Documentation:** Resmi dökümantasyon sayfaları

---

Bu döküman ile Nautilus Trader'da sandbox mode live trading simulation yapmaya hazırsınız! Herhangi bir sorunla karşılaştığınızda bu dökümanı referans olarak kullanabilirsiniz.

**İyi tradeler! 🚀📈**
