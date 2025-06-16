# 📊 PostgreSQL Historical Data Sorguları

## Nautilus Trader Historical Data Rehberi

Bu dokümantasyon, Nautilus Trader PostgreSQL veritabanındaki historical dataları nasıl sorgulayacağınızı gösterir.

### 1. PostgreSQL'e Bağlanma Yöntemleri

#### A. Docker Container Üzerinden:
```bash
# PostgreSQL container'ına bağlan:
docker exec -it nautilus-postgres psql -U trading_user -d nautilus_trading

# Veya .env dosyasındaki değişkenlerle:
docker exec -it nautilus-postgres psql -U ${POSTGRES_USERNAME} -d ${POSTGRES_DATABASE}
```

#### B. Host'tan Bağlanma:
```bash
# psql client kullanarak (port 5433'ten):
psql -h localhost -p 5433 -U trading_user -d nautilus_trading

# Şifre: .env dosyasındaki POSTGRES_PASSWORD
```

#### C. pgAdmin veya DBeaver ile GUI:
- Host: localhost
- Port: 5433
- Database: nautilus_trading
- Username: trading_user
- Password: .env dosyasındaki değer

### 2. Nautilus Trader Database Schema

#### Temel Tablolar:
```sql
-- Tüm tabloları listele:
\dt

-- Tablo yapısını incele:
\d table_name

-- Yaygın tablolar:
\d bars            -- OHLCV bar data
\d ticks           -- Tick data (trades)
\d quotes          -- Quote data (bid/ask)
\d orders          -- Order history
\d trades          -- Executed trades
\d positions       -- Position history
\d accounts        -- Account states
\d instruments     -- Instrument definitions
```

### 3. Historical Data Sorguları

#### A. Bar Data (OHLCV) Sorguları:
```sql
-- Son 100 BTCUSDT 1-dakika barları:
SELECT 
    ts_event,
    open,
    high,
    low,
    close,
    volume
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
ORDER BY ts_event DESC 
LIMIT 100;

-- Belirli tarih aralığındaki barlar:
SELECT 
    ts_event,
    open,
    high,
    low,
    close,
    volume
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
  AND ts_event >= '2025-06-15 00:00:00'
  AND ts_event <= '2025-06-16 23:59:59'
ORDER BY ts_event ASC;

-- Günlük OHLCV özeti:
SELECT 
    DATE(ts_event) as date,
    MIN(open) as day_open,
    MAX(high) as day_high,
    MIN(low) as day_low,
    MAX(close) as day_close,
    SUM(volume) as total_volume
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
GROUP BY DATE(ts_event)
ORDER BY date DESC;
```

#### B. Tick Data Sorguları:
```sql
-- Son trade tick'leri:
SELECT 
    ts_event,
    price,
    size,
    aggressor_side,
    trade_id
FROM ticks 
WHERE instrument_id = 'BTCUSDT.BINANCE'
  AND tick_type = 'TRADE'
ORDER BY ts_event DESC 
LIMIT 50;

-- Belirli fiyat aralığındaki trade'ler:
SELECT 
    ts_event,
    price,
    size,
    aggressor_side
FROM ticks 
WHERE instrument_id = 'BTCUSDT.BINANCE'
  AND tick_type = 'TRADE'
  AND price BETWEEN 100000 AND 110000
ORDER BY ts_event DESC;

-- Saatlik trade volume analizi:
SELECT 
    DATE_TRUNC('hour', ts_event) as hour,
    COUNT(*) as trade_count,
    SUM(size) as total_volume,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM ticks 
WHERE instrument_id = 'BTCUSDT.BINANCE'
  AND tick_type = 'TRADE'
GROUP BY DATE_TRUNC('hour', ts_event)
ORDER BY hour DESC;
```

#### C. Quote Data Sorguları:
```sql
-- Son bid/ask quote'ları:
SELECT 
    ts_event,
    bid_price,
    ask_price,
    bid_size,
    ask_size,
    (ask_price - bid_price) as spread
FROM ticks 
WHERE instrument_id = 'BTCUSDT.BINANCE'
  AND tick_type = 'QUOTE'
ORDER BY ts_event DESC 
LIMIT 50;

-- Spread analizi:
SELECT 
    DATE_TRUNC('minute', ts_event) as minute,
    AVG(ask_price - bid_price) as avg_spread,
    MIN(ask_price - bid_price) as min_spread,
    MAX(ask_price - bid_price) as max_spread
FROM ticks 
WHERE instrument_id = 'BTCUSDT.BINANCE'
  AND tick_type = 'QUOTE'
GROUP BY DATE_TRUNC('minute', ts_event)
ORDER BY minute DESC;
```

#### D. Trading Performance Sorguları:
```sql
-- Executed orders:
SELECT 
    ts_event,
    order_id,
    instrument_id,
    order_side,
    order_type,
    quantity,
    price,
    status
FROM orders 
WHERE trader_id = 'SANDBOX-TRADER-001'
ORDER BY ts_event DESC;

-- Position history:
SELECT 
    ts_event,
    instrument_id,
    position_side,
    quantity,
    avg_px_open,
    avg_px_close,
    unrealized_pnl,
    realized_pnl
FROM positions 
WHERE trader_id = 'SANDBOX-TRADER-001'
ORDER BY ts_event DESC;

-- Trading günlük P&L:
SELECT 
    DATE(ts_event) as date,
    SUM(realized_pnl) as daily_pnl,
    COUNT(*) as trade_count
FROM positions 
WHERE trader_id = 'SANDBOX-TRADER-001'
  AND realized_pnl != 0
GROUP BY DATE(ts_event)
ORDER BY date DESC;
```

