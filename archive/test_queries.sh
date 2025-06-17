#!/bin/bash
# 🧪 PostgreSQL Historical Data Test Script
# =========================================

echo "🔍 PostgreSQL Historical Data Sorguları Test Ediliyor..."
echo "================================================="

# Container çalışıyor mu kontrol et
if ! docker ps | grep -q "nautilus-postgres"; then
    echo "❌ PostgreSQL container çalışmıyor!"
    echo "🚀 Önce sistemi başlatın: docker-compose up -d"
    exit 1
fi

echo "✅ PostgreSQL container çalışıyor"

# Python script çalışıyor mu test et
echo ""
echo "📊 Mevcut tabloları listeliyorum..."
python3 query_historical_data.py --list-tables

echo ""
echo "📈 Mevcut instrument'ları listeliyorum..."
python3 query_historical_data.py --list-instruments

echo ""
echo "💾 BTCUSDT son 10 bar'ı alıyorum..."
python3 query_historical_data.py --bars BTCUSDT --limit 10

echo ""
echo "📊 BTCUSDT tick data (son 5)..."
python3 query_historical_data.py --ticks BTCUSDT --limit 5

echo ""
echo "📈 Son 7 günün trading istatistikleri..."
python3 query_historical_data.py --stats BTCUSDT --days 7

echo ""
echo "📋 Order history..."
python3 query_historical_data.py --orders --limit 5

echo ""
echo "💼 Position history..."
python3 query_historical_data.py --positions --limit 5

echo ""
echo "🎉 Test tamamlandı!"
echo ""
echo "💡 Daha fazla seçenek için:"
echo "   python3 query_historical_data.py --help"
