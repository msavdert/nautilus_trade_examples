# Risk Yönetimi

Risk yönetimi, trading botlarda en kritik konudur. Bu doküman, botunuzun güvenli şekilde çalışması için gerekli risk yönetimi tekniklerini kapsar.

## 🎯 Risk Yönetimi Nedir?

Risk yönetimi, potansiyel kayıpları kontrol altına almak ve sermayeyi korumak için uygulanan teknik ve stratejilerin bütünüdür.

### Temel İlkeler
1. **Sermayeyi Koru**: İlk öncelik para kaybetmemek
2. **Küçük Riskler Al**: Her işlemde küçük risk al
3. **Diversifikasyon**: Riskleri dağıt
4. **Disiplin**: Kurallara uy, duyguları kontrol et

## 💰 Position Sizing (Pozisyon Boyutlandırma)

### 1. Sabit Risk Yöntemi
```python
def calculate_position_size(self, entry_price: float, stop_price: float) -> float:
    """
    Sabit risk yöntemi ile position size hesaplama
    """
    account_balance = self.portfolio.net_liquidation_value()
    risk_per_trade = 0.01  # %1 risk
    
    # Risk miktarı
    max_risk_amount = account_balance * risk_per_trade
    
    # Stop loss mesafesi
    stop_distance = abs(entry_price - stop_price)
    
    # Position size
    position_size = max_risk_amount / stop_distance
    
    return min(position_size, account_balance * 0.1)  # Max %10 pozisyon
```

### 2. Volatilite Bazlı Sizing
```python
def calculate_position_size_atr(self, atr_value: float) -> float:
    """
    ATR (Average True Range) bazlı position sizing
    """
    account_balance = self.portfolio.net_liquidation_value()
    risk_per_trade = 0.01
    
    # ATR'nin 2 katını stop loss olarak kullan
    stop_distance = atr_value * 2
    
    max_risk_amount = account_balance * risk_per_trade
    position_size = max_risk_amount / stop_distance
    
    return position_size
```

### 3. Kelly Criterion
```python
def kelly_position_size(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
    """
    Kelly Criterion ile optimal position size
    """
    if avg_loss == 0:
        return 0.0
    
    win_loss_ratio = avg_win / avg_loss
    kelly_percentage = win_rate - ((1 - win_rate) / win_loss_ratio)
    
    # Kelly'nin yarısını kullan (daha konservativ)
    return max(0.0, kelly_percentage * 0.5)
```

## 🛡️ Stop Loss Stratejileri

### 1. Percentage Stop Loss
```python
class PercentageStopLoss:
    def __init__(self, percentage: float = 0.02):
        self.percentage = percentage
    
    def calculate_stop_price(self, entry_price: float, side: OrderSide) -> float:
        if side == OrderSide.BUY:
            return entry_price * (1 - self.percentage)
        else:
            return entry_price * (1 + self.percentage)
```

### 2. ATR Stop Loss
```python
class ATRStopLoss:
    def __init__(self, atr_multiplier: float = 2.0):
        self.atr_multiplier = atr_multiplier
    
    def calculate_stop_price(self, entry_price: float, atr: float, side: OrderSide) -> float:
        stop_distance = atr * self.atr_multiplier
        
        if side == OrderSide.BUY:
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance
```

### 3. Trailing Stop Loss
```python
class TrailingStopLoss:
    def __init__(self, trail_distance: float = 0.02):
        self.trail_distance = trail_distance
        self.current_stop = None
    
    def update_stop(self, current_price: float, side: OrderSide) -> float:
        if side == OrderSide.BUY:
            new_stop = current_price * (1 - self.trail_distance)
            if self.current_stop is None or new_stop > self.current_stop:
                self.current_stop = new_stop
        else:
            new_stop = current_price * (1 + self.trail_distance)
            if self.current_stop is None or new_stop < self.current_stop:
                self.current_stop = new_stop
        
        return self.current_stop
```

## 📊 Risk Metrics (Risk Ölçümleri)

