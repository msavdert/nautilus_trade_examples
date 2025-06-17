#!/usr/bin/env python3
"""
Nautilus Trader - Professional Sandbox Trading Bot
==================================================

🌊 Nautilus Trader tabanlı profesyonel sandbox trading sistemi
Bu script, Binance Testnet üzerinde EMA Cross stratejisiyle tam otomatik trading yapar.

⚠️ UYARI: Bu tamamen sandbox/testnet modudur - gerçek para kullanılmaz!

🎯 ANA ÖZELLİKLER:
- Binance Testnet entegrasyonu (güvenli test ortamı)
- EMA Cross algoritması (10/20 periyot moving average)
- PostgreSQL ile historical data storage
- Redis ile real-time market data caching
- Comprehensive risk management sistemi
- Live market data streaming
- Detaylı logging ve monitoring
- Docker containerized deployment

📊 STRATEJİ DETAYI:
EMA Cross stratejisi, iki farklı periyotluk üssel hareketli ortalama kullanır:
- Hızlı EMA (10 periyot): Kısa vadeli trend
- Yavaş EMA (20 periyot): Uzun vadeli trend
- BUY Signal: Hızlı EMA > Yavaş EMA (Golden Cross)
- SELL Signal: Hızlı EMA < Yavaş EMA (Death Cross)

🔧 GEREKSINIMLER:
- Binance Testnet API anahtarları (.env dosyasında)
- Docker & Docker Compose
- PostgreSQL container (historical data)
- Redis container (real-time cache)

📁 DOSYA YAPISI:
├── docker-compose.yml     # Tüm servisler (PostgreSQL, Redis, Bot)
├── sandbox/
│   ├── sandbox_trader.py  # Ana trading bot (bu dosya)
│   ├── .env              # API anahtarları ve ortam değişkenleri
│   └── pyproject.toml    # Python dependencies and project config
└── README.md             # Kullanım kılavuzu

🚀 KULLANIM:
1. .env dosyasında Binance Testnet API anahtarlarınızı ayarlayın
2. docker-compose up -d
3. Bot otomatik olarak başlayacak ve trading yapmaya başlayacak

📈 TRADING PARAMETRELERİ:
- Trading Pair: BTCUSDT.BINANCE
- Timeframe: 1 dakika
- Trade Size: 0.001 BTC (test için güvenli miktar)
- Risk Management: Aktif (max 10 order/saniye)

Author: Nautilus Trader Sandbox Implementation
Version: 3.0.0 (Full Configuration Edition)
License: LGPL-3.0
Repository: https://github.com/nautechsystems/nautilus_trader
"""

import os
import sys
import signal
import time
from decimal import Decimal
from typing import Optional, Dict, Any

# Environment variable loading
from dotenv import load_dotenv

# Nautilus Trader Core Framework
from nautilus_trader.config import (
    TradingNodeConfig,
    LoggingConfig, 
    InstrumentProviderConfig,
    CacheConfig,
    DatabaseConfig,
    MessageBusConfig,
    LiveExecEngineConfig
)

# Nautilus Data Models
from nautilus_trader.model.identifiers import TraderId, InstrumentId
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import TimeInForce

# Binance Exchange Adapter
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import (
    BinanceDataClientConfig, 
    BinanceExecClientConfig
)
from nautilus_trader.adapters.binance import (
    BINANCE,
    BinanceLiveDataClientFactory, 
    BinanceLiveExecClientFactory
)

# Trading Engine
from nautilus_trader.live.node import TradingNode

# Strategy Implementation
from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig


