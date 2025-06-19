#!/usr/bin/env python3
"""
Results Analysis for One-Three Risk Management Bot
================================================

This script provides comprehensive analysis of trading results from both
backtesting and live trading sessions. It generates detailed reports including:

1. Performance metrics and statistics
2. Risk analysis and drawdown calculations  
3. Trade distribution and patterns
4. Visual charts and graphs
5. Detailed trade-by-trade breakdown

The analysis helps evaluate strategy performance and identify areas for optimization.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional, Tuple
import argparse


class TradingAnalyzer:
    """
    Comprehensive trading results analyzer for the One-Three strategy.
    
    This class provides detailed analysis of trading performance including:
    - P&L calculations and statistics
    - Risk metrics and drawdown analysis
    - Win/loss ratios and distributions
    - Time-based performance patterns
    - Visual reporting and charts
    """
    
    def __init__(self, results_file: Optional[str] = None):
        """
        Initialize the analyzer.
        
        Args:
            results_file: Path to results file (CSV or JSON)
        """
        self.results_file = results_file
        self.trades_df: Optional[pd.DataFrame] = None
        self.summary_stats: Dict = {}
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        sns.set_palette("husl")
        
    def load_results(self, file_path: str = None) -> pd.DataFrame:
        """
        Load trading results from file or generate sample data.
        
        Args:
            file_path: Path to results file
            
        Returns:
            DataFrame containing trade data
        """
        if file_path and Path(file_path).exists():
            print(f"📁 Loading results from {file_path}")
            
            if file_path.endswith('.csv'):
                self.trades_df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.trades_df = pd.DataFrame(data)
            else:
                raise ValueError("Unsupported file format. Use CSV or JSON.")
                
        else:
            print("📊 Generating sample trading results for analysis...")
            self.trades_df = self._generate_sample_results()
            
        # Ensure required columns exist
        self._validate_data()
        
        # Process timestamps
        if 'entry_time' in self.trades_df.columns:
            self.trades_df['entry_time'] = pd.to_datetime(self.trades_df['entry_time'])
        if 'exit_time' in self.trades_df.columns:
            self.trades_df['exit_time'] = pd.to_datetime(self.trades_df['exit_time'])
            
        print(f"✅ Loaded {len(self.trades_df)} trades for analysis")
        return self.trades_df
        
    def _generate_sample_results(self) -> pd.DataFrame:
        """
        Generate realistic sample trading results for demonstration.
        
        Returns:
            DataFrame with sample trade data
        """
        np.random.seed(42)  # For reproducible results
        
        # Generate 100 sample trades over 30 days
        num_trades = 100
        start_date = datetime.now() - timedelta(days=30)
        
        trades = []
        current_time = start_date
        cumulative_pnl = 0
        
        for i in range(num_trades):
            # Generate trade timing (random intervals between 1-6 hours)
            time_delta = timedelta(hours=np.random.uniform(1, 6))
            entry_time = current_time + time_delta
            
            # Generate trade duration (1-30 minutes for this strategy)
            duration = timedelta(minutes=np.random.uniform(1, 30))
            exit_time = entry_time + duration
            
            # Generate entry/exit prices (around 1.0800 for EUR/USD)
            entry_price = np.random.uniform(1.0750, 1.0850)
            
            # Determine if it's a winning or losing trade (60% win rate)
            is_winner = np.random.random() < 0.60
            
            if is_winner:
                # Winning trade: +1.3 pips
                exit_price = entry_price + 0.00013
                pnl_pips = 1.3
                exit_reason = "TAKE_PROFIT"
            else:
                # Losing trade: -1.3 pips  
                exit_price = entry_price - 0.00013
                pnl_pips = -1.3
                exit_reason = "STOP_LOSS"
                
            # Calculate P&L in USD (100,000 unit position)
            pnl_usd = pnl_pips * 10  # $10 per pip for standard lot EUR/USD
            cumulative_pnl += pnl_usd
            
            trade = {
                'trade_id': i + 1,
                'entry_time': entry_time,
                'exit_time': exit_time,
                'entry_price': round(entry_price, 5),
                'exit_price': round(exit_price, 5),
                'position_size': 100000,
                'pnl_pips': pnl_pips,
                'pnl_usd': pnl_usd,
                'cumulative_pnl': cumulative_pnl,
                'exit_reason': exit_reason,
                'duration_minutes': duration.total_seconds() / 60,
            }
            
            trades.append(trade)
            current_time = exit_time
            
        return pd.DataFrame(trades)
        
    def _validate_data(self):
        """Validate that required columns exist in the data."""
        required_columns = ['pnl_usd', 'pnl_pips', 'exit_reason']
        missing_columns = [col for col in required_columns if col not in self.trades_df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
            
    def calculate_statistics(self) -> Dict:
        """
        Calculate comprehensive trading statistics.
        
        Returns:
            Dictionary containing all performance metrics
        """
        print("📊 Calculating performance statistics...")
        
        df = self.trades_df
        
        # Basic metrics
        total_trades = len(df)
        winning_trades = len(df[df['pnl_usd'] > 0])
        losing_trades = len(df[df['pnl_usd'] < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # P&L metrics
        total_pnl = df['pnl_usd'].sum()
        avg_win = df[df['pnl_usd'] > 0]['pnl_usd'].mean() if winning_trades > 0 else 0
        avg_loss = df[df['pnl_usd'] < 0]['pnl_usd'].mean() if losing_trades > 0 else 0
        
        # Risk metrics
        max_drawdown = self._calculate_max_drawdown()
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # Profit factor (gross profit / gross loss)
        gross_profit = df[df['pnl_usd'] > 0]['pnl_usd'].sum()
        gross_loss = abs(df[df['pnl_usd'] < 0]['pnl_usd'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)
        
        self.summary_stats = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'profit_factor': profit_factor,
            'expectancy': expectancy,
            'largest_win': df['pnl_usd'].max(),
            'largest_loss': df['pnl_usd'].min(),
        }
        
        return self.summary_stats
        
    def _calculate_max_drawdown(self) -> float:
        """Calculate maximum drawdown from peak equity."""
        if 'cumulative_pnl' not in self.trades_df.columns:
            return 0.0
            
        cum_pnl = self.trades_df['cumulative_pnl']
        running_max = cum_pnl.cummax()
        drawdown = cum_pnl - running_max
        max_drawdown = drawdown.min()
        
        return max_drawdown
        
    def _calculate_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio (assuming risk-free rate of 2%)."""
        if len(self.trades_df) < 2:
            return 0.0
            
        returns = self.trades_df['pnl_usd']
        excess_return = returns.mean() - 0.02/252  # Daily risk-free rate
        volatility = returns.std()
        
        if volatility == 0:
            return 0.0
            
        sharpe = excess_return / volatility * np.sqrt(252)  # Annualized
        return sharpe
        
    def generate_report(self) -> str:
        """
        Generate a comprehensive text report.
        
        Returns:
            String containing formatted report
        """
        if not self.summary_stats:
            self.calculate_statistics()
            
        stats = self.summary_stats
        
        report = f"""
{'='*60}
ONE-THREE STRATEGY PERFORMANCE REPORT
{'='*60}

📊 TRADING SUMMARY
{'─'*30}
Total Trades:           {stats['total_trades']:,}
Winning Trades:         {stats['winning_trades']:,} ({stats['win_rate']:.1f}%)
Losing Trades:          {stats['losing_trades']:,} ({100-stats['win_rate']:.1f}%)

💰 PROFIT & LOSS
{'─'*30}
Total P&L:              ${stats['total_pnl']:,.2f}
Average Win:            ${stats['avg_win']:,.2f}
Average Loss:           ${stats['avg_loss']:,.2f}
Largest Win:            ${stats['largest_win']:,.2f}
Largest Loss:           ${stats['largest_loss']:,.2f}

📈 PERFORMANCE METRICS  
{'─'*30}
Profit Factor:          {stats['profit_factor']:.2f}
Expectancy:             ${stats['expectancy']:,.2f}
Sharpe Ratio:           {stats['sharpe_ratio']:.2f}
Max Drawdown:           ${stats['max_drawdown']:,.2f}

🎯 STRATEGY ANALYSIS
{'─'*30}
Risk Management:        ±1.3 pips per trade
Position Sizing:        Fixed (100,000 units)
Win Rate Target:        >50% (Actual: {stats['win_rate']:.1f}%)
R:R Ratio:              1:1 (Fixed TP/SL)

💡 OBSERVATIONS
{'─'*30}
"""
        
        # Add strategy-specific observations
        if stats['win_rate'] >= 50:
            report += "✅ Win rate meets expectation for 1:1 R:R strategy\n"
        else:
            report += "⚠️ Win rate below 50% - strategy may need optimization\n"
            
        if stats['profit_factor'] > 1.0:
            report += "✅ Positive profit factor indicates profitable strategy\n"
        else:
            report += "❌ Profit factor below 1.0 - strategy losing money\n"
            
        if abs(stats['max_drawdown']) < 1000:
            report += "✅ Drawdown well controlled\n"
        else:
            report += "⚠️ High drawdown - consider reducing position size\n"
            
        report += f"\n{'='*60}\n"
        
        return report
        
    def create_visualizations(self, save_path: str = "analysis_charts"):
        """
        Create comprehensive visualization charts.
        
        Args:
            save_path: Directory to save chart files
        """
        print("📈 Creating visualization charts...")
        
        # Create output directory
        Path(save_path).mkdir(exist_ok=True)
        
        # Set up the figure layout
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Equity Curve
        plt.subplot(3, 3, 1)
        if 'cumulative_pnl' in self.trades_df.columns:
            plt.plot(self.trades_df.index, self.trades_df['cumulative_pnl'], 'b-', linewidth=2)
            plt.title('Equity Curve', fontsize=14, fontweight='bold')
            plt.xlabel('Trade Number')
            plt.ylabel('Cumulative P&L ($)')
            plt.grid(True, alpha=0.3)
            
        # 2. P&L Distribution
        plt.subplot(3, 3, 2)
        plt.hist(self.trades_df['pnl_usd'], bins=30, alpha=0.7, edgecolor='black')
        plt.axvline(0, color='red', linestyle='--', linewidth=2)
        plt.title('P&L Distribution', fontsize=14, fontweight='bold')
        plt.xlabel('P&L per Trade ($)')
        plt.ylabel('Frequency')
        plt.grid(True, alpha=0.3)
        
        # 3. Win/Loss Ratio Pie Chart
        plt.subplot(3, 3, 3)
        wins = len(self.trades_df[self.trades_df['pnl_usd'] > 0])
        losses = len(self.trades_df[self.trades_df['pnl_usd'] < 0])
        plt.pie([wins, losses], labels=['Wins', 'Losses'], autopct='%1.1f%%',
                colors=['green', 'red'], startangle=90)
        plt.title('Win/Loss Ratio', fontsize=14, fontweight='bold')
        
        # 4. Trade Duration Analysis
        if 'duration_minutes' in self.trades_df.columns:
            plt.subplot(3, 3, 4)
            plt.hist(self.trades_df['duration_minutes'], bins=20, alpha=0.7, edgecolor='black')
            plt.title('Trade Duration Distribution', fontsize=14, fontweight='bold')
            plt.xlabel('Duration (minutes)')
            plt.ylabel('Frequency')
            plt.grid(True, alpha=0.3)
            
        # 5. Exit Reason Analysis
        plt.subplot(3, 3, 5)
        exit_counts = self.trades_df['exit_reason'].value_counts()
        plt.bar(exit_counts.index, exit_counts.values, alpha=0.7)
        plt.title('Exit Reasons', fontsize=14, fontweight='bold')
        plt.xlabel('Exit Reason')
        plt.ylabel('Count')
        plt.xticks(rotation=45)
        
        # 6. Drawdown Chart
        plt.subplot(3, 3, 6)
        if 'cumulative_pnl' in self.trades_df.columns:
            cum_pnl = self.trades_df['cumulative_pnl']
            running_max = cum_pnl.cummax()
            drawdown = cum_pnl - running_max
            plt.fill_between(self.trades_df.index, 0, drawdown, alpha=0.7, color='red')
            plt.title('Drawdown', fontsize=14, fontweight='bold')
            plt.xlabel('Trade Number')
            plt.ylabel('Drawdown ($)')
            plt.grid(True, alpha=0.3)
            
        # 7. Monthly Performance (if applicable)
        if 'entry_time' in self.trades_df.columns:
            plt.subplot(3, 3, 7)
            monthly_pnl = self.trades_df.set_index('entry_time')['pnl_usd'].resample('M').sum()
            monthly_pnl.plot(kind='bar', alpha=0.7)
            plt.title('Monthly P&L', fontsize=14, fontweight='bold')
            plt.xlabel('Month')
            plt.ylabel('P&L ($)')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            
        # 8. Rolling Win Rate
        plt.subplot(3, 3, 8)
        window = min(20, len(self.trades_df) // 4)  # 20-trade rolling window or 1/4 of data
        if window > 1:
            winning_trades = (self.trades_df['pnl_usd'] > 0).astype(int)
            rolling_win_rate = winning_trades.rolling(window=window).mean() * 100
            plt.plot(self.trades_df.index, rolling_win_rate, 'g-', linewidth=2)
            plt.axhline(50, color='red', linestyle='--', linewidth=2)
            plt.title(f'{window}-Trade Rolling Win Rate', fontsize=14, fontweight='bold')
            plt.xlabel('Trade Number')
            plt.ylabel('Win Rate (%)')
            plt.grid(True, alpha=0.3)
            
        # 9. Risk-Return Scatter
        plt.subplot(3, 3, 9)
        plt.scatter(self.trades_df['pnl_pips'], self.trades_df['pnl_usd'], alpha=0.6)
        plt.title('Risk vs Return', fontsize=14, fontweight='bold')
        plt.xlabel('P&L (pips)')
        plt.ylabel('P&L ($)')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout(pad=3.0)
        
        # Save the comprehensive chart
        chart_path = f"{save_path}/one_three_analysis.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"💾 Charts saved to {chart_path}")
        
        plt.show()
        
    def export_detailed_report(self, output_file: str = "one_three_report.txt"):
        """
        Export detailed analysis report to file.
        
        Args:
            output_file: Output file path
        """
        report = self.generate_report()
        
        with open(output_file, 'w') as f:
            f.write(report)
            f.write("\n\nDETAILED TRADE BREAKDOWN\n")
            f.write("=" * 60 + "\n")
            f.write(self.trades_df.to_string(index=False))
            
        print(f"📄 Detailed report exported to {output_file}")
        
    def run_complete_analysis(self, results_file: str = None):
        """
        Run complete analysis pipeline.
        
        Args:
            results_file: Path to results file (optional)
        """
        print("🚀 Running Complete One-Three Strategy Analysis")
        print("=" * 60)
        
        # Load data
        self.load_results(results_file)
        
        # Calculate statistics
        self.calculate_statistics()
        
        # Generate and display report
        report = self.generate_report()
        print(report)
        
        # Create visualizations
        self.create_visualizations()
        
        # Export detailed report
        self.export_detailed_report()
        
        print("\n✅ Analysis complete!")
        print("📊 Review the charts and detailed report for insights.")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Analyze One-Three Strategy Results')
    parser.add_argument('--file', '-f', help='Results file path (CSV or JSON)')
    parser.add_argument('--output', '-o', default='one_three_report.txt', 
                       help='Output report file')
    
    args = parser.parse_args()
    
    # Create analyzer and run analysis
    analyzer = TradingAnalyzer()
    analyzer.run_complete_analysis(args.file)


if __name__ == "__main__":
    main()