### 4. Python'dan Historical Data Erişimi

#### A. Direct PostgreSQL Connection:
```python
import psql2
import pandas as pd
from decimal import Decimal

# Connection string (.env'den değerleri al)
conn_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# DataFrame olarak data çek:
def get_historical_bars(symbol, start_date, end_date):
    query = """
    SELECT 
        ts_event,
        open,
        high,
        low,
        close,
        volume
    FROM bars 
    WHERE bar_type LIKE %s
      AND ts_event >= %s
      AND ts_event <= %s
    ORDER BY ts_event ASC
    """
    
    with psycopg2.connect(conn_string) as conn:
        df = pd.read_sql_query(
            query, 
            conn, 
            params=[f'%{symbol}%1-MINUTE%', start_date, end_date]
        )
    
    return df

# Kullanım:
df = get_historical_bars('BTCUSDT', '2025-06-15', '2025-06-16')
print(df.head())
```

#### B. Nautilus Trader Data Client Kullanarak:
```python
from nautilus_trader.core.datetime import dt_to_unix_nanos
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.data import BarType

# Data client'tan historical data çek:
def get_nautilus_historical_data():
    # Bar type tanımla
    instrument_id = InstrumentId.from_str("BTCUSDT.BINANCE")
    bar_type = BarType.from_str("BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL")
    
    # Cache'den data çek
    bars = cache.bars(bar_type)
    
    # Veya database'den direkt çek
    bars = cache.load_bars(bar_type)
    
    return bars

# DataFrame'e çevir:
def bars_to_dataframe(bars):
    data = []
    for bar in bars:
        data.append({
            'timestamp': bar.ts_event,
            'open': float(bar.open),
            'high': float(bar.high),
            'low': float(bar.low),
            'close': float(bar.close),
            'volume': float(bar.volume)
        })
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ns')
    return df
```

### 5. Useful Analysis Queries

#### A. Technical Analysis Hazırlığı:
```sql
-- Moving averages için data:
SELECT 
    ts_event,
    close,
    AVG(close) OVER (
        ORDER BY ts_event 
        ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
    ) as ma_10,
    AVG(close) OVER (
        ORDER BY ts_event 
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as ma_20
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
ORDER BY ts_event DESC;

-- Volatility analysis:
SELECT 
    DATE(ts_event) as date,
    AVG(high - low) as avg_range,
    STDDEV(close) as price_volatility,
    (MAX(high) - MIN(low)) / AVG(close) * 100 as daily_range_pct
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
GROUP BY DATE(ts_event)
ORDER BY date DESC;
```

#### B. Trading Pattern Analysis:
```sql
-- Saatlik trading pattern:
SELECT 
    EXTRACT(hour from ts_event) as hour,
    AVG(volume) as avg_volume,
    COUNT(*) as bar_count,
    AVG(high - low) as avg_range
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
GROUP BY EXTRACT(hour from ts_event)
ORDER BY hour;

-- Volume spike detection:
SELECT 
    ts_event,
    volume,
    close,
    volume / AVG(volume) OVER (
        ORDER BY ts_event 
        ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING
    ) as volume_ratio
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
  AND volume > 0
ORDER BY ts_event DESC;
```

### 6. Data Export

#### A. CSV Export:
```sql
-- CSV dosyasına export:
\copy (SELECT ts_event, open, high, low, close, volume FROM bars WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%' ORDER BY ts_event) TO '/tmp/btcusdt_data.csv' WITH CSV HEADER;
```

#### B. Python ile Export:
```python
# DataFrame'i CSV'ye kaydet:
df.to_csv('historical_data.csv', index=False)

# Excel'e kaydet:
df.to_excel('historical_data.xlsx', index=False)

# Parquet format (büyük data için):
df.to_parquet('historical_data.parquet')
```

### 7. Performance Optimization

#### A. Index'ler:
```sql
-- Performans için index'ler:
CREATE INDEX IF NOT EXISTS idx_bars_instrument_time 
ON bars(instrument_id, ts_event);

CREATE INDEX IF NOT EXISTS idx_ticks_instrument_time 
ON ticks(instrument_id, ts_event);

-- Query performance check:
EXPLAIN ANALYZE SELECT * FROM bars WHERE bar_type LIKE '%BTCUSDT%' ORDER BY ts_event DESC LIMIT 100;
```

#### B. Data Retention:
```sql
-- Eski data temizliği (dikkatli kullan!):
DELETE FROM bars WHERE ts_event < NOW() - INTERVAL '30 days';
DELETE FROM ticks WHERE ts_event < NOW() - INTERVAL '7 days';
```

### 8. Monitoring & Maintenance

```sql
-- Database size:
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Row counts:
SELECT 
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables 
WHERE schemaname = 'public';
```

---

## 💡 İpuçları:

1. **Büyük sorgular için**: LIMIT kullanın ve pagination yapın
2. **Performans için**: Uygun index'leri kullanın  
3. **Memory kullanımı**: Büyük resultset'ler için streaming kullanın
4. **Backup**: Önemli dataları düzenli olarak yedekleyin
5. **Monitoring**: Query performance'ını takip edin

## 🔧 Troubleshooting:

- Connection error: `.env` dosyasındaki credentials'ları kontrol edin
- Slow queries: `EXPLAIN ANALYZE` ile query plan'ını inceleyin
- Memory issues: `work_mem` PostgreSQL parametresini artırın
- Lock issues: Uzun süreli transaction'ları kaçının
