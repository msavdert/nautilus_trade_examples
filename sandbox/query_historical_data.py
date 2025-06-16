#!/usr/bin/env python3
"""
📊 Nautilus Trader Historical Data Query Tool
============================================

Bu script PostgreSQL'deki historical dataları sorgulamak için
kolay kullanılabilir bir arayüz sağlar.

Kullanım:
    python query_historical_data.py --help
    python query_historical_data.py --bars BTCUSDT --start 2025-06-15 --end 2025-06-16
    python query_historical_data.py --ticks BTCUSDT --limit 1000
    python query_historical_data.py --stats BTCUSDT --days 7
"""

import os
import sys
import argparse
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from decimal import Decimal
import warnings
warnings.filterwarnings('ignore')

# .env dosyasından environment variables yükle
from dotenv import load_dotenv
load_dotenv()

class NautilusHistoricalData:
    def __init__(self):
        self.host = os.getenv('POSTGRES_HOST', 'localhost')
        self.port = os.getenv('POSTGRES_EXPOSED_PORT', '5433')
        self.database = os.getenv('POSTGRES_DATABASE', 'nautilus_trading')
        self.username = os.getenv('POSTGRES_USERNAME', 'trading_user')
        self.password = os.getenv('POSTGRES_PASSWORD', 'trading_pass')
        
        self.conn_string = f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        
    def connect(self):
        """PostgreSQL bağlantısı kur"""
        try:
            self.conn = psycopg2.connect(self.conn_string)
            print(f"✅ PostgreSQL'e bağlandı: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            print(f"❌ PostgreSQL bağlantı hatası: {e}")
            return False
    
    def get_tables(self):
        """Mevcut tabloları listele"""
        query = """
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename;
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            return df['tablename'].tolist()
        except Exception as e:
            print(f"❌ Tablo listesi alınamadı: {e}")
            return []
    
    def get_available_instruments(self):
        """Mevcut instrument'ları listele"""
        query = """
        SELECT DISTINCT 
            SPLIT_PART(bar_type, '.', 1) as symbol,
            COUNT(*) as bar_count
        FROM bars 
        GROUP BY SPLIT_PART(bar_type, '.', 1)
        ORDER BY bar_count DESC;
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"❌ Instrument listesi alınamadı: {e}")
            return pd.DataFrame()
    
    def get_bars(self, symbol, start_date=None, end_date=None, limit=None, timeframe='1-MINUTE'):
        """Historical bar data çek"""
        
        # Base query
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
        """
        
        params = [f'%{symbol}%{timeframe}%']
        
        # Date filters
        if start_date:
            query += " AND ts_event >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND ts_event <= %s"
            params.append(end_date)
        
        query += " ORDER BY ts_event DESC"
        
        # Limit
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            df['ts_event'] = pd.to_datetime(df['ts_event'])
            df = df.sort_values('ts_event').reset_index(drop=True)
            return df
        except Exception as e:
            print(f"❌ Bar data alınamadı: {e}")
            return pd.DataFrame()
    
    def get_ticks(self, symbol, start_date=None, end_date=None, limit=None, tick_type='TRADE'):
        """Historical tick data çek"""
        
        query = """
        SELECT 
            ts_event,
            price,
            size,
            aggressor_side,
            trade_id
        FROM ticks 
        WHERE instrument_id LIKE %s
          AND tick_type = %s
        """
        
        params = [f'%{symbol}%', tick_type]
        
        # Date filters
        if start_date:
            query += " AND ts_event >= %s"
            params.append(start_date)
        
        if end_date:
            query += " AND ts_event <= %s"
            params.append(end_date)
        
        query += " ORDER BY ts_event DESC"
        
        # Limit
        if limit:
            query += f" LIMIT {limit}"
        
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            if not df.empty:
                df['ts_event'] = pd.to_datetime(df['ts_event'])
                df = df.sort_values('ts_event').reset_index(drop=True)
            return df
        except Exception as e:
            print(f"❌ Tick data alınamadı: {e}")
            return pd.DataFrame()
    
    def get_trading_stats(self, symbol, days=7):
        """Trading istatistikleri"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Daily stats
        query = """
        SELECT 
            DATE(ts_event) as date,
            COUNT(*) as bar_count,
            MIN(low) as daily_low,
            MAX(high) as daily_high,
            AVG(close) as avg_price,
            SUM(volume) as total_volume,
            STDDEV(close) as volatility,
            (MAX(high) - MIN(low)) / AVG(close) * 100 as daily_range_pct
        FROM bars 
        WHERE bar_type LIKE %s
          AND ts_event >= %s
        GROUP BY DATE(ts_event)
        ORDER BY date DESC;
        """
        
        try:
            df = pd.read_sql_query(query, self.conn, params=[f'%{symbol}%', start_date])
            return df
        except Exception as e:
            print(f"❌ Trading stats alınamadı: {e}")
            return pd.DataFrame()
    
    def get_orders(self, trader_id='SANDBOX-TRADER-001', limit=50):
        """Order history"""
        
        query = """
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
        WHERE trader_id = %s
        ORDER BY ts_event DESC
        LIMIT %s;
        """
        
        try:
            df = pd.read_sql_query(query, self.conn, params=[trader_id, limit])
            if not df.empty:
                df['ts_event'] = pd.to_datetime(df['ts_event'])
            return df
        except Exception as e:
            print(f"❌ Order history alınamadı: {e}")
            return pd.DataFrame()
    
    def get_positions(self, trader_id='SANDBOX-TRADER-001', limit=50):
        """Position history"""
        
        query = """
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
        WHERE trader_id = %s
        ORDER BY ts_event DESC
        LIMIT %s;
        """
        
        try:
            df = pd.read_sql_query(query, self.conn, params=[trader_id, limit])
            if not df.empty:
                df['ts_event'] = pd.to_datetime(df['ts_event'])
            return df
        except Exception as e:
            print(f"❌ Position history alınamadı: {e}")
            return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description='Nautilus Trader Historical Data Query Tool')
    parser.add_argument('--list-tables', action='store_true', help='Mevcut tabloları listele')
    parser.add_argument('--list-instruments', action='store_true', help='Mevcut instrument\'ları listele')
    parser.add_argument('--bars', type=str, help='Bar data çek (örn: BTCUSDT)')
    parser.add_argument('--ticks', type=str, help='Tick data çek (örn: BTCUSDT)')
    parser.add_argument('--stats', type=str, help='Trading istatistikleri (örn: BTCUSDT)')
    parser.add_argument('--orders', action='store_true', help='Order history')
    parser.add_argument('--positions', action='store_true', help='Position history')
    parser.add_argument('--start', type=str, help='Başlangıç tarihi (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='Bitiş tarihi (YYYY-MM-DD)')
    parser.add_argument('--limit', type=int, help='Sonuç limiti')
    parser.add_argument('--days', type=int, default=7, help='İstatistik için gün sayısı')
    parser.add_argument('--timeframe', type=str, default='1-MINUTE', help='Timeframe (1-MINUTE, 5-MINUTE, etc.)')
    parser.add_argument('--output', type=str, help='CSV dosyasına kaydet')
    parser.add_argument('--trader-id', type=str, default='SANDBOX-TRADER-001', help='Trader ID')
    
    args = parser.parse_args()
    
    # Historical data client oluştur
    hd = NautilusHistoricalData()
    
    if not hd.connect():
        sys.exit(1)
    
    try:
        df = pd.DataFrame()
        
        if args.list_tables:
            tables = hd.get_tables()
            print("\n📋 Mevcut tablolar:")
            for table in tables:
                print(f"  - {table}")
        
        elif args.list_instruments:
            instruments = hd.get_available_instruments()
            print("\n📊 Mevcut instrument'lar:")
            print(instruments.to_string(index=False))
        
        elif args.bars:
            print(f"\n📈 {args.bars} bar data çekiliyor...")
            df = hd.get_bars(
                symbol=args.bars,
                start_date=args.start,
                end_date=args.end,
                limit=args.limit,
                timeframe=args.timeframe
            )
        
        elif args.ticks:
            print(f"\n📊 {args.ticks} tick data çekiliyor...")
            df = hd.get_ticks(
                symbol=args.ticks,
                start_date=args.start,
                end_date=args.end,
                limit=args.limit
            )
        
        elif args.stats:
            print(f"\n📈 {args.stats} trading istatistikleri çekiliyor...")
            df = hd.get_trading_stats(
                symbol=args.stats,
                days=args.days
            )
        
        elif args.orders:
            print(f"\n📋 Order history çekiliyor...")
            df = hd.get_orders(
                trader_id=args.trader_id,
                limit=args.limit or 50
            )
        
        elif args.positions:
            print(f"\n💼 Position history çekiliyor...")
            df = hd.get_positions(
                trader_id=args.trader_id,
                limit=args.limit or 50
            )
        
        else:
            parser.print_help()
            return
        
        # Sonuçları göster
        if not df.empty:
            print(f"\n✅ {len(df)} kayıt bulundu")
            print(f"\n📊 İlk 10 kayıt:")
            print(df.head(10).to_string(index=False))
            
            if len(df) > 10:
                print(f"\n... ({len(df) - 10} kayıt daha)")
            
            # CSV'ye kaydet
            if args.output:
                df.to_csv(args.output, index=False)
                print(f"\n💾 Data {args.output} dosyasına kaydedildi")
        
        else:
            print("\n❌ Hiç kayıt bulunamadı")
    
    except Exception as e:
        print(f"\n❌ Hata: {e}")
    
    finally:
        if hasattr(hd, 'conn'):
            hd.conn.close()

if __name__ == "__main__":
    main()
