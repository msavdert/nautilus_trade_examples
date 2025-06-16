#!/usr/bin/env python3
"""
Nautilus Trader - Hızlı Test Script
Bu script temel konfigürasyonları test eder ve sorunları tespit eder.
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Ortam değişkenlerini test et"""
    print("🔍 Ortam değişkenleri kontrol ediliyor...")
    
    load_dotenv()
    
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
    
    if not api_key:
        print("❌ BINANCE_TESTNET_API_KEY bulunamadı!")
        return False
        
    if not api_secret:
        print("❌ BINANCE_TESTNET_API_SECRET bulunamadı!")
        return False
        
    print("✅ API anahtarları bulundu")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"   Secret: {api_secret[:8]}...{api_secret[-4:]}")
    
    return True

def test_imports():
    """Gerekli paketlerin import edilebilirliğini test et"""
    print("\n📦 Paket importları test ediliyor...")
    
    try:
        import nautilus_trader
        print(f"✅ nautilus_trader {nautilus_trader.__version__}")
    except ImportError as e:
        print(f"❌ nautilus_trader import edilemedi: {e}")
        return False
    
    try:
        from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
        print("✅ Binance adapter")
    except ImportError as e:
        print(f"❌ Binance adapter import edilemedi: {e}")
        return False
    
    try:
        from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig
        print("✅ EMA Cross strategy")
    except ImportError as e:
        print(f"❌ EMA Cross strategy import edilemedi: {e}")
        return False
    
    return True

def test_instrumentid():
    """InstrumentId formatlarını test et"""
    print("\n🎯 InstrumentId formatları test ediliyor...")
    
    try:
        from nautilus_trader.model.identifiers import InstrumentId
        
        # Doğru formatlar
        valid_instruments = [
            "BTCUSDT.BINANCE",
            "ETHUSDT.BINANCE", 
            "BNBUSDT.BINANCE",
        ]
        
        for instrument_str in valid_instruments:
            try:
                instrument_id = InstrumentId.from_str(instrument_str)
                print(f"✅ {instrument_str} -> {instrument_id}")
            except Exception as e:
                print(f"❌ {instrument_str} hatalı: {e}")
                return False
        
        # Hatalı formatları test et
        print("\n⚠️  Hatalı formatlar test ediliyor...")
        invalid_instruments = ["USD", "BTC", "BTCUSDT"]
        
        for instrument_str in invalid_instruments:
            try:
                instrument_id = InstrumentId.from_str(instrument_str)
                print(f"⚠️  {instrument_str} beklenmedik şekilde geçerli: {instrument_id}")
            except Exception as e:
                print(f"✅ {instrument_str} beklenen şekilde hatalı: {str(e)[:50]}...")
        
    except ImportError as e:
        print(f"❌ InstrumentId import edilemedi: {e}")
        return False
    
    return True

def test_config():
    """Konfigürasyon oluşturmayı test et"""
    print("\n⚙️  Konfigürasyon oluşturma test ediliyor...")
    
    try:
        load_dotenv()
        api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        
        if not api_key or not api_secret:
            print("❌ API anahtarları eksik, config testi atlanıyor")
            return False
        
        from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
        from nautilus_trader.adapters.binance.config import BinanceDataClientConfig
        
        # Binance config test
        config = BinanceDataClientConfig(
            api_key=api_key,
            api_secret=api_secret,
            account_type=BinanceAccountType.SPOT,
            testnet=True,
            base_url_http="https://testnet.binance.vision",
            base_url_ws="wss://testnet.binance.vision",
        )
        
        print("✅ Binance config oluşturuldu")
        
        return True
        
    except Exception as e:
        print(f"❌ Config oluşturulamadı: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🧪 Nautilus Trader - Hızlı Test")
    print("=" * 50)
    
    tests = [
        ("Ortam Değişkenleri", test_environment),
        ("Paket İmportları", test_imports),
        ("InstrumentId Formatları", test_instrumentid),
        ("Konfigürasyon", test_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} Test Ediliyor...")
        print("-" * 30)
        
        try:
            if test_func():
                print(f"✅ {test_name} testi BAŞARILI")
                passed += 1
            else:
                print(f"❌ {test_name} testi BAŞARISIZ")
        except Exception as e:
            print(f"💥 {test_name} testi hata verdi: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Sonuçları: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Sandbox trader çalıştırılabilir.")
        print("🚀 Çalıştırmak için: python sandbox_trader.py")
    else:
        print("⚠️  Bazı testler başarısız. Sorunları çözün ve tekrar deneyin.")
        print("📚 Detaylar için SANDBOX.md dosyasını kontrol edin.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
