# Binance Spot Testnet Bot Rehberi

Bu rehber, sıfırdan Binance Spot Testnet'te çalışan bir trading bot oluşturmanızı sağlar.

## 🎯 Önkoşullar

### 1. Binance Testnet Hesabı
1. [Binance Testnet](https://testnet.binance.vision/) adresine gidin
2. GitHub/Google ile giriş yapın
3. **API Management** bölümünden API keys oluşturun
4. **Spot Trading** izinlerini aktif edin

### 2. Development Environment
- Docker kurulu olmalı
- Git kurulu olmalı
- Temel Python bilgisi

## 🚀 Adım Adım Bot Oluşturma

### Adım 1: Environment Hazırlama

```bash
# 1. Projeyi klonlayın (zaten yaptınız)
cd nautilus_trade_examples

# 2. Environment variables dosyasını kopyalayın
cp .env.example .env

# 3. .env dosyasını düzenleyin
nano .env

# 4. Container'ı başlatın
docker-compose up -d

# 5. Container'a bağlanın
docker exec -it nautilus-trader bash
```

### Adım 2: Bot Projesi Oluşturma

```bash
# Container içinde
cd /workspace/bots/binance-spot-testnet

# Yeni bot projesi oluştur
uv init my-first-bot
cd my-first-bot

# Gerekli paketleri yükle
uv add nautilus_trader python-dotenv
```

### Adım 3: Environment Variables (.env dosyası)

```bash
# .env dosyanızda şunları doldurun:
BINANCE_TESTNET_API_KEY=your_api_key_here
BINANCE_TESTNET_API_SECRET=your_secret_here
SYMBOL=BTCUSDT
TRADE_SIZE=10.0
STOP_LOSS_PERCENTAGE=2.0
TAKE_PROFIT_PERCENTAGE=5.0
```

### Adım 4: Basit EMA Cross Strategy

`strategy.py` dosyası oluşturun:

```python
from decimal import Decimal
from nautilus_trader.indicators.average.ema import ExponentialMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.trading.strategy import Strategy


class EMACrossStrategy(Strategy):
    """
    Basit EMA Cross Strategy
    - Kısa EMA, uzun EMA'yı yukarı keserse BUY
    - Kısa EMA, uzun EMA'yı aşağı keserse SELL
    """

    def __init__(self, config=None):
        super().__init__(config)
        
        # Strategy parametreleri
        self.instrument_id = InstrumentId.from_str("BTCUSDT.BINANCE")
        self.trade_size = Decimal("10.0")  # USDT
        self.stop_loss_pct = Decimal("0.02")  # %2
        self.take_profit_pct = Decimal("0.05")  # %5
        
        # Indicators
        self.ema_short = ExponentialMovingAverage(12)
        self.ema_long = ExponentialMovingAverage(26)
        
        # State tracking
        self.previous_ema_short = None
        self.previous_ema_long = None

    def on_start(self):
        """Strategy başlatıldığında çalışır"""
        self.log.info("EMA Cross Strategy started")
        
        # Bar data subscription
        self.subscribe_bars(self.instrument_id)

    def on_bar(self, bar: Bar):
        """Her yeni bar'da çalışır"""
        # Indicators'ı güncelle
        self.ema_short.update_raw(float(bar.close))
        self.ema_long.update_raw(float(bar.close))
        
        # İlk değerler hazır değilse bekle
        if not self.ema_short.initialized or not self.ema_long.initialized:
            return
        
        # Cross sinyallerini kontrol et
        self._check_signals(bar)
        
        # Önceki değerleri sakla
        self.previous_ema_short = self.ema_short.value
        self.previous_ema_long = self.ema_long.value

    def _check_signals(self, bar: Bar):
        """Cross sinyallerini kontrol et"""
        current_short = self.ema_short.value
        current_long = self.ema_long.value
        
        # İlk bar için önceki değerler yoksa
        if self.previous_ema_short is None or self.previous_ema_long is None:
            return
        
        # Golden Cross (BUY signal)
        if (current_short > current_long and 
            self.previous_ema_short <= self.previous_ema_long):
            self._execute_buy(bar)
        
        # Death Cross (SELL signal)  
        elif (current_short < current_long and 
              self.previous_ema_short >= self.previous_ema_long):
            self._execute_sell(bar)

    def _execute_buy(self, bar: Bar):
        """Buy order execution"""
        # Mevcut pozisyon var mı kontrol et
        if self.portfolio.is_net_long(self.instrument_id):
            self.log.info("Already in long position, skipping buy signal")
            return
        
        # Mevcut short pozisyonu kapat
        if self.portfolio.is_net_short(self.instrument_id):
            self._close_all_positions()
        
        # Market order oluştur
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.BUY,
            quantity=self.instrument.make_qty(self.trade_size)
        )
        
        self.submit_order(order)
        self.log.info(f"BUY signal: EMA_SHORT={self.ema_short.value:.2f}, "
                     f"EMA_LONG={self.ema_long.value:.2f}")

    def _execute_sell(self, bar: Bar):
        """Sell order execution"""
        # Mevcut pozisyon var mı kontrol et
        if self.portfolio.is_net_short(self.instrument_id):
            self.log.info("Already in short position, skipping sell signal")
            return
        
        # Mevcut long pozisyonu kapat
        if self.portfolio.is_net_long(self.instrument_id):
            self._close_all_positions()
        
        # Market order oluştur
        order = self.order_factory.market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=self.instrument.make_qty(self.trade_size)
        )
        
        self.submit_order(order)
        self.log.info(f"SELL signal: EMA_SHORT={self.ema_short.value:.2f}, "
                     f"EMA_LONG={self.ema_long.value:.2f}")

    def _close_all_positions(self):
        """Tüm pozisyonları kapat"""
        for position in self.portfolio.positions_open():
            if position.instrument_id == self.instrument_id:
                order = self.order_factory.market(
                    instrument_id=self.instrument_id,
                    order_side=OrderSide.BUY if position.side.name == "SHORT" else OrderSide.SELL,
                    quantity=abs(position.quantity)
                )
                self.submit_order(order)

    def on_stop(self):
        """Strategy durdurulduğunda çalışır"""
        self.log.info("EMA Cross Strategy stopped")
        self._close_all_positions()
```

### Adım 5: Configuration Dosyası

`config.py` dosyası oluşturun:

```python
import os
from dotenv import load_dotenv
from nautilus_trader.config import TradingNodeConfig
from nautilus_trader.config import LoggingConfig
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceExecClientConfig

# .env dosyasını yükle
load_dotenv()

def create_config():
    """Trading node configuration oluştur"""
    
    # API credentials
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError("Binance API credentials not found in .env file")
    
    # Binance configuration
    binance_config = {
        "api_key": api_key,
        "api_secret": api_secret,
        "account_type": BinanceAccountType.SPOT,
        "testnet": True,
        "base_url_http": None,
        "base_url_ws": None,
    }
    
    # Trading node config
    config = TradingNodeConfig(
        trader_id="TRADER-001",
        
        # Logging
        logging=LoggingConfig(
            log_level="INFO",
            log_to_file=True,
            log_file_format="{time} | {level} | {name} | {message}",
        ),
        
        # Data clients
        data_clients={
            "BINANCE": BinanceDataClientConfig(**binance_config)
        },
        
        # Execution clients  
        exec_clients={
            "BINANCE": BinanceExecClientConfig(**binance_config)
        },
        
        # Risk management
        risk_engine={
            "max_order_rate": "100/00:00:01",  # Max 100 orders per second
            "max_notional_per_order": {
                "USDT": 1000  # Max $1000 per order
            }
        },
        
        # Strategy'ler sonra eklenecek
        strategies=[],
    )
    
    return config
```

### Adım 6: Main Bot Dosyası

`main.py` dosyası oluşturun:

```python
import asyncio
import signal
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.live.data import BinanceLiveDataClientFactory  
from nautilus_trader.adapters.binance.live.exec import BinanceLiveExecClientFactory
from nautilus_trader.live.node import TradingNode
from nautilus_trader.config import StrategyConfig

from config import create_config
from strategy import EMACrossStrategy


class BinanceSpotBot:
    """Binance Spot Trading Bot"""
    
    def __init__(self):
        self.node = None
        self.is_running = False
    
    async def start(self):
        """Bot'u başlat"""
        try:
            print("🚀 Binance Spot Bot başlatılıyor...")
            
            # Configuration oluştur
            config = create_config()
            
            # Trading node oluştur
            self.node = TradingNode(config=config)
            
            # Client factories ekle
            self.node.add_data_client_factory("BINANCE", BinanceLiveDataClientFactory)
            self.node.add_exec_client_factory("BINANCE", BinanceLiveExecClientFactory)
            
            # Strategy ekle
            strategy_config = StrategyConfig(strategy_id="EMA_CROSS_001")
            self.node.trader.add_strategy(EMACrossStrategy(strategy_config))
            
            # Node'u build et
            self.node.build()
            
            print("✅ Bot başarıyla konfigüre edildi")
            
            # Signal handlers
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Bot'u başlat
            await self.node.start()
            self.is_running = True
            
            print("🎯 Bot aktif - EMA Cross stratejisi çalışıyor...")
            print("📊 BTCUSDT çiftini izleme başlandı")
            print("⚠️  CTRL+C ile durdurun")
            
            # Sürekli çalışır durumda tut
            while self.is_running:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"❌ Bot başlatma hatası: {e}")
            raise
    
    async def stop(self):
        """Bot'u durdur"""
        if self.node and self.is_running:
            print("\n🛑 Bot durduruluyor...")
            self.is_running = False
            await self.node.stop()
            await self.node.dispose()
            print("✅ Bot başarıyla durduruldu")
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        print(f"\n📡 Signal {signum} alındı, bot durduruluyor...")
        self.is_running = False


async def main():
    """Main function"""
    bot = BinanceSpotBot()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n⚠️  Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
```

### Adım 7: Requirements Dosyası

`requirements.txt` oluşturun:

```txt
nautilus_trader
python-dotenv
```

## 🧪 Bot'u Test Etme

### Adım 1: Bağımlılıkları Kontrol Edin

```bash
# Container içinde
cd /workspace/bots/binance-spot-testnet/my-first-bot

# .env dosyasının doğru olduğunu kontrol edin
cat .env

# Dependencies kurulu mu kontrol edin
uv pip list | grep nautilus
```

### Adım 2: Configuration Test

```python
# config_test.py oluşturun
from config import create_config

try:
    config = create_config()
    print("✅ Configuration başarılı")
    print(f"API Key: {config.data_clients['BINANCE'].api_key[:10]}...")
except Exception as e:
    print(f"❌ Configuration hatası: {e}")
```

```bash
# Test çalıştır
uv run python config_test.py
```

### Adım 3: Bot'u Başlatın

```bash
# Bot'u çalıştır
uv run python main.py
```

**Beklenen çıktı:**
```
🚀 Binance Spot Bot başlatılıyor...
✅ Bot başarıyla konfigüre edildi
🎯 Bot aktif - EMA Cross stratejisi çalışıyor...
📊 BTCUSDT çiftini izleme başlandı
⚠️  CTRL+C ile durdurun
```

## 📊 Monitoring ve Logs

### Log Dosyalarını İzleme

```bash
# Container içinde log dosyalarını kontrol edin
tail -f /workspace/logs/*.log

# Ya da Python ile live log takibi
python -c "
import time
import os
log_dir = '/workspace/logs'
if os.path.exists(log_dir):
    files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if files:
        latest_log = sorted(files)[-1]
        print(f'Monitoring: {latest_log}')
        os.system(f'tail -f {log_dir}/{latest_log}')
"
```

### Performance Monitoring

Strategy'nize performans tracking ekleyin:

```python
# strategy.py içine ekleyin
def on_event(self, event):
    """Tüm events'leri logla"""
    if hasattr(event, 'type'):
        self.log.info(f"Event: {event.type} - {event}")

def on_order_filled(self, event):
    """Order fill events"""
    self.log.info(f"Order filled: {event.order_side} {event.quantity} at {event.avg_px}")

def on_position_opened(self, event):
    """Position açıldığında"""
    self.log.info(f"Position opened: {event.position}")

def on_position_closed(self, event):
    """Position kapandığında"""
    pnl = event.position.realized_pnl
    self.log.info(f"Position closed: PnL = {pnl}")
```

## ⚠️ Güvenlik ve Risk Yönetimi

### 1. API Key Güvenliği
```bash
# .env dosyasının git'e gitmediğini kontrol edin
cat .gitignore | grep .env

# Eğer yoksa ekleyin
echo ".env" >> .gitignore
```

### 2. Position Size Limits
Strategy'nize risk limitleri ekleyin:

```python
def _execute_buy(self, bar: Bar):
    # Maksimum pozisyon kontrolü
    portfolio_value = self.portfolio.net_liquidation_value()
    max_position_value = portfolio_value * Decimal("0.1")  # %10 max
    
    if self.trade_size > max_position_value:
        self.log.warning(f"Trade size too large: {self.trade_size} > {max_position_value}")
        return
    
    # ... rest of the method
```

### 3. Stop Loss Implementation
```python
def on_order_filled(self, event):
    """Order dolduktan sonra stop loss ekle"""
    if event.order.order_side == OrderSide.BUY:
        # Long pozisyon için stop loss
        stop_price = event.avg_px * (1 - self.stop_loss_pct)
        
        stop_order = self.order_factory.stop_market(
            instrument_id=self.instrument_id,
            order_side=OrderSide.SELL,
            quantity=event.quantity,
            trigger_price=self.instrument.make_price(stop_price)
        )
        
        self.submit_order(stop_order)
        self.log.info(f"Stop loss placed at {stop_price}")
```

## 🐛 Troubleshooting

### Yaygın Hatalar ve Çözümleri

#### 1. API Key Hatası
```
Error: Invalid API key
```
**Çözüm**: 
- .env dosyasındaki API key'leri kontrol edin
- Binance Testnet'te API key'in aktif olduğunu doğrulayın
- Spot trading izinlerinin açık olduğunu kontrol edin

#### 2. Connection Hatası
```
Error: Failed to connect to Binance
```
**Çözüm**:
- İnternet bağlantınızı kontrol edin
- Binance Testnet'in erişilebilir olduğunu doğrulayın
- Firewall ayarlarını kontrol edin

#### 3. Insufficient Balance
```
Error: Insufficient balance
```
**Çözüm**:
- Binance Testnet'te fake USDT alın
- Trade size'ı küçültün

### Debug Mode

Debug için strategy'yi geliştirin:

```python
class EMACrossStrategy(Strategy):
    def __init__(self, config=None):
        super().__init__(config)
        self.debug_mode = True  # Debug mode açık
        
    def on_bar(self, bar: Bar):
        if self.debug_mode:
            self.log.info(f"Bar: O={bar.open} H={bar.high} L={bar.low} C={bar.close}")
            
        # ... rest of the method
```

## 🎓 Sonraki Adımlar

### 1. Strategy Geliştirme
- RSI ekleyerek signal filtreleme
- Volume confirmation
- Multiple timeframe analysis

### 2. Risk Management
- [Risk Yönetimi Dokümantasyonu](../risk-management.md)'nu okuyun
- Position sizing algoritmaları
- Drawdown kontrolü

### 3. Backtesting
- Historical data ile strategy test etme
- Parameter optimizasyonu
- Performance metrics

### 4. Advanced Features
- Telegram/Discord notifications
- Database logging
- Multiple symbol trading

## 📚 Kaynaklar

- [Nautilus Trader Docs](https://nautilustrader.io/)
- [Binance API Docs](https://binance-docs.github.io/apidocs/spot/en/)
- [Trading Fundamentals](../trading-fundamentals.md)

---
**Başarılar!** İlk trading botunuzu oluşturdunuz. Küçük miktarlarla test edin ve adım adım geliştirin.
