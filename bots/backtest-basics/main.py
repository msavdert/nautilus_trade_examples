#!/usr/bin/env python3
# -------------------------------------------------------------------------------------------------
# Nautilus Trader Backtest Example
# Complete tutorial on how to backtest trading strategies with historical data
# -------------------------------------------------------------------------------------------------

from decimal import Decimal
from datetime import datetime

# Core Nautilus imports for backtesting
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.config import BacktestEngineConfig
from nautilus_trader.config import BacktestRunConfig, BacktestVenueConfig, BacktestDataConfig
from nautilus_trader.backtest.node import BacktestNode

# Strategy and configuration imports  
from nautilus_trader.config import ImportableStrategyConfig, LoggingConfig

# Market data and trading objects
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.enums import AccountType, OmsType
from nautilus_trader.model.identifiers import Venue
from nautilus_trader.model.objects import Money
from nautilus_trader.model.data import QuoteTick, BarType, Bar
from nautilus_trader.model.identifiers import InstrumentId


class BacktestTutorial:
    """
    Complete tutorial for running backtests with Nautilus Trader.
    
    This class demonstrates the core concepts and approaches to backtesting
    without requiring external data dependencies.
    """
    
    def __init__(self):
        print("🔧 Initializing Backtest Tutorial...")
        # We'll use demo concepts without actual data for this tutorial
        
    def explain_basic_backtest_engine(self):
        """
        Method 1: Basic backtest using BacktestEngine directly (Low-level API)
        
        This approach gives you full control but requires more manual setup.
        Good for: Learning, custom setups, fine-grained control
        """
        print("\n🚀 Explaining Basic Backtest with BacktestEngine...")
        print("=" * 60)
        
        print("📋 Step-by-step process:")
        print("1. Configure the backtest engine")
        print("2. Create the backtest engine")
        print("3. Add a trading venue (exchange/broker)")
        print("4. Add instruments to trade")
        print("5. Add historical market data")
        print("6. Add your trading strategy")
        print("7. Run the backtest")
        print("8. Analyze results")
        
        print("\n💻 Example code structure:")
        print("""
        # Step 1: Configure the backtest engine
        engine_config = BacktestEngineConfig(
            trader_id="BACKTEST-001",
            logging=LoggingConfig(log_level="INFO"),
        )
        
        # Step 2: Create the backtest engine
        engine = BacktestEngine(config=engine_config)
        
        # Step 3: Add a trading venue
        engine.add_venue(
            venue=Venue("SIM"),
            oms_type=OmsType.HEDGING,
            account_type=AccountType.MARGIN,
            base_currency=USD,
            starting_balances=[Money(100_000, USD)],
        )
        
        # Steps 4-8: Add instrument, data, strategy, run, analyze
        """)
        
    def explain_advanced_backtest_node(self):
        """
        Method 2: Advanced backtest using BacktestNode (High-level API)
        
        This is the recommended approach for most use cases.
        Good for: Production use, complex scenarios, multiple strategies
        """
        print("\n🚀 Explaining Advanced Backtest with BacktestNode...")
        print("=" * 60)
        
        print("📋 Configuration-based approach:")
        print("1. Configure the strategy")
        print("2. Configure the backtest engine")
        print("3. Configure the trading venue")
        print("4. Configure the data source")
        print("5. Create run configuration")
        print("6. Execute with BacktestNode")
        
        print("\n💻 Example configuration structure:")
        print("""
        # Strategy configuration
        strategy_config = ImportableStrategyConfig(
            strategy_path="my_strategy.main:MyStrategy",
            config_path="my_strategy.main:MyStrategyConfig",
            config={
                "instrument_id": "EUR/USD.SIM",
                "trade_size": 100_000,
                "ma_period": 10,
            }
        )
        
        # Engine configuration
        engine_config = BacktestEngineConfig(
            trader_id="BACKTEST-NODE-001",
            strategies=[strategy_config],
        )
        
        # Venue configuration
        venue_config = BacktestVenueConfig(
            name="SIM",
            oms_type="HEDGING",
            account_type="MARGIN",
            starting_balances=["100_000 USD"],
        )
        
        # Data configuration
        data_config = BacktestDataConfig(
            data_cls=QuoteTick,
            catalog_path="./data",
            instrument_id="EUR/USD.SIM",
            start_time="2023-01-01",
            end_time="2023-01-31",
        )
        
        # Run configuration
        run_config = BacktestRunConfig(
            engine=engine_config,
            venues=[venue_config],
            data=[data_config],
        )
        
        # Execute
        node = BacktestNode(configs=[run_config])
        results = node.run()
        """)
        
    def explain_data_types_and_sources(self):
        """
        Explain different types of market data and where to get them
        """
        print("\n🚀 Understanding Market Data for Backtesting...")
        print("=" * 60)
        
        print("📊 Types of Market Data:")
        print("1. Tick Data:")
        print("   - Individual price quotes and trades")
        print("   - Highest resolution, largest storage")
        print("   - Best for strategies sensitive to execution")
        print("   - Example: QuoteTick, TradeTick")
        
        print("\n2. Bar Data (OHLC):")
        print("   - Open, High, Low, Close for time periods")
        print("   - Medium resolution, manageable storage") 
        print("   - Good for most trend-following strategies")
        print("   - Example: 1-minute, 5-minute, hourly bars")
        
        print("\n3. Order Book Data:")
        print("   - Bid/ask levels and quantities")
        print("   - High resolution, complex analysis")
        print("   - For market making and arbitrage")
        print("   - Example: Level 2, Level 3 data")
        
        print("\n📈 Data Sources:")
        print("- Cryptocurrency: Binance, Coinbase, Kraken")
        print("- Forex: Dukascopy, TrueFX, FXCM")
        print("- Stocks: Yahoo Finance, Alpha Vantage, IEX")
        print("- Professional: Bloomberg, Reuters, Refinitiv")
        
    def explain_performance_metrics(self):
        """
        Explain key performance metrics for backtesting
        """
        print("\n🚀 Understanding Backtest Performance Metrics...")
        print("=" * 60)
        
        print("📊 Key Performance Indicators:")
        
        print("\n💰 Return Metrics:")
        print("- Total Return: Overall percentage gain/loss")
        print("- Annualized Return: Return normalized to yearly basis")
        print("- CAGR: Compound Annual Growth Rate")
        
        print("\n⚠️  Risk Metrics:")
        print("- Maximum Drawdown: Worst peak-to-trough loss")
        print("- Volatility: Standard deviation of returns")
        print("- VaR: Value at Risk (potential loss)")
        
        print("\n📈 Risk-Adjusted Returns:")
        print("- Sharpe Ratio: Return per unit of risk")
        print("- Sortino Ratio: Like Sharpe but only downside risk")
        print("- Calmar Ratio: Return / Maximum Drawdown")
        
        print("\n🎯 Trade Statistics:")
        print("- Win Rate: Percentage of profitable trades")
        print("- Profit Factor: Gross profit / Gross loss")
        print("- Average Trade: Average profit per trade")
        print("- Expectancy: Expected value per trade")
        
        print("\n⏰ Timing Metrics:")
        print("- Trade Frequency: Number of trades per period")
        print("- Average Hold Time: Time positions are held")
        print("- Turnover: Portfolio turnover rate")
        
    def explain_best_practices(self):
        """
        Explain backtesting best practices and common pitfalls
        """
        print("\n🚀 Backtesting Best Practices...")
        print("=" * 60)
        
        print("✅ DO:")
        print("- Use out-of-sample data for validation")
        print("- Include realistic transaction costs")
        print("- Account for slippage and market impact")
        print("- Test across different market conditions")
        print("- Use walk-forward analysis")
        print("- Implement proper risk management")
        print("- Document all assumptions")
        
        print("\n❌ DON'T:")
        print("- Over-optimize on historical data (curve fitting)")
        print("- Use look-ahead bias (future information)")
        print("- Ignore survivorship bias")
        print("- Assume infinite liquidity")
        print("- Skip out-of-sample testing")
        print("- Ignore market regime changes")
        print("- Trade without stop losses")
        
        print("\n⚠️  Common Pitfalls:")
        print("- Data snooping: Testing too many strategies")
        print("- Survivorship bias: Only using successful assets")
        print("- Look-ahead bias: Using future information")
        print("- Overfitting: Too many parameters")
        print("- Ignoring costs: Unrealistic assumptions")
        print("- Point-in-time issues: Using latest data")
        
    def explain_next_steps(self):
        """
        Provide guidance on next steps after learning backtesting
        """
        print("\n� Next Steps in Your Trading Journey...")
        print("=" * 60)
        
        print("🎯 Immediate Next Steps:")
        print("1. Get familiar with the my-first-bot strategy")
        print("2. Download historical data for your chosen market")
        print("3. Run your first backtest with real data")
        print("4. Analyze the results and identify improvements")
        
        print("\n📚 Learning Path:")
        print("Phase 1: Basic Backtesting")
        print("- Master the my-first-bot example")
        print("- Understand different data types")
        print("- Learn to interpret results")
        
        print("\nPhase 2: Strategy Development")
        print("- Create your own strategies")
        print("- Implement proper risk management")
        print("- Add indicators and signals")
        
        print("\nPhase 3: Advanced Techniques")
        print("- Multi-asset strategies")
        print("- Portfolio optimization")
        print("- Walk-forward analysis")
        print("- Monte Carlo simulations")
        
        print("\nPhase 4: Production Ready")
        print("- Paper trading")
        print("- Risk monitoring")
        print("- Performance tracking")
        print("- Live trading preparation")
        
        print("\n🛠️  Tools to Master:")
        print("- Nautilus Trader: Trading framework")
        print("- Pandas: Data analysis")
        print("- NumPy: Numerical computing")
        print("- Matplotlib/Plotly: Visualization")
        print("- Jupyter: Interactive development")

    def run_tutorial(self):
        """Run the complete backtesting tutorial"""
        print("🎯 Nautilus Trader Backtest Tutorial")
        print("=" * 60)
        print("Learn everything about backtesting trading strategies!")
        
        # Run all tutorial sections
        self.explain_basic_backtest_engine()
        self.explain_advanced_backtest_node()
        self.explain_data_types_and_sources()
        self.explain_performance_metrics()
        self.explain_best_practices()
        self.explain_next_steps()
        
        print("\n🎓 Tutorial Completed Successfully!")
        print("=" * 60)
        print("📚 What you learned:")
        print("- Two main approaches to backtesting")
        print("- Types of market data and sources")
        print("- Key performance metrics")
        print("- Best practices and pitfalls to avoid")
        print("- Clear path forward for development")
        
        print("\n🚀 Ready for Action:")
        print("1. Study the my-first-bot strategy")
        print("2. Get historical data for your market")
        print("3. Implement your first backtest")
        print("4. Iterate and improve!")


def main():
    """
    Main function to run the backtest tutorial
    """
    print("🤖 Nautilus Trader Backtest Tutorial")
    print("This comprehensive guide teaches you everything about backtesting!")
    print("Check the README.md for detailed code examples and explanations!")
    
    # Create and run the tutorial
    tutorial = BacktestTutorial()
    tutorial.run_tutorial()


if __name__ == "__main__":
    main()


