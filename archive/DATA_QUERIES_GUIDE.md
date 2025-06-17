# 🔍 PostgreSQL Historical Data - Hızlı Rehber

## 📊 Temel Sorgular

### 1. Hazırlık
```bash
# Sistem çalışıyor mu kontrol et
docker-compose ps

# Query script'ini test et
./test_queries.sh
```

### 2. Bar Data (OHLCV)
```bash
# Son 100 bar
python3 query_historical_data.py --bars BTCUSDT --limit 100

# Tarih aralığı ile
python3 query_historical_data.py --bars BTCUSDT --start 2025-06-15 --end 2025-06-16

# 5 dakikalık barlar
python3 query_historical_data.py --bars BTCUSDT --timeframe 5-MINUTE --limit 50

# CSV'ye kaydet
python3 query_historical_data.py --bars BTCUSDT --limit 1000 --output btc_bars.csv
```

### 3. Tick Data (Trade Verileri)
```bash
# Son trade'ler
python3 query_historical_data.py --ticks BTCUSDT --limit 50

# Belirli tarihler
python3 query_historical_data.py --ticks BTCUSDT --start 2025-06-16 --limit 100
```

### 4. Trading İstatistikleri
```bash
# Son 7 günün özeti
python3 query_historical_data.py --stats BTCUSDT --days 7

# Son 30 günün özeti
python3 query_historical_data.py --stats BTCUSDT --days 30
```

### 5. Order ve Position History
```bash
# Order geçmişi
python3 query_historical_data.py --orders --limit 20

# Position geçmişi
python3 query_historical_data.py --positions --limit 20

# Belirli trader için
python3 query_historical_data.py --orders --trader-id SANDBOX-TRADER-001
```

### 6. PostgreSQL'e Direkt Bağlanma
```bash
# Container içinden
docker exec -it nautilus-postgres psql -U trading_user -d nautilus_trading

# Host'tan (port 5433)
psql -h localhost -p 5433 -U trading_user -d nautilus_trading
```

### 7. Yararlı SQL Sorguları
```sql
-- Tüm tabloları listele
\dt

-- Son 24 saatin bar'ları
SELECT ts_event, open, high, low, close, volume 
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%' 
  AND ts_event >= NOW() - INTERVAL '24 hours'
ORDER BY ts_event DESC;

-- Günlük volume analizi
SELECT 
    DATE(ts_event) as date,
    COUNT(*) as bar_count,
    SUM(volume) as total_volume,
    AVG(close) as avg_price,
    MIN(low) as daily_low,
    MAX(high) as daily_high
FROM bars 
WHERE bar_type LIKE '%BTCUSDT%1-MINUTE%'
GROUP BY DATE(ts_event)
ORDER BY date DESC;

-- Trading performance
SELECT 
    trader_id,
    COUNT(*) as total_positions,
    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as profitable,
    SUM(realized_pnl) as total_pnl,
    AVG(realized_pnl) as avg_pnl
FROM positions 
GROUP BY trader_id;
```

### 8. Data Export
```bash
# Büyük veri setini CSV'ye export
python3 query_historical_data.py --bars BTCUSDT --start 2025-06-01 --output historical_data.csv

# PostgreSQL'den direkt export
docker exec -it nautilus-postgres psql -U trading_user -d nautilus_trading -c "\copy (SELECT * FROM bars WHERE bar_type LIKE '%BTCUSDT%' ORDER BY ts_event) TO '/tmp/export.csv' WITH CSV HEADER;"
```

## 🔧 Troubleshooting

### Bağlantı Problemi
```bash
# Container status kontrol
docker-compose ps

# PostgreSQL logları
docker-compose logs nautilus-postgres

# Network testi
docker exec nautilus-sandbox-trader ping nautilus-postgres
```

### Performance Problemi
```sql
-- Slow query'leri bulma
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Index durumu
SELECT schemaname, tablename, indexname, idx_scan 
FROM pg_stat_user_indexes 
ORDER BY idx_scan DESC;
```

### Disk Kullanımı
```sql
-- Database boyutu
SELECT 
    pg_size_pretty(pg_database_size('nautilus_trading')) as db_size;

-- Tablo boyutları
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename) DESC;
```

## 💡 İpuçları

1. **Büyük sorgular için**: `LIMIT` kullanın
2. **Tarih filtreleri**: Index'li sorgular için `ts_event` kullanın
3. **Performance**: `EXPLAIN ANALYZE` ile query planını inceleyin
4. **Backup**: Önemli verileri düzenli olarak yedekleyin
5. **Monitoring**: Query sürelerini takip edin

## 📚 Daha Detaylı Bilgi

- [POSTGRESQL_QUERIES.md](POSTGRESQL_QUERIES.md) - Detaylı SQL sorguları
- [SYSTEM_OPTIMIZATION.md](SYSTEM_OPTIMIZATION.md) - Sistem optimizasyonları
- [README.md](README.md) - Ana dokümantasyon
