#!/bin/sh
# 🔧 System Optimization Script for Nautilus Trader
# ================================================
# Bu script Redis'in sistem uyarılarını minimize etmek için
# bazı kernel parametrelerini ayarlar.

echo "🔧 Nautilus Trader sistem optimizasyonları başlatılıyor..."

# Memory overcommit ayarı (Redis için)
# Bu ayar container içinde çalışmayabilir, ancak denemeye değer
if [ -w /proc/sys/vm/overcommit_memory ]; then
    echo 1 > /proc/sys/vm/overcommit_memory 2>/dev/null || echo "⚠️  Memory overcommit ayarlanamadı (normal durum)"
else
    echo "ℹ️  Memory overcommit ayarı container içinde yapılamıyor (normal durum)"
fi

# TCP backlog ayarı
if [ -w /proc/sys/net/core/somaxconn ]; then
    echo 1024 > /proc/sys/net/core/somaxconn 2>/dev/null || echo "⚠️  TCP backlog ayarlanamadı"
else
    echo "ℹ️  TCP backlog ayarı container içinde yapılamıyor"
fi

echo "✅ Sistem optimizasyonları tamamlandı"
echo "📊 Nautilus Trader başlatılıyor..."

# Ana script'i çalıştır
exec "$@"