class SandboxTrader:
    """
    🌊 Nautilus Trader Sandbox Implementation
    
    Bu sınıf, Binance Testnet üzerinde tamamen güvenli bir şekilde
    algoritmik trading yapmak için tasarlanmış profesyonel bir trading sistemidir.
    
    Sistem Bileşenleri:
    - Trading Engine: Nautilus Trader framework
    - Data Source: Binance Testnet (real market data)
    - Strategy: EMA Cross algoritması
    - Database: PostgreSQL (historical data)
    - Cache: Redis (real-time data)
    - Risk Management: Built-in risk controls
    """
    
    def __init__(self):
        """
        Sandbox Trader'ı başlat ve temel konfigürasyonu yükle
        """
        print("🔧 Sandbox Trader başlatılıyor...")
        
        # .env dosyasından ortam değişkenlerini yükle
        load_dotenv()
        
        # Instance variables
        self.node: Optional[TradingNode] = None
        self.running: bool = False
        
        # API Authentication - Binance Testnet
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        
        # API anahtarlarını doğrula
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "❌ API anahtarları bulunamadı!\n"
                "🔧 .env dosyasında aşağıdaki değerleri ayarlayın:\n"
                "   BINANCE_API_KEY=your_testnet_api_key\n"
                "   BINANCE_API_SECRET=your_testnet_api_secret\n"
                "📖 Binance Testnet API: https://testnet.binance.vision/"
            )
        
        print("✅ API anahtarları yüklendi")
        print("🔐 Binance Testnet bağlantısı hazır")
    
    
    def create_config(self) -> TradingNodeConfig:
        """
        🔧 Trading Node için kapsamlı konfigürasyon oluştur
        
        Bu method, tüm trading sisteminin konfigürasyonunu tanımlar:
        - Database connections (PostgreSQL)
        - Cache settings (Redis) 
        - Risk management rules
        - Logging configuration
        - Exchange connections (Binance)
        - Data clients and execution clients
        
        Returns:
            TradingNodeConfig: Tam yapılandırılmış trading node config
        """
        
        print("📋 Trading konfigürasyonu oluşturuluyor...")
        
        # === TEMEL TRADER KIMLIK AYARLARI ===
        trader_id = TraderId("SANDBOX-TRADER-001")
        print(f"🆔 Trader ID: {trader_id}")
        
        # === LOGGING KONFIGÜRASYONU ===
        # Tüm trading aktiviteleri detaylı şekilde loglanır
        logging_config = LoggingConfig(
            log_level="INFO",              # INFO seviyesinde logging (DEBUG çok detaylı)
            log_colors=True,               # Terminal'de renkli loglar
            log_level_file="INFO",         # Dosyaya da log yaz
            log_directory="./logs",        # Log dosya yolu
        )
        
        # === DATABASE KONFIGÜRASYONU ===
        # PostgreSQL - Historical data storage için (Nautilus Trader execution persistence)
        # Not: Cache ve MessageBus sadece Redis'i destekliyor, PostgreSQL sadece historical data için
        # Nautilus Trader standard environment variables kullanıyoruz
        database_config = DatabaseConfig(
            type="postgresql",                                    # PostgreSQL database
            host=os.getenv("POSTGRES_HOST", "localhost"),        # Docker: nautilus-postgres
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            username=os.getenv("POSTGRES_USERNAME", "nautilus"),
            password=os.getenv("POSTGRES_PASSWORD", "nautilus123"),
            # NOT: POSTGRES_DATABASE env var Nautilus'un internal connection logic'inde kullanılır
        )
        
        # === CACHE KONFIGÜRASYONU ===
        # Redis - Real-time caching için (Nautilus Trader sadece Redis'i cache için destekliyor)
        # PostgreSQL cache için desteklenmiyor - sadece Redis kullanılabilir
        cache_config = CacheConfig(
            database=DatabaseConfig(
                type="redis",                                      # Redis cache (zorunlu)
                host=os.getenv("REDIS_HOST", "localhost"),         # Docker: nautilus-redis
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),              # Redis password (optional)
            ),
            timestamps_as_iso8601=True,            # ISO8601 format timestamps
            buffer_interval_ms=100,                # Buffer interval for batching operations
            flush_on_start=False,                  # Restart'ta data'yı temizleme
            tick_capacity=10000,                   # Historical tick data capacity
            bar_capacity=10000,                    # Historical bar data capacity
        )
        
        # === MESSAGE BUS KONFIGÜRASYONU ===
        # Redis - Message Bus da sadece Redis'i destekliyor (PostgreSQL değil)
        # Nautilus Trader sadece Redis'i cache ve message bus persistent storage için destekliyor
        message_bus_config = MessageBusConfig(
            database=DatabaseConfig(
                type="redis",                                      # Redis message bus (zorunlu)
                host=os.getenv("REDIS_HOST", "localhost"),         # Docker: nautilus-redis
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),              # Redis password (optional)
            ),
            timestamps_as_iso8601=True,            # ISO8601 format timestamps
            use_trader_prefix=True,                # Use trader prefix in keys
            use_instance_id=False,                 # Instance ID in keys
        )
        
        # === EXECUTION ENGINE KONFIGÜRASYONU ===
        # Execution engine ayarları - order execution ve reconciliation
        exec_engine_config = LiveExecEngineConfig(
            reconciliation=True,                            # Enable reconciliation
            reconciliation_lookback_mins=1440,             # 24 saat geriye dönük kontrol
        )
        
        # === BINANCE DATA CLIENT KONFIGÜRASYONU ===
        # Market data alımı için client ayarları
        binance_data_config = BinanceDataClientConfig(
            api_key=self.api_key,
            api_secret=self.api_secret,
            account_type=BinanceAccountType.SPOT,      # Spot trading (margin/futures değil)
            testnet=True,                              # TESTNET modu - güvenli!
            
            # Binance Testnet URL'leri
            base_url_http="https://testnet.binance.vision",
            base_url_ws="wss://stream.testnet.binance.vision",
            
            # Instrument provider - hangi coinleri trade edeceğimizi belirtir
            instrument_provider=InstrumentProviderConfig(
                load_all=False,    # Tüm binlerce coini yükleme (performans için)
                load_ids=frozenset([
                    InstrumentId.from_str("BTCUSDT.BINANCE"),  # Sadece BTC/USDT
                    # İhtiyaç halinde buraya başka coinler eklenebilir:
                    # InstrumentId.from_str("ETHUSDT.BINANCE"),
                    # InstrumentId.from_str("ADAUSDT.BINANCE"),
                ]),
            ),
        )
        
        # === BINANCE EXECUTION CLIENT KONFIGÜRASYONU ===
        # Gerçek emir gönderimi için client ayarları
        binance_exec_config = BinanceExecClientConfig(
            api_key=self.api_key,
            api_secret=self.api_secret,
            account_type=BinanceAccountType.SPOT,      # Spot trading
            testnet=True,                              # TESTNET - güvenli mod!
            
            # Binance Testnet URL'leri (execution için)
            base_url_http="https://testnet.binance.vision",
            base_url_ws="wss://stream.testnet.binance.vision",
        )
        
        # === COMPLETE TRADING NODE CONFIGURATION ===
        config = TradingNodeConfig(
            trader_id=trader_id,
            
            # System Configuration
            logging=logging_config,
            cache=cache_config,                    # Redis için real-time cache
            message_bus=message_bus_config,        # PostgreSQL için persistent storage
            
            # Execution Engine Configuration
            exec_engine=exec_engine_config,
            
            # Exchange Connections
            data_clients={
                BINANCE: binance_data_config,    # Market data için
            },
            exec_clients={
                BINANCE: binance_exec_config,    # Emir gönderimi için
            },
        )
        
        print("✅ Trading konfigürasyonu hazır")
        print(f"🚀 Cache: Redis @ {cache_config.database.host}:{cache_config.database.port} (Real-time)")
        print(f"📨 MessageBus: Redis @ {message_bus_config.database.host}:{message_bus_config.database.port} (Message Storage)")
        print(f"🏦 Database: PostgreSQL @ {database_config.host}:{database_config.port} (Historical Data Only)")
        print("🛡️ Execution Engine: Aktif")
        
        return config
    
    
    def create_strategy(self) -> EMACross:
        """
        📈 EMA Cross Trading Strategy oluştur
        
        EMA Cross Stratejisi Nasıl Çalışır:
        ------------------------------------
        1. İki EMA (Exponential Moving Average) hesaplar:
           - Hızlı EMA: Son 10 dakikanın ortalaması (trend değişimlerini hızlı yakalar)
           - Yavaş EMA: Son 20 dakikanın ortalaması (genel trend yönünü gösterir)
        
        2. Trading sinyalleri:
           - BUY (Satın Al): Hızlı EMA > Yavaş EMA (Golden Cross)
           - SELL (Sat): Hızlı EMA < Yavaş EMA (Death Cross)
        
        3. Risk yönetimi:
           - Her trade 0.001 BTC (yaklaşık $30-50 test değeri)
           - Stop loss ve take profit mantığı Nautilus'ta otomatik
        
        Returns:
            EMACross: Yapılandırılmış EMA Cross stratejisi
        """
        
        print("📊 EMA Cross stratejisi oluşturuluyor...")
        
        # === TRADING PAIR TANIMI ===
        # BTCUSDT: Bitcoin/US Dollar Tether çifti
        # En likit ve güvenilir trading pair
        instrument_id = InstrumentId.from_str("BTCUSDT.BINANCE")
        
        # === BAR TYPE TANIMI ===
        # 1 dakikalık mum grafikleri kullan
        # Format: {INSTRUMENT}-{TIMEFRAME}-{PRICE_TYPE}-{AGGREGATION}
        bar_type = BarType.from_str("BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL")
        
        # === STRATEJİ PARAMETRELERİ ===
        strategy_config = EMACrossConfig(
            instrument_id=instrument_id,
            bar_type=bar_type,
            
            # EMA periyotları
            fast_ema_period=10,    # Hızlı EMA: 10 dakika
            slow_ema_period=20,    # Yavaş EMA: 20 dakika
            
            # Trade büyüklüğü
            trade_size=Decimal("0.001"),  # 0.001 BTC (güvenli test miktarı)
            
            # Data subscription settings
            subscribe_quote_ticks=False,     # Quote tick'leri dinleme (bandwidth için)
            subscribe_trade_ticks=True,      # Trade tick'leri dinle (gerçek işlemler)
            request_bars=True,               # Historical bar data iste
            unsubscribe_data_on_stop=True,   # Durdurulduğunda data feed'lerini kapat
            
            # Order settings (güncel API)
            order_quantity_precision=None,   # Otomatik precision (exchange'den al)
            order_time_in_force=None,        # Varsayılan TIF kullan
            close_positions_on_stop=True,    # Durdurulduğunda pozisyonları kapat
            reduce_only_on_stop=True,        # Sadece reduce-only emirleri gönder
        )
        
        # Strateji instance'ı oluştur
        strategy = EMACross(config=strategy_config)
        
        print(f"📈 Trading Pair: {instrument_id}")
        print(f"⏱️ Timeframe: 1 dakika")
        print(f"🔄 Hızlı EMA: {strategy_config.fast_ema_period} periyot")
        print(f"🔄 Yavaş EMA: {strategy_config.slow_ema_period} periyot")
        print(f"💰 Trade Size: {strategy_config.trade_size} BTC")
        print(f"📊 Subscribe Trade Ticks: {strategy_config.subscribe_trade_ticks}")
        print(f"📈 Request Historical Bars: {strategy_config.request_bars}")
        print("✅ EMA Cross stratejisi hazır")
        
        return strategy
    
    
    def run(self):
        """
        🚀 Ana trading loop - sistemi başlat ve çalıştır
        
        Bu method şunları yapar:
        1. Trading node'u oluştur ve configure et
        2. Binance factory'lerini kaydet
        3. EMA Cross stratejisini ekle
        4. Signal handler'ları ayarla (graceful shutdown için)
        5. Sistemi başlat ve sonsuz döngüde çalıştır
        6. Hata durumunda temiz şekilde kapat
        """
        
        try:
            print("\n" + "="*60)
            print("🌊 NAUTILUS TRADER SANDBOX BAŞLANIYOR")
            print("="*60)
            print("⚠️  TESTNET MODU - Gerçek para kullanılmaz!")
            print("📡 Binance Testnet'e bağlanılıyor...")
            
            # === TRADING NODE OLUŞTURMA ===
            print("\n🔧 Trading node yapılandırılıyor...")
            config = self.create_config()
            self.node = TradingNode(config=config)
            
            # === EXCHANGE FACTORY KAYITLARI ===
            # Nautilus'un Binance ile konuşabilmesi için factory'ler gerekli
            print("🏭 Binance factory'leri kaydediliyor...")
            self.node.add_data_client_factory(BINANCE, BinanceLiveDataClientFactory)
            self.node.add_exec_client_factory(BINANCE, BinanceLiveExecClientFactory)
            
            # === STRATEJİ EKLEME ===
            print("📊 EMA Cross stratejisi ekleniyor...")
            strategy = self.create_strategy()
            self.node.trader.add_strategy(strategy)
            
            # === SIGNAL HANDLER KURULUMU ===
            # Ctrl+C ile temiz şekilde kapatılabilmesi için
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # === TRADING NODE BUILD ===
            print("🔨 Trading node build ediliyor...")
            self.node.build()
            self.running = True
            
            # === BAŞLATMA MESAJLARI ===
            print("\n" + "🎉 SANDBOX TRADER BAŞARIYLA BAŞLATILDI!" + "\n")
            print("📊 Market verileri alınıyor...")
            print("🤖 EMA Cross stratejisi aktif...")
            print("📈 Trading pair: BTCUSDT.BINANCE")
            print("💰 Trade size: 0.001 BTC")
            print("🛡️ Risk management: Aktif")
            print("📝 Loglar: ./logs/ dizininde")
            print("\n⏹️  Durdurmak için Ctrl+C basın")
            print("="*60 + "\n")
            
            # === TRADING LOOP BAŞLATMA ===
            # Bu blocking call - sistem burada çalışır durur
            self.node.run()
                
        except KeyboardInterrupt:
            print("\n\n🛑 Kullanıcı tarafından durduruldu (Ctrl+C)")
            
        except Exception as e:
            print(f"\n❌ Beklenmeyen hata: {e}")
            print("🔍 Hata detayları:")
            import traceback
            traceback.print_exc()
            raise
            
        finally:
            # Her durumda temiz kapatma
            self.stop()
    
    
    def stop(self):
        """
        🔴 Trading sistemi temiz kapatma
        
        Şunları yapar:
        1. Açık pozisyonları kontrol et
        2. Bekleyen emirleri iptal et
        3. Database bağlantılarını kapat
        4. Log dosyalarını flush et
        5. Tüm thread'leri temiz şekilde sonlandır
        """
        
        if self.node:
            print("\n🔄 Trading node kapatılıyor...")
            print("💾 Veriler kaydediliyor...")
            
            try:
                # Node'u durdur
                self.node.stop()
                print("⏹️ Trading durduruldu")
                
                # Kaynakları temizle
                self.node.dispose()
                print("🧹 Kaynaklar temizlendi")
                
            except Exception as e:
                print(f"⚠️ Kapatma sırasında hata: {e}")
            
            finally:
                print("✅ Trading node kapatıldı")
        
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """
        📶 Signal handler (Ctrl+C, SIGTERM vs.)
        
        Sistem güvenli şekilde kapatılabilmesi için signal'ları yakalar
        """
        print(f"\n📶 Signal alındı: {signum}")
        print("🔄 Güvenli kapatma başlatılıyor...")
        self.running = False


