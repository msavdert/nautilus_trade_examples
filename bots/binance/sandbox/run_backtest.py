#!/usr/bin/env python3
"""
Backtest Runner for Volatility Breakout Strategy
Comprehensive backtesting with performance analysis and visualization.
"""

import asyncio
import logging
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd
import numpy as np

from nautilus_trader.adapters.binance import BinanceDataClientConfig, BinanceAccountType
from nautilus_trader.backtest.engine import BacktestEngine, BacktestEngineConfig
from nautilus_trader.backtest.models import FillModel
from nautilus_trader.config import LoggingConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import BarType
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue, InstrumentId, TraderId
from nautilus_trader.model.objects import Money
from nautilus_trader.persistence.wranglers import BarDataWrangler
from nautilus_trader.test_kit.providers import TestInstrumentProvider

from config import get_config
from strategy import VolatilityBreakoutStrategy, VolatilityBreakoutConfig
from coin_selector import CoinSelector
from utils import LoggingUtils, MathUtils


class BacktestRunner:
    """
    Comprehensive backtesting system for the Volatility Breakout strategy.
    
    Features:
    - Historical data fetching from Binance
    - Multi-symbol backtesting
    - Performance metrics calculation
    - Trade analysis and reporting
    - Results visualization
    """
    
    def __init__(self):
        """Initialize backtest runner."""
        self.config = get_config()
        self.logger = LoggingUtils.setup_logger("BacktestRunner", "INFO")
        
        # Backtest parameters
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2024, 12, 31)
        self.initial_balance = 10000.0
        
        # Selected instruments for backtesting
        self.test_symbols = ["BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"]
        self.instrument_ids: List[InstrumentId] = []
        
        # Results storage
        self.results: Dict[str, Any] = {}
        self.trades: List[Dict] = []
        
    async def setup_instruments(self) -> None:
        """Setup instruments for backtesting."""
        self.logger.info("Setting up test instruments...")
        
        # Create instrument IDs
        venue_suffix = ".BINANCE"
        if self.config.exchange.account_type == "USDT_FUTURE":
            self.instrument_ids = [
                InstrumentId.from_str(f"{symbol}-PERP{venue_suffix}")
                for symbol in self.test_symbols
            ]
        else:
            self.instrument_ids = [
                InstrumentId.from_str(f"{symbol}{venue_suffix}")
                for symbol in self.test_symbols
            ]
        
        self.logger.info(f"Setup {len(self.instrument_ids)} instruments for backtesting")
    
    def create_backtest_engine(self) -> BacktestEngine:
        """
        Create and configure backtest engine.
        
        Returns:
            Configured backtest engine
        """
        # Engine configuration
        config = BacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),
            logging=LoggingConfig(log_level="INFO"),
            
            # Use simple fill model for backtesting
            # In production, consider using more sophisticated models
            # that account for slippage, market impact, etc.
        )
        
        # Create engine
        engine = BacktestEngine(config=config)
        
        # Add venue
        venue = Venue("BINANCE")
        engine.add_venue(
            venue=venue,
            oms_type=OmsType.HEDGING,  # Allows multiple positions per instrument
            account_type=AccountType.MARGIN,  # Margin account for leverage
            base_currency=USD,
            starting_balances=[Money(self.initial_balance, USD)]
        )
        
        return engine
    
    def create_test_data(self) -> Dict[InstrumentId, pd.DataFrame]:
        """
        Create synthetic test data for backtesting.
        
        In a production environment, this would fetch real historical data
        from Binance API or a data provider.
        
        Returns:
            Dictionary of test data per instrument
        """
        self.logger.info("Creating synthetic test data...")
        
        test_data = {}
        
        for instrument_id in self.instrument_ids:
            # Generate synthetic OHLCV data
            dates = pd.date_range(
                start=self.start_date,
                end=self.end_date,
                freq='1T'  # 1-minute bars
            )
            
            np.random.seed(42)  # For reproducible results
            
            # Generate price data with trend and volatility
            base_price = 100.0
            price_trend = np.cumsum(np.random.normal(0, 0.001, len(dates)))
            volatility = np.random.normal(0, 0.02, len(dates))
            
            prices = base_price * (1 + price_trend + volatility)
            prices = np.maximum(prices, 1.0)  # Ensure positive prices
            
            # Create OHLCV data
            opens = prices
            highs = prices * (1 + np.abs(np.random.normal(0, 0.01, len(dates))))
            lows = prices * (1 - np.abs(np.random.normal(0, 0.01, len(dates))))
            closes = prices + np.random.normal(0, 0.005, len(dates))
            volumes = np.random.lognormal(10, 1, len(dates))
            
            # Ensure OHLC consistency
            for i in range(len(dates)):
                high = max(opens[i], highs[i], lows[i], closes[i])
                low = min(opens[i], highs[i], lows[i], closes[i])
                highs[i] = high
                lows[i] = low
            
            # Create DataFrame
            df = pd.DataFrame({
                'timestamp': dates,
                'open': opens,
                'high': highs,
                'low': lows,
                'close': closes,
                'volume': volumes
            })
            
            test_data[instrument_id] = df
            
            self.logger.info(
                f"Generated {len(df)} bars for {instrument_id.symbol} "
                f"from {self.start_date} to {self.end_date}"
            )
        
        return test_data
    
    async def load_historical_data(self) -> Dict[InstrumentId, pd.DataFrame]:
        """
        Load real historical data from Binance API.
        
        This is a placeholder implementation. In production, you would:
        1. Use Binance historical data API
        2. Handle rate limiting
        3. Cache data locally
        4. Validate data quality
        
        Returns:
            Dictionary of historical data per instrument
        """
        self.logger.warning("Using synthetic data - implement real data loading for production")
        return self.create_test_data()
    
    def add_data_to_engine(self, engine: BacktestEngine, data: Dict[InstrumentId, pd.DataFrame]) -> None:
        """
        Add historical data to backtest engine.
        
        Args:
            engine: Backtest engine
            data: Historical data per instrument
        """
        self.logger.info("Adding data to backtest engine...")
        
        for instrument_id, df in data.items():
            # Create test instrument
            instrument = TestInstrumentProvider.default_fx_ccy(instrument_id.symbol)
            engine.add_instrument(instrument)
            
            # Create bar type
            bar_type = BarType.from_str(f"{instrument_id.symbol}.BINANCE-1-MINUTE-LAST-EXTERNAL")
            
            # Convert DataFrame to Nautilus bars
            wrangler = BarDataWrangler(bar_type, instrument)
            bars = wrangler.process(df)
            
            # Add bars to engine
            engine.add_data(bars)
            
            self.logger.info(f"Added {len(bars)} bars for {instrument_id.symbol}")
    
    def create_strategy(self) -> VolatilityBreakoutStrategy:
        """
        Create strategy instance for backtesting.
        
        Returns:
            Configured strategy
        """
        # Strategy configuration
        config = VolatilityBreakoutConfig(
            instrument_ids=self.instrument_ids,
            bar_type=BarType.from_str(f"{self.test_symbols[0]}.BINANCE-1-MINUTE-LAST-EXTERNAL"),
            
            # Technical indicator parameters
            atr_period=self.config.strategy.atr_period,
            bollinger_period=self.config.strategy.bollinger_period,
            bollinger_std=self.config.strategy.bollinger_std,
            rsi_period=self.config.strategy.rsi_period,
            volume_period=self.config.strategy.volume_period,
            
            # Entry conditions (more conservative for backtesting)
            volume_threshold_multiplier=2.0,  # Higher threshold
            rsi_min=25.0,  # Wider range
            rsi_max=75.0,
            volatility_threshold_atr=0.3,  # Lower threshold
            
            # Exit conditions
            stop_loss_atr_multiplier=self.config.strategy.stop_loss_atr_multiplier,
            take_profit_atr_multiplier=self.config.strategy.take_profit_atr_multiplier,
            trailing_stop_atr_multiplier=self.config.strategy.trailing_stop_atr_multiplier,
            
            # Risk management (conservative for backtesting)
            max_risk_per_trade=0.005,  # 0.5% risk per trade
            max_position_size=0.01     # 1% position size
        )
        
        return VolatilityBreakoutStrategy(config=config)
    
    async def run_backtest(self) -> BacktestEngine:
        """
        Run the backtest.
        
        Returns:
            Completed backtest engine with results
        """
        self.logger.info("Starting backtest execution...")
        
        # Setup instruments
        await self.setup_instruments()
        
        # Create backtest engine
        engine = self.create_backtest_engine()
        
        # Load historical data
        data = await self.load_historical_data()
        
        # Add data to engine
        self.add_data_to_engine(engine, data)
        
        # Create and add strategy
        strategy = self.create_strategy()
        engine.add_strategy(strategy)
        
        # Run backtest
        self.logger.info(f"Running backtest from {self.start_date} to {self.end_date}")
        engine.run()
        
        self.logger.info("Backtest completed")
        return engine
    
    def analyze_results(self, engine: BacktestEngine) -> Dict[str, Any]:
        """
        Analyze backtest results and calculate performance metrics.
        
        Args:
            engine: Completed backtest engine
            
        Returns:
            Dictionary of performance metrics
        """
        self.logger.info("Analyzing backtest results...")
        
        # Get portfolio statistics
        portfolio = engine.trader.portfolio
        
        # Basic metrics
        total_pnl = float(portfolio.net_position().as_double()) if portfolio.net_position() else 0.0
        total_trades = len(portfolio.closed_positions)
        
        # Calculate additional metrics
        if total_trades > 0:
            winning_trades = len([p for p in portfolio.closed_positions if p.realized_pnl.as_double() > 0])
            losing_trades = total_trades - winning_trades
            win_rate = (winning_trades / total_trades) * 100
            
            # PnL analysis
            trade_pnls = [float(p.realized_pnl.as_double()) for p in portfolio.closed_positions]
            avg_win = np.mean([pnl for pnl in trade_pnls if pnl > 0]) if winning_trades > 0 else 0
            avg_loss = np.mean([pnl for pnl in trade_pnls if pnl < 0]) if losing_trades > 0 else 0
            profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
            
            # Equity curve for drawdown calculation
            equity_curve = []
            running_pnl = self.initial_balance
            for position in portfolio.closed_positions:
                running_pnl += float(position.realized_pnl.as_double())
                equity_curve.append(running_pnl)
            
            max_drawdown = MathUtils.calculate_max_drawdown(equity_curve) if equity_curve else 0
            
            # Calculate Sharpe ratio (simplified)
            daily_returns = []
            if len(equity_curve) > 1:
                for i in range(1, len(equity_curve)):
                    daily_return = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
                    daily_returns.append(daily_return)
            
            sharpe_ratio = MathUtils.calculate_sharpe_ratio(daily_returns) if daily_returns else 0
            
        else:
            winning_trades = losing_trades = 0
            win_rate = avg_win = avg_loss = profit_factor = max_drawdown = sharpe_ratio = 0
            trade_pnls = []
        
        # Final balance
        final_balance = self.initial_balance + total_pnl
        return_pct = ((final_balance - self.initial_balance) / self.initial_balance) * 100
        
        results = {
            'initial_balance': self.initial_balance,
            'final_balance': final_balance,
            'total_pnl': total_pnl,
            'return_percentage': return_pct,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'average_win': avg_win,
            'average_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'test_period_days': (self.end_date - self.start_date).days,
            'instruments_tested': len(self.instrument_ids)
        }
        
        self.results = results
        return results
    
    def print_results(self, results: Dict[str, Any]) -> None:
        """
        Print formatted backtest results.
        
        Args:
            results: Performance metrics dictionary
        """
        print("\n" + "=" * 50)
        print("BACKTEST RESULTS")
        print("=" * 50)
        
        print(f"Test Period: {self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}")
        print(f"Instruments: {', '.join(self.test_symbols)}")
        print(f"Duration: {results['test_period_days']} days")
        print()
        
        print("PERFORMANCE SUMMARY:")
        print(f"  Initial Balance:     ${results['initial_balance']:,.2f}")
        print(f"  Final Balance:       ${results['final_balance']:,.2f}")
        print(f"  Total PnL:           ${results['total_pnl']:,.2f}")
        print(f"  Return:              {results['return_percentage']:+.2f}%")
        print(f"  Max Drawdown:        {results['max_drawdown']:.2f}%")
        print(f"  Sharpe Ratio:        {results['sharpe_ratio']:.3f}")
        print()
        
        print("TRADE STATISTICS:")
        print(f"  Total Trades:        {results['total_trades']}")
        print(f"  Winning Trades:      {results['winning_trades']}")
        print(f"  Losing Trades:       {results['losing_trades']}")
        print(f"  Win Rate:            {results['win_rate']:.1f}%")
        print(f"  Average Win:         ${results['average_win']:.2f}")
        print(f"  Average Loss:        ${results['average_loss']:.2f}")
        print(f"  Profit Factor:       {results['profit_factor']:.2f}")
        print()
        
        # Performance evaluation
        print("PERFORMANCE EVALUATION:")
        if results['return_percentage'] > 0:
            print("  ✓ Strategy was profitable")
        else:
            print("  ✗ Strategy was unprofitable")
        
        if results['win_rate'] > 50:
            print("  ✓ Win rate above 50%")
        else:
            print("  ✗ Win rate below 50%")
        
        if results['profit_factor'] > 1.0:
            print("  ✓ Profit factor > 1.0")
        else:
            print("  ✗ Profit factor < 1.0")
        
        if results['max_drawdown'] < 10:
            print("  ✓ Max drawdown < 10%")
        else:
            print("  ⚠ Max drawdown >= 10%")
        
        print("=" * 50)
    
    def save_results(self, filename: str = None) -> None:
        """
        Save backtest results to file.
        
        Args:
            filename: Output filename
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_results_{timestamp}.json"
        
        try:
            import json
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")


async def main():
    """Main entry point for backtest runner."""
    parser = argparse.ArgumentParser(description="Volatility Breakout Strategy Backtest")
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)", default="2024-01-01")
    parser.add_argument("--end-date", help="End date (YYYY-MM-DD)", default="2024-12-31")
    parser.add_argument("--initial-balance", type=float, help="Initial balance", default=10000.0)
    parser.add_argument("--save-results", action="store_true", help="Save results to file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create backtest runner
        runner = BacktestRunner()
        
        # Override dates if provided
        if args.start_date:
            runner.start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        if args.end_date:
            runner.end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
        if args.initial_balance:
            runner.initial_balance = args.initial_balance
        
        # Run backtest
        engine = await runner.run_backtest()
        
        # Analyze results
        results = runner.analyze_results(engine)
        
        # Print results
        runner.print_results(results)
        
        # Save results if requested
        if args.save_results:
            runner.save_results()
        
        return 0
        
    except Exception as e:
        logging.error(f"Backtest failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
