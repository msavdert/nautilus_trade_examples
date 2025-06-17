"""
Basit Binance Spot Testnet Bot Stratejisi
Bu strateji öğrenme amaçlı basit al-sat işlemleri yapar.
"""

from nautilus_trader.config import StrategyConfig
from nautilus_trader.core.data import Data
from nautilus_trader.indicators.average.sma import SimpleMovingAverage
from nautilus_trader.model.data import Bar
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.trading.strategy import Strategy


class SimpleTradingBotConfig(StrategyConfig, frozen=True):
    """
    Strateji konfigürasyonu
    """
    instrument_id: str  # Örn: "BTCUSDT.BINANCE"
    fast_sma_period: int = 10
    slow_sma_period: int = 20
    trade_size: str = "0.001"  # BTC miktarı


class SimpleTradingBot(Strategy):
    """
    Basit SMA Crossover Stratejisi
    
    Logic:
    - Fast SMA > Slow SMA: BUY signal
    - Fast SMA < Slow SMA: SELL signal
    """

    def __init__(self, config: SimpleTradingBotConfig) -> None:
        super().__init__(config)
        
        # Configuration
        self.instrument_id = InstrumentId.from_str(config.instrument_id)
        self.trade_size = config.trade_size
        
        # Indicators
        self.fast_sma = SimpleMovingAverage(config.fast_sma_period)
        self.slow_sma = SimpleMovingAverage(config.slow_sma_period)
        
        # State
        self.position_side = None  # "long", "short", None

    def on_start(self) -> None:
        """
        Strateji başlatıldığında çalışır
        """
        self.log.info(f"Starting SimpleTradingBot for {self.instrument_id}")
        
        # Bar data subscription
        bar_type = BarType.from_str(f"{self.instrument_id}-1-MINUTE-LAST-EXTERNAL")
        self.subscribe_bars(bar_type)

    def on_bar(self, bar: Bar) -> None:
        """
        Yeni bar geldiğinde çalışır
        """
        # Update indicators
        self.fast_sma.update_raw(bar.close.as_double())
        self.slow_sma.update_raw(bar.close.as_double())
        
        # Wait for indicators to be ready
        if not (self.fast_sma.initialized and self.slow_sma.initialized):
            return
            
        # Get indicator values
        fast_value = self.fast_sma.value
        slow_value = self.slow_sma.value
        
        self.log.info(
            f"Bar: {bar.close} | Fast SMA: {fast_value:.2f} | Slow SMA: {slow_value:.2f}"
        )
        
        # Generate signals
        if fast_value > slow_value and self.position_side != "long":
            self._place_buy_order()
        elif fast_value < slow_value and self.position_side != "short":
            self._place_sell_order()

    def _place_buy_order(self) -> None:
        """
        Alış emri ver
        """
        if self.portfolio.is_flat(self.instrument_id):
            self.log.info("🟢 BUY Signal - Placing market buy order")
            
            order = self.order_factory.market(
                instrument_id=self.instrument_id,
                order_side=OrderSide.BUY,
                quantity=self.instrument.make_qty(self.trade_size),
            )
            
            self.submit_order(order)
            self.position_side = "long"

    def _place_sell_order(self) -> None:
        """
        Satış emri ver
        """
        position = self.cache.position(self.instrument_id)
        if position and position.quantity > 0:
            self.log.info("🔴 SELL Signal - Placing market sell order")
            
            order = self.order_factory.market(
                instrument_id=self.instrument_id,
                order_side=OrderSide.SELL,
                quantity=position.quantity,
            )
            
            self.submit_order(order)
            self.position_side = "short"

    def on_stop(self) -> None:
        """
        Strateji durdurulduğunda çalışır
        """
        self.log.info("Stopping SimpleTradingBot")
        
        # Close any open positions
        position = self.cache.position(self.instrument_id)
        if position and not position.is_flat:
            self.close_position(position)
