#!/usr/bin/env python3
"""
Main Entry Point for One-Three Risk Management Bot
=================================================

This script provides a unified interface to run the One-Three trading bot
in different modes: backtesting, live trading, analysis, and testing.

Usage:
    python main.py --mode backtest    # Run backtest
    python main.py --mode live        # Run live trading  
    python main.py --mode analyze     # Analyze results
    python main.py --mode test        # Run tests
    python main.py --mode demo        # Quick demonstration
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Import our modules
from one_three_strategy import OneThreeBot, OneThreeConfig
from utils import RiskCalculator, PerformanceTracker, MarketDataGenerator


def run_demo():
    """
    Run a quick demonstration of the One-Three strategy components.
    
    This mode shows how the strategy components work without
    running a full backtest or live trading session.
    """
    print("🎯 One-Three Strategy Demo")
    print("=" * 40)
    print()
    
    # 1. Show configuration
    print("📋 1. Strategy Configuration:")
    config = OneThreeConfig(
        trade_size=100_000,
        take_profit_pips=1.3,
        stop_loss_pips=1.3,
        max_daily_trades=10,
    )
    
    print(f"   • Instrument: {config.instrument_id}")
    print(f"   • Position Size: {config.trade_size:,} units")
    print(f"   • Take Profit: +{config.take_profit_pips} pips")
    print(f"   • Stop Loss: -{config.stop_loss_pips} pips")
    print(f"   • Risk-Reward: 1:1")
    print()
    
    # 2. Show risk calculations
    print("⚖️ 2. Risk Management:")
    risk_calc = RiskCalculator(account_balance=100_000, max_risk_per_trade=0.01)
    
    entry_price = 1.0800
    stop_loss_price = 1.0787  # -1.3 pips
    take_profit_price = 1.0813  # +1.3 pips
    
    position_size = risk_calc.calculate_position_size(entry_price, stop_loss_price)
    rr_ratio = risk_calc.calculate_risk_reward_ratio(entry_price, take_profit_price, stop_loss_price)
    
    print(f"   • Account Balance: ${risk_calc.account_balance:,}")
    print(f"   • Risk per Trade: {risk_calc.max_risk_per_trade * 100}%")
    print(f"   • Suggested Position: {position_size:,} units")
    print(f"   • Risk-Reward Ratio: {rr_ratio:.1f}:1")
    print()
    
    # 3. Show market data generation
    print("📊 3. Market Data Generation:")
    from datetime import datetime, timedelta
    
    data_gen = MarketDataGenerator(seed=42)
    sample_data = data_gen.generate_tick_data(
        start_date=datetime.now() - timedelta(hours=1),
        end_date=datetime.now(),
        num_ticks=100,
        base_price=1.0800
    )
    
    print(f"   • Generated {len(sample_data)} ticks")
    print(f"   • Price range: {sample_data['bid_price'].min():.5f} - {sample_data['ask_price'].max():.5f}")
    print(f"   • Avg spread: {(sample_data['ask_price'] - sample_data['bid_price']).mean() * 10000:.1f} pips")
    print()
    
    # 4. Show performance tracking
    print("📈 4. Performance Tracking Demo:")
    tracker = PerformanceTracker()
    
    # Simulate some trades
    import random
    random.seed(42)
    
    for i in range(10):
        is_winner = random.random() < 0.6  # 60% win rate
        pnl = 13.0 if is_winner else -13.0
        reason = "TAKE_PROFIT" if is_winner else "STOP_LOSS"
        
        tracker.add_trade(
            entry_time=datetime.now() - timedelta(minutes=10*(i+1)),
            exit_time=datetime.now() - timedelta(minutes=10*i),
            entry_price=1.0800,
            exit_price=1.0813 if is_winner else 1.0787,
            position_size=100_000,
            pnl=pnl,
            reason=reason
        )
    
    stats = tracker.get_statistics()
    print(f"   • Total Trades: {stats['total_trades']}")
    print(f"   • Win Rate: {stats['win_rate']:.1f}%")
    print(f"   • Total P&L: ${stats['total_pnl']:.2f}")
    print(f"   • Profit Factor: {stats['profit_factor']:.2f}")
    print()
    
    print("✅ Demo complete! Ready to run backtests or live trading.")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="One-Three Risk Management Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode demo        # Quick demonstration
  python main.py --mode backtest    # Run backtest with sample data
  python main.py --mode live        # Start live trading (requires setup)
  python main.py --mode analyze     # Analyze trading results
  python main.py --mode test        # Run test suite
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['demo', 'backtest', 'live', 'analyze', 'test'],
        default='demo',
        help='Mode to run the bot in (default: demo)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file (optional)'
    )
    
    parser.add_argument(
        '--data',
        help='Path to market data file for backtesting (optional)'
    )
    
    parser.add_argument(
        '--output',
        help='Output directory for results (optional)'
    )
    
    args = parser.parse_args()
    
    print("🤖 One-Three Risk Management Trading Bot")
    print("=" * 50)
    print(f"Mode: {args.mode.upper()}")
    print()
    
    try:
        if args.mode == 'demo':
            run_demo()
            
        elif args.mode == 'backtest':
            print("🔄 Starting backtest...")
            import run_backtest
            run_backtest.run_backtest()
            
        elif args.mode == 'live':
            print("🔴 Starting live trading...")
            print("⚠️ Make sure you have configured your data and execution providers!")
            import run_live
            asyncio.run(run_live.main())
            
        elif args.mode == 'analyze':
            print("📊 Starting results analysis...")
            import analyze_results
            analyzer = analyze_results.TradingAnalyzer()
            analyzer.run_complete_analysis(args.data)
            
        elif args.mode == 'test':
            print("🧪 Running test suite...")
            import test_strategy
            success = test_strategy.run_tests()
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
