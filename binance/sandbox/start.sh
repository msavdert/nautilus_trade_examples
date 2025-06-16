#!/bin/bash

# Nautilus Trader Minimal Setup - Başlangıç Script'i

echo "🌊 Nautilus Trader Minimal Setup"
echo "================================="
echo

# Önce Nautilus repository'nin clone edilip edilmediğini kontrol et
echo "📋 Ön kontroller..."

if [ ! -d "nautilus_trader" ]; then
    echo "⚠️  Nautilus Trader repository bulunamadı."
    echo "📥 Lütfen önce şu komutu çalıştırın:"
    echo "    git clone https://github.com/nautechsystems/nautilus_trader.git"
    echo
    read -p "Repository'yi şimdi clone etmek ister misiniz? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Nautilus Trader repository clone ediliyor..."
        git clone https://github.com/nautechsystems/nautilus_trader.git
        echo "✅ Clone tamamlandı!"
    else
        echo "❌ Repository olmadan devam edilemiyor. Çıkılıyor..."
        exit 1
    fi
fi

echo "✅ Ön kontroller tamamlandı!"
echo

# Docker servislerini başlat
echo "🚀 Docker servislerini başlatıyor..."
docker-compose up -d

echo
echo "⏳ Servislerin hazır olması bekleniyor..."
sleep 10

# Servis durumlarını kontrol et
echo "📊 Servis durumları:"
docker-compose ps

echo
echo "🧪 Setup testini çalıştırıyor..."
echo

# Test script'ini çalıştır
docker-compose exec -T nautilus-trader python test_setup.py

echo
echo "✅ Nautilus Trader Minimal Setup hazır!"
echo
echo "🔧 Kullanım örnekleri:"
echo "  docker-compose exec nautilus-trader bash          # İnteraktif shell"
echo "  docker-compose logs -f                            # Logları izle"
echo "  docker-compose down                               # Servisleri durdur"
echo
echo "📚 Daha fazla bilgi için README.md dosyasını okuyun."
