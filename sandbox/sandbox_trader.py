#!/usr/bin/env python3
"""
Nautilus Trader - Sandbox Mode Live Trading Simulation
Bu script Binance testnet üzerinde EMA Cross stratejisiyle sandbox trading yapar.

⚠️ UYARI: Bu sadece testnet/sandbox modudur - gerçek para kullanılmaz!
"""

import asyncio
import os
import sys
import signal
from decimal import Decimal
from dotenv import load_dotenv

# Nautilus Trader imports
from nautilus_trader.config import TradingNodeConfig, LoggingConfig, LiveRiskEngineConfig
from nautilus_trader.adapters.binance.common.enums import BinanceAccountType
from nautilus_trader.adapters.binance.config import BinanceDataClientConfig, BinanceExecClientConfig
from nautilus_trader.live.node import TradingNode
from nautilus_trader.model.identifiers import TraderId, StrategyId

# Strategy imports
from nautilus_trader.examples.strategies.ema_cross import EMACross, EMACrossConfig


class SandboxTrader:
    """Nautilus Trader Sandbox Implementation"""
    
    def __init__(self):
        # .env dosyasını yükle
        load_dotenv()
        
        self.node = None
        self.running = False
        
        # API anahtarlarını kontrol et
        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "❌ API anahtarları bulunamadı!\n"
                "🔧 .env dosyasında BINANCE_TESTNET_API_KEY ve BINANCE_TESTNET_API_SECRET "
                "değerlerini ayarlayın."
            )
    
    def create_config(self) -> TradingNodeConfig:
        """Trading node konfigürasyonu oluştur"""
        
        # Binance adapter konfigürasyonu
        data_config = BinanceDataClientConfig(
            api_key=self.api_key,
            api_secret=self.api_secret,
            account_type=BinanceAccountType.SPOT,  # SPOT hesap türü
            testnet=True,  # Testnet modunu etkinleştir
            base_url_http="https://testnet.binance.vision",
            base_url_ws="wss://testnet.binance.vision",
        )
        
        exec_config = BinanceExecClientConfig(
            api_key=self.api_key,
            api_secret=self.api_secret,
            account_type=BinanceAccountType.SPOT,
            testnet=True,
            base_url_http="https://testnet.binance.vision",
            base_url_ws="wss://testnet.binance.vision",
        )
        
        # Trading node konfigürasyonu
        config = TradingNodeConfig(
            trader_id=TraderId("SANDBOX-TRADER-001"),
            
            # Logging
            logging=LoggingConfig(
                log_level="INFO",
                log_colors=True,
            ),
            
            # Data clients
            data_clients={
                "BINANCE": data_config,
            },
            
            # Execution clients  
            exec_clients={
                "BINANCE": exec_config,
            },
            
            # Risk Engine
            risk_engine=LiveRiskEngineConfig(
                bypass=False,  # Risk kontrollerini etkinleştir
                max_order_submit_rate="10/00:00:01",  # Saniyede max 10 emir
                max_order_modify_rate="10/00:00:01",
                
                # Position limits (Currency formatında)
                max_notional_per_order={
                    "USDT": Decimal("500"),   # Emir başına max 500 USDT
                    "BTC": Decimal("0.05"),   # Emir başına max 0.05 BTC
                },
                
                max_notionals={
                    "USDT": Decimal("5000"),  # Toplam pozisyon max 5000 USDT
                    "BTC": Decimal("0.5"),    # Toplam BTC pozisyonu max 0.5
                },
            ),
        )
        
        return config
    
    def create_strategy(self) -> EMACross:
        """EMA Cross stratejisi oluştur"""
        
        # Strateji konfigürasyonu
        strategy_config = EMACrossConfig(
            instrument_id="BTCUSDT.BINANCE",  # ✅ Doğru format: symbol.venue
            bar_type="BTCUSDT.BINANCE-1-MINUTE-LAST-INTERNAL",
            fast_ema_period=10,
            slow_ema_period=20,
            trade_size=Decimal("0.001"),  # 0.001 BTC (küçük test miktarı)
        )
        
        # Strateji oluştur
        strategy = EMACross(config=strategy_config)
        
        return strategy
    
    async def run(self):
        """Ana trading loop"""
        try:
            print("🚀 Nautilus Trader Sandbox başlatılıyor...")
            print("📡 Binance Testnet'e bağlanılıyor...")
            
            # Konfigürasyon oluştur
            config = self.create_config()
            
            # Trading node oluştur
            self.node = TradingNode(config=config)
            
            # Strateji ekle
            strategy = self.create_strategy()
            self.node.trader.add_strategy(strategy)
            
            # Signal handler'ları ayarla
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            # Node'u başlat
            await self.node.start_async()
            self.running = True
            
            print("✅ Sandbox Trader başlatıldı!")
            print("📊 Market verileri alınıyor...")
            print("🤖 EMA Cross stratejisi aktif...")
            print("📈 Trading pair: BTCUSDT.BINANCE")
            print("💰 Trade size: 0.001 BTC")
            print("⏹️  Durdurmak için Ctrl+C basın\n")
            
            # Ana döngü
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Kullanıcı tarafından durduruldu")
        except Exception as e:
            print(f"❌ Hata: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Trading node'u durdur"""
        if self.node:
            print("🔄 Trading node kapatılıyor...")
            await self.node.stop_async()
            print("✅ Trading node kapatıldı")
        self.running = False
    
    def _signal_handler(self, signum, frame):
        """Signal handler (Ctrl+C vs)"""
        print(f"\n📶 Signal alındı: {signum}")
        self.running = False


async def main():
    """Ana fonksiyon"""
    # Log dizini oluştur
    os.makedirs("./logs", exist_ok=True)
    
    print("🌊 Nautilus Trader - Sandbox Mode")
    print("=" * 50)
    print("⚠️  TESTNET MODU - Gerçek para kullanılmaz!")
    print("🔐 API anahtarları kontrol ediliyor...")
    
    # Trader'ı başlat
    trader = SandboxTrader()
    await trader.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Güle güle!")
    except Exception as e:
        print(f"💥 Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
