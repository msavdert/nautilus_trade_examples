# Trading Bot Geliştirme Temelleri

Bu doküman, trading bot geliştirirken bilmeniz gereken temel konuları kapsar.

## 🎯 Trading Bot Nedir?

Trading bot, önceden programlanmış kurallar doğrultusunda otomatik olarak alım/satım işlemleri yapan yazılımdır.

### Avantajları
- ✅ **7/24 Çalışma**: Hiç durmadan piyasayı takip eder
- ✅ **Disiplin**: Duygu faktörünü ortadan kaldırır  
- ✅ **Hız**: Millisaniyeler içinde işlem yapar
- ✅ **Backtest**: Geçmiş verilerle test edilebilir

### Dezavantajları
- ❌ **Teknik Risk**: Kod hatası büyük kayıplara neden olabilir
- ❌ **Piyasa Değişimi**: Değişen piyasa koşullarına adapte olmayabilir
- ❌ **Over-optimization**: Geçmiş verilere fazla uyum

## 📊 Temel Trading Kavramları

### 1. Market Structure
- **Trend**: Fiyatın genel yönü (yukarı/aşağı/yatay)
- **Support**: Fiyatın düşmekte zorlandığı seviye
- **Resistance**: Fiyatın yükselmekte zorlandığı seviye
- **Volume**: İşlem hacmi

### 2. Order Types
```python
# Market Order - Hemen al/sat
order = order_factory.market(
    instrument_id=instrument_id,
    order_side=OrderSide.BUY,
    quantity=quantity
)

# Limit Order - Belirli fiyatta al/sat
order = order_factory.limit(
    instrument_id=instrument_id,
    order_side=OrderSide.BUY,
    quantity=quantity,
    price=Price.from_str("50000.00")
)

# Stop Loss - Zarar durdur
order = order_factory.stop_market(
    instrument_id=instrument_id,
    order_side=OrderSide.SELL,
    quantity=quantity,
    trigger_price=Price.from_str("48000.00")
)
```

### 3. Position Sizing
```python
# Risk bazlı position sizing
account_balance = 1000.0  # USDT
risk_per_trade = 0.02     # %2 risk
stop_loss_distance = 0.05 # %5 stop loss

position_size = (account_balance * risk_per_trade) / stop_loss_distance
# Position size = 1000 * 0.02 / 0.05 = 400 USDT
```

## 🛠️ Temel Strategi Bileşenleri

### 1. Entry Signal (Giriş Sinyali)
```python
def should_buy(self, bar: Bar) -> bool:
    """Buy sinyali kontrolü"""
    # EMA cross stratejisi örneği
    ema_short = self.indicators['ema_short'].value
    ema_long = self.indicators['ema_long'].value
    
    return ema_short > ema_long and self.previous_ema_short <= self.previous_ema_long
```

### 2. Exit Signal (Çıkış Sinyali)
```python
def should_sell(self, bar: Bar) -> bool:
    """Sell sinyali kontrolü"""
    ema_short = self.indicators['ema_short'].value
    ema_long = self.indicators['ema_long'].value
    
    return ema_short < ema_long and self.previous_ema_short >= self.previous_ema_long
```

### 3. Risk Management
```python
def calculate_stop_loss(self, entry_price: Price, side: OrderSide) -> Price:
    """Stop loss hesaplama"""
    stop_loss_pct = 0.02  # %2
    
    if side == OrderSide.BUY:
        return Price.from_str(str(float(entry_price) * (1 - stop_loss_pct)))
    else:
        return Price.from_str(str(float(entry_price) * (1 + stop_loss_pct)))
```

## 📈 Popüler Trading Stratejileri

### 1. EMA Cross Strategy
- **Mantık**: Kısa EMA, uzun EMA'yı yukarı keserse AL, aşağı keserse SAT
- **Avantaj**: Basit ve etkili
- **Dezavantaj**: Trend değişimlerinde geç sinyal

### 2. RSI Mean Reversion
- **Mantık**: RSI 30'un altındaysa AL, 70'in üstündeyse SAT
- **Avantaj**: Aşırı alım/satım seviyelerini yakalar
- **Dezavantaj**: Güçlü trendlerde yanlış sinyal

### 3. Bollinger Bands
- **Mantık**: Fiyat alt banda değerse AL, üst banda değerse SAT
- **Avantaj**: Volatiliteye uyum sağlar
- **Dezavantaj**: Karmaşık parametre ayarı

### 4. Support/Resistance Breakout
- **Mantık**: Önemli seviyelerin kırılmasında işlem
- **Avantaj**: Güçlü hareket yakalar
- **Dezavantaj**: False breakout riski

## ⚠️ Yaygın Hatalar

### 1. Over-fitting
```python
# ❌ Yanlış - Çok fazla parametre
if (ema5 > ema10 and ema10 > ema20 and rsi > 60 and 
    macd > signal and volume > avg_volume * 1.5 and 
    close > sma50 and price_change > 0.02):
    return True

# ✅ Doğru - Basit ve net
if ema_short > ema_long and rsi < 70:
    return True
```

### 2. Position Size Hatası
```python
# ❌ Yanlış - Sabit miktar
quantity = 100.0  # Her zaman aynı miktar

# ✅ Doğru - Risk bazlı sizing
max_risk = account_balance * 0.02
stop_distance = abs(entry_price - stop_price) / entry_price
quantity = max_risk / stop_distance
```

### 3. Stop Loss Unutma
```python
# ❌ Yanlış - Stop loss yok
self.submit_order(market_order)

# ✅ Doğru - Her zaman stop loss
self.submit_order(market_order)
stop_order = self.order_factory.stop_market(...)
self.submit_order(stop_order)
```

## 🔧 Development Best Practices

### 1. Kod Organizasyonu
```python
class MyStrategy(Strategy):
    """
    Açık ve anlaşılır strateji sınıfı
    """
    
    def __init__(self):
        # Parametreleri açık bir şekilde tanımla
        self.ema_short_period = 12
        self.ema_long_period = 26
        self.risk_per_trade = 0.02
    
    def on_start(self):
        """Strateji başlatma"""
        self._setup_indicators()
        self._setup_risk_management()
    
    def on_bar(self, bar: Bar):
        """Ana trading logic"""
        self._update_indicators(bar)
        self._check_entry_signals(bar)
        self._check_exit_signals(bar)
        self._update_risk_management()
```

### 2. Logging
```python
import logging

class MyStrategy(Strategy):
    def on_trade(self, trade: Trade):
        self.log.info(
            f"Trade executed: {trade.side} {trade.quantity} "
            f"at {trade.price} - PnL: {trade.realized_pnl}"
        )
```

### 3. Configuration
```python
# config.py
class StrategyConfig:
    EMA_SHORT = 12
    EMA_LONG = 26
    RISK_PER_TRADE = 0.02
    MAX_POSITION_SIZE = 1000.0
    STOP_LOSS_PCT = 0.02
```

## 📖 Sonraki Adımlar

1. [Risk Yönetimi](risk-management.md) - Detaylı risk yönetimi teknikleri
2. [Binance Spot Testnet Bot](bot-guides/binance-spot-testnet.md) - İlk botunuzu oluşturun
3. Backtest yapmayı öğrenin
4. Live trading'e geçmeden önce extensive testing yapın

---
**Uyarı**: Trading risklidir. Bu doküman eğitim amaçlıdır, yatırım tavsiyesi değildir.
