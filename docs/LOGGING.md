# 📊 Enhanced Logging System

Nautilus Trader best practices ile geliştirilmiş logging sistemi.

## 🚀 Özellikler

### 📁 Log Dosyaları

1. **`bot_activity.json`** - Structured JSON logs (custom events)
2. **`bot_activity_enhanced.log`** - Enhanced text logs with function info
3. **`nautilus_bot_*.json`** - Nautilus Trader native logs (JSON format)
4. **`bot_activity.log`** - Basic custom logs (eski format)

### 🔧 Nautilus Trader Konfigürasyonu

```python
LoggingConfig(
    log_level="INFO",              # Console log level
    log_level_file="DEBUG",        # File log level (daha detaylı)
    log_colors=True,               # Console renkleri
    use_pyo3=True,                 # Rust component logging
    log_file_format="json",        # JSON format
    log_directory="/workspace/logs", # Log dizini
    log_file_name="nautilus_bot",   # Dosya ismi
    log_file_max_size=50_000_000,   # 50MB rotation
    log_file_max_backup_count=10,   # 10 backup dosya
    clear_log_file=False,          # Başlangıçta silme
    log_component_levels={         # Component-specific levels
        "Portfolio": "INFO",
        "DataEngine": "INFO", 
        "RiskEngine": "WARNING",
        "ExecEngine": "INFO",
        "TestStrategy": "DEBUG",
    },
)
```

### 📊 Custom Logger Features

1. **Rotating File Handler** - 50MB boyutunda otomatik rotation
2. **JSON Structured Logs** - Machine-readable format
3. **Trading Event Tracking** - Structured trading event logging
4. **Performance Metrics** - Metric logging sistemi
5. **Console Colors** - Renkli console output

## 🔍 Log Analizi

### Manual Analiz

```bash
# Real-time log takibi
tail -f logs/bot_activity.json

# JSON logs'u güzel formatla
cat logs/bot_activity.json | jq .

# Nautilus logs'u analiz et
cat logs/nautilus_bot_*.json | jq 'select(.level=="ERROR")'
```

### Automated Analiz

```bash
# Log istatistikleri
docker exec -it nautilus-trader python3 /workspace/scripts/analyze_logs.py --stats

# Specific dosya analizi
docker exec -it nautilus-trader python3 /workspace/scripts/analyze_logs.py --file bot_activity.json

# Tüm logları analiz et
docker exec -it nautilus-trader python3 /workspace/scripts/analyze_logs.py
```

## 📈 Structured Events

### Trading Events

```json
{
  "event_type": "account_balance",
  "timestamp": "2025-06-17T03:48:43.526298",
  "currency": "USDT", 
  "balance": "AccountBalance(...)",
  "venue": "BINANCE"
}
```

### Performance Metrics

```json
{
  "metric_type": "performance",
  "metric_name": "price_change",
  "value": 123.45,
  "unit": "price_units",
  "timestamp": "2025-06-17T03:48:43.526298"
}
```

### Bot Events

```json
{
  "event_type": "bot_startup",
  "timestamp": "2025-06-17T03:48:43.527081",
  "instrument": "BTCUSDT.BINANCE",
  "venue": "BINANCE",
  "mode": "simulation"
}
```

## 🛠️ Usage Examples

### Strategy'de Event Logging

```python
from logger_setup import log_trading_event, log_performance_metric

# Account balance event
log_trading_event(custom_logger, "account_balance", {
    "currency": "USDT",
    "balance": str(balance),
    "venue": "BINANCE"
})

# Performance metric
log_performance_metric(custom_logger, "price_change", 
                     float(price_diff), "price_units")
```

### Custom Logger Kullanımı

```python
from logger_setup import setup_custom_logger

logger = setup_custom_logger()
logger.info("🚀 Bot started")
logger.error("❌ Error occurred")
logger.debug("🐛 Debug info")
```

## 📊 Log Rotation

- **Size-based**: 50MB dosya boyutunda otomatik rotation
- **Backup Count**: En fazla 10 backup dosya tutulur
- **Automatic Cleanup**: Eski dosyalar otomatik silinir
- **Timestamp Naming**: Dosyalar timestamp ile adlandırılır

## 🔍 Monitoring

### Key Metrics to Watch

1. **Trading Events**: Account balances, trades, orders
2. **System Events**: Bot startup, shutdown, errors
3. **Performance**: Price changes, volume, execution times
4. **Errors**: Component errors, connection issues

### Alerting Opportunities

```bash
# Error monitoring
grep -E "ERROR|WARN" logs/nautilus_bot_*.json

# Trading activity
grep "TRADING_EVENT" logs/bot_activity.json

# Performance issues
grep "timeout\|failed\|error" logs/*.log
```

## 🚨 Best Practices

1. **Monitor Log Size**: Düzenli olarak log boyutlarını kontrol edin
2. **Error Tracking**: ERROR ve WARN seviyesindeki logları takip edin
3. **Performance Monitoring**: Metric loglarını analiz edin
4. **Backup Strategy**: Log dosyalarının backup'ını alın
5. **Real-time Monitoring**: tail -f ile real-time takip yapın

## 📝 Troubleshooting

### Common Issues

1. **Log files not created**: Container volume mount'unu kontrol edin
2. **Permission errors**: Container içinde log dizin izinlerini kontrol edin
3. **Large log files**: Rotation ayarlarını gözden geçirin
4. **Missing events**: Log level ayarlarını kontrol edin

### Debug Commands

```bash
# Container logs dizinini kontrol et
docker exec -it nautilus-trader ls -la /workspace/logs/

# Log file permissions
docker exec -it nautilus-trader ls -la /workspace/logs/*.log

# Container içinde log takibi
docker exec -it nautilus-trader tail -f /workspace/logs/bot_activity.json
```
