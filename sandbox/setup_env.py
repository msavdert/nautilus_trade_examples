#!/usr/bin/env python3
"""
Nautilus Trader - API Anahtarı Kurulum Yardımcısı
Bu script .env dosyasını düzenlemenize yardımcı olur.
"""

import os
import sys

def setup_env():
    """
    .env dosyasını API anahtarlarıyla güncelle
    """
    print("🔐 Nautilus Trader - API Anahtarı Kurulumu")
    print("=" * 50)
    print("⚠️  Bu sadece TESTNET anahtarları için kullanılmalıdır!")
    print("💡 Binance Testnet: https://testnet.binance.vision/")
    print()
    
    # Mevcut .env dosyasını oku
    env_path = ".env"
    env_content = ""
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            env_content = f.read()
        print("📄 Mevcut .env dosyası bulundu")
    else:
        print("📄 Yeni .env dosyası oluşturulacak")
    
    print()
    print("🔑 Binance Testnet API anahtarlarınızı girin:")
    print("   (Boş bırakırsanız mevcut değerler korunur)")
    print()
    
    # API Key al
    api_key = input("🔸 API Key: ").strip()
    if not api_key:
        print("   → Mevcut API Key korundu")
    else:
        # Mevcut API key'i güncelle veya ekle
        if "BINANCE_TESTNET_API_KEY=" in env_content:
            # Mevcut değeri güncelle
            import re
            env_content = re.sub(
                r'BINANCE_TESTNET_API_KEY=.*', 
                f'BINANCE_TESTNET_API_KEY={api_key}',
                env_content
            )
        else:
            # Yeni satır ekle
            env_content += f"\nBINANCE_TESTNET_API_KEY={api_key}\n"
    
    # API Secret al
    api_secret = input("🔸 API Secret: ").strip()
    if not api_secret:
        print("   → Mevcut API Secret korundu")
    else:
        # Mevcut API secret'i güncelle veya ekle
        if "BINANCE_TESTNET_API_SECRET=" in env_content:
            # Mevcut değeri güncelle
            import re
            env_content = re.sub(
                r'BINANCE_TESTNET_API_SECRET=.*', 
                f'BINANCE_TESTNET_API_SECRET={api_secret}',
                env_content
            )
        else:
            # Yeni satır ekle
            env_content += f"BINANCE_TESTNET_API_SECRET={api_secret}\n"
    
    # .env dosyasını kaydet
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print()
        print("✅ .env dosyası güncellendi!")
        print("🔐 API anahtarları güvenli şekilde saklandı")
        print()
        print("📋 Sonraki adımlar:")
        print("1. Test et:       python test_setup.py")
        print("2. Çalıştır:      python sandbox_trader.py")
        print("3. Docker ile:    docker-compose up --build")
        print()
        print("⚠️  UYARI: .env dosyasını asla git'e commit etmeyin!")
        
    except Exception as e:
        print(f"❌ .env dosyası kaydedilemedi: {e}")
        return False
    
    return True

def show_current_config():
    """Mevcut .env konfigürasyonunu göster"""
    print("📋 Mevcut .env Konfigürasyonu")
    print("-" * 30)
    
    if not os.path.exists(".env"):
        print("❌ .env dosyası bulunamadı")
        return
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        
        if api_key:
            print(f"✅ API Key: {api_key[:8]}...{api_key[-4:]}")
        else:
            print("❌ API Key tanımlı değil")
            
        if api_secret:
            print(f"✅ API Secret: {api_secret[:8]}...{api_secret[-4:]}")
        else:
            print("❌ API Secret tanımlı değil")
    
    except ImportError:
        print("⚠️  python-dotenv paketi yüklü değil")
        print("📦 Yüklemek için: pip install python-dotenv")
    except Exception as e:
        print(f"❌ Hata: {e}")

def main():
    """Ana fonksiyon"""
    if len(sys.argv) > 1 and sys.argv[1] == "show":
        show_current_config()
        return
    
    # .env kurulumu
    if setup_env():
        # Kurulum başarılı, test öner
        print("🧪 Kurulumu test etmek istiyor musunuz? (y/N): ", end="")
        response = input().strip().lower()
        
        if response in ['y', 'yes', 'evet', 'e']:
            print("\n🧪 Test çalıştırılıyor...")
            os.system("python test_setup.py")

if __name__ == "__main__":
    main()