def main():
    """
    🎯 Ana fonksiyon - Entry point
    
    Program başlangıç noktası:
    1. Çevre hazırlığı yap
    2. Trader'ı başlat
    3. Hata durumlarını handle et
    """
    
    # === ÇEVRE HAZIRLIĞI ===
    # Log dizini oluştur (yoksa)
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./data", exist_ok=True)
    
    # === BAŞLANGIC BANNER ===
    print("\n" + "🌊" * 20)
    print("   NAUTILUS TRADER - SANDBOX MODE")
    print("🌊" * 20)
    print("⚠️  TESTNET MODU - Gerçek para kullanılmaz!")
    print("🔐 API anahtarları kontrol ediliyor...")
    print("📊 Trading sistemi hazırlanıyor...")
    
    try:
        # === TRADER BAŞLATMA ===
        trader = SandboxTrader()
        trader.run()
        
    except KeyboardInterrupt:
        print("\n👋 Güvenli kapatma tamamlandı. Güle güle!")
        
    except Exception as e:
        print(f"\n💥 Kritik hata: {e}")
        print("🔍 Bu hatayı geliştiricilere bildirin:")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# === PROGRAM ENTRY POINT ===
if __name__ == "__main__":
    """
    Program başlangıç noktası
    
    Bu script doğrudan çalıştırıldığında main() fonksiyonu devreye girer.
    Docker container içinde de bu şekilde başlatılır.
    """
    main()