### 1. Maximum Drawdown
```python
class DrawdownTracker:
    def __init__(self):
        self.peak_value = 0
        self.max_drawdown = 0
    
    def update(self, current_value: float):
        if current_value > self.peak_value:
            self.peak_value = current_value
        
        current_drawdown = (self.peak_value - current_value) / self.peak_value
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
    
    def get_max_drawdown_percentage(self) -> float:
        return self.max_drawdown * 100
```

### 2. Sharpe Ratio
```python
def calculate_sharpe_ratio(returns: list, risk_free_rate: float = 0.02) -> float:
    """
    Sharpe Ratio hesaplama
    """
    import numpy as np
    
    returns_array = np.array(returns)
    excess_returns = returns_array - risk_free_rate
    
    if np.std(excess_returns) == 0:
        return 0.0
    
    return np.mean(excess_returns) / np.std(excess_returns)
```

### 3. Win Rate Tracking
```python
class PerformanceTracker:
    def __init__(self):
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0
        self.winning_pnl = 0
        self.losing_pnl = 0
    
    def add_trade(self, pnl: float):
        self.total_trades += 1
        self.total_pnl += pnl
        
        if pnl > 0:
            self.winning_trades += 1
            self.winning_pnl += pnl
        else:
            self.losing_pnl += pnl
    
    def get_win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades
    
    def get_profit_factor(self) -> float:
        if self.losing_pnl == 0:
            return float('inf')
        return abs(self.winning_pnl / self.losing_pnl)
```

## ⚠️ Risk Kontrol Sistemleri

### 1. Daily Loss Limit
```python
class DailyLossLimit:
    def __init__(self, max_daily_loss: float):
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = 0
        self.last_reset_date = None
    
    def check_and_update(self, current_pnl: float) -> bool:
        """
        Returns True if trading is allowed, False if daily limit exceeded
        """
        from datetime import date
        
        # Günlük reset
        today = date.today()
        if self.last_reset_date != today:
            self.daily_pnl = 0
            self.last_reset_date = today
        
        self.daily_pnl += current_pnl
        
        return self.daily_pnl > -self.max_daily_loss
```

### 2. Maximum Positions Limit
```python
class PositionLimiter:
    def __init__(self, max_positions: int = 3):
        self.max_positions = max_positions
    
    def can_open_new_position(self, portfolio) -> bool:
        open_positions = len([pos for pos in portfolio.positions_open() 
                            if pos.is_open])
        return open_positions < self.max_positions
```

### 3. Correlation Check
```python
class CorrelationChecker:
    def __init__(self, max_correlation: float = 0.7):
        self.max_correlation = max_correlation
    
    def check_correlation(self, new_symbol: str, existing_positions: list) -> bool:
        """
        Yeni pozisyonun mevcut pozisyonlarla korelasyonunu kontrol et
        """
        # Basitleştirilmiş örnek - gerçekte fiyat korelasyonu hesaplanmalı
        correlated_symbols = {
            'BTCUSDT': ['ETHUSDT', 'ADAUSDT'],
            'ETHUSDT': ['BTCUSDT', 'LINKUSDT'],
            # ... diğer korelasyonlar
        }
        
        for position in existing_positions:
            if position.instrument_id.symbol.value in correlated_symbols.get(new_symbol, []):
                return False
        
        return True
```

## 🚨 Emergency Controls

### 1. Circuit Breaker
```python
class CircuitBreaker:
    def __init__(self, max_loss_percentage: float = 0.05):
        self.max_loss_percentage = max_loss_percentage
        self.initial_balance = None
        self.is_triggered = False
    
    def check(self, current_balance: float) -> bool:
        if self.initial_balance is None:
            self.initial_balance = current_balance
            return True
        
        loss_percentage = (self.initial_balance - current_balance) / self.initial_balance
        
        if loss_percentage >= self.max_loss_percentage:
            self.is_triggered = True
            return False
        
        return True
```

### 2. Market Volatility Filter
```python
class VolatilityFilter:
    def __init__(self, max_volatility: float = 0.05):
        self.max_volatility = max_volatility
    
    def is_market_stable(self, recent_returns: list) -> bool:
        import numpy as np
        
        if len(recent_returns) < 10:
            return True
        
        volatility = np.std(recent_returns)
        return volatility < self.max_volatility
```

## 🔧 Pratik Implementation

