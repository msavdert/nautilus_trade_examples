#!/usr/bin/env python3
"""
Nautilus Trader Minimal Test Script
Bu script Nautilus Trader'ın düzgün kurulup kurulmadığını test eder.
"""

def test_nautilus_import():
    """Nautilus Trader import testı"""
    try:
        import nautilus_trader
        print(f"✅ Nautilus Trader başarıyla import edildi!")
        
        # Version bilgisini güvenli şekilde al
        try:
            from nautilus_trader import __version__
            print(f"📦 Versiyon: {__version__}")
        except ImportError:
            print("📦 Versiyon bilgisi alınamadı (normal)")
            
        return True
    except ImportError as e:
        print(f"❌ Nautilus Trader import edilemedi: {e}")
        print("💡 Önce 'uv add nautilus_trader' komutunu çalıştırın")
        return False

def test_redis_connection():
    """Redis bağlantısını test eder"""
    try:
        import redis
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis bağlantısı başarılı!")
        
        # Test data yazıp oku
        test_key = "nautilus:test"
        test_value = "Hello Nautilus!"
        r.set(test_key, test_value)
        retrieved = r.get(test_key)
        
        if retrieved == test_value:
            print("✅ Redis write/read testi başarılı!")
            r.delete(test_key)  # Temizle
        else:
            print("❌ Redis write/read testi başarısız!")
        
        return True
    except Exception as e:
        print(f"❌ Redis bağlantısı başarısız: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🌊 Nautilus Trader Minimal Setup Test")
    print("=" * 40)
    
    # Import testı
    nautilus_ok = test_nautilus_import()
    print()
    
    # Redis testı  
    redis_ok = test_redis_connection()
    print()
    
    # Sonuç
    if nautilus_ok and redis_ok:
        print("🎉 Tüm testler başarılı! Setup hazır.")
        print()
        print("Sonraki adımlar:")
        print("1. Trading strategy'lerinizi yazın")
        print("2. Market data adaptörlerinizi yapılandırın")
        print("3. Backtest veya live trading'e başlayın")
    else:
        print("⚠️ Bazı testler başarısız oldu. Kurulumu kontrol edin.")

if __name__ == "__main__":
    main()