### Complete Risk Manager
```python
class RiskManager:
    def __init__(self, config):
        self.config = config
        self.daily_loss_limit = DailyLossLimit(config.max_daily_loss)
        self.position_limiter = PositionLimiter(config.max_positions)
        self.circuit_breaker = CircuitBreaker(config.max_portfolio_loss)
        self.performance_tracker = PerformanceTracker()
    
    def can_open_position(self, portfolio, symbol: str, size: float) -> tuple[bool, str]:
        """
        Returns (can_open, reason)
        """
        # Daily loss check
        if not self.daily_loss_limit.check_and_update(0):
            return False, "Daily loss limit exceeded"
        
        # Position count check
        if not self.position_limiter.can_open_new_position(portfolio):
            return False, "Maximum positions limit reached"
        
        # Circuit breaker check
        current_balance = portfolio.net_liquidation_value()
        if not self.circuit_breaker.check(current_balance):
            return False, "Circuit breaker triggered"
        
        # Position size check
        max_position_value = current_balance * self.config.max_position_percentage
        if size > max_position_value:
            return False, f"Position too large. Max: {max_position_value}"
        
        return True, "OK"
    
    def calculate_optimal_size(self, entry_price: float, stop_price: float, 
                             current_balance: float) -> float:
        """
        Optimal position size hesaplama
        """
        risk_amount = current_balance * self.config.risk_per_trade
        stop_distance = abs(entry_price - stop_price)
        
        if stop_distance == 0:
            return 0
        
        size = risk_amount / stop_distance
        max_size = current_balance * self.config.max_position_percentage
        
        return min(size, max_size)
```

## 📈 Monitoring ve Alerting

### 1. Risk Alerts
```python
class RiskAlertSystem:
    def __init__(self, config):
        self.config = config
        self.alert_thresholds = {
            'drawdown': 0.03,      # %3 drawdown'da alert
            'daily_loss': 0.02,    # %2 günlük kayıp
            'win_rate': 0.4        # %40'ın altında win rate
        }
    
    def check_alerts(self, metrics: dict):
        alerts = []
        
        if metrics['drawdown'] > self.alert_thresholds['drawdown']:
            alerts.append(f"High drawdown: {metrics['drawdown']:.2%}")
        
        if metrics['daily_pnl'] < -self.alert_thresholds['daily_loss']:
            alerts.append(f"Daily loss alert: {metrics['daily_pnl']:.2f}")
        
        if metrics['win_rate'] < self.alert_thresholds['win_rate']:
            alerts.append(f"Low win rate: {metrics['win_rate']:.2%}")
        
        return alerts
```

## 💡 Best Practices

### 1. Risk Configuration
```python
# risk_config.py
class RiskConfig:
    # Position sizing
    RISK_PER_TRADE = 0.01          # %1 per trade
    MAX_POSITION_PCT = 0.1         # Max %10 per position
    MAX_TOTAL_RISK = 0.05          # Max %5 total portfolio risk
    
    # Stop losses
    DEFAULT_STOP_LOSS = 0.02       # %2 stop loss
    MAX_STOP_LOSS = 0.05           # Max %5 stop loss
    
    # Daily limits
    MAX_DAILY_LOSS = 0.03          # Max %3 daily loss
    MAX_DAILY_TRADES = 10          # Max 10 trades per day
    
    # Portfolio limits
    MAX_DRAWDOWN = 0.1             # %10 max drawdown
    MAX_POSITIONS = 3              # Max 3 open positions
```

### 2. Logging Risk Events
```python
import logging

risk_logger = logging.getLogger('risk_management')

def log_risk_event(event_type: str, details: dict):
    risk_logger.warning(f"Risk Event: {event_type}", extra=details)

# Usage
log_risk_event("POSITION_REJECTED", {
    "symbol": "BTCUSDT",
    "reason": "Daily loss limit exceeded",
    "current_loss": -150.50
})
```

## 📚 Sonraki Adımlar

1. Risk parametrelerinizi backtest ile optimize edin
2. Real-time monitoring sistemini kurun
3. Alerting mekanizmalarını test edin
4. Risk raporları oluşturun

---
**Kritik Not**: Risk yönetimi asla ihmal edilmemelidir. Her stratejide mutlaka implement edilmelidir.
