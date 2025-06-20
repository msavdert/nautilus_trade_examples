#!/usr/bin/env python3
"""
Results Analysis Module
Comprehensive analysis and visualization of trading bot performance.
"""

import json
import logging
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logging.warning("Matplotlib not available - charts will be disabled")

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    logging.warning("Plotly not available - interactive charts will be disabled")

from utils import MathUtils, format_number


class PerformanceAnalyzer:
    """
    Comprehensive performance analysis for trading bot results.
    
    Features:
    - Trade analysis and statistics
    - Risk metrics calculation
    - Drawdown analysis
    - Performance visualization
    - Comparative analysis
    """
    
    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize performance analyzer.
        
        Args:
            log_file: Optional log file to analyze
        """
        self.logger = logging.getLogger(__name__)
        self.log_file = log_file
        
        # Analysis results
        self.trade_data: List[Dict] = []
        self.equity_curve: List[float] = []
        self.daily_returns: List[float] = []
        self.drawdown_periods: List[Dict] = []
        
        # Performance metrics
        self.metrics: Dict[str, Any] = {}
        
    def load_backtest_results(self, filename: str) -> Dict[str, Any]:
        """
        Load backtest results from JSON file.
        
        Args:
            filename: Results file path
            
        Returns:
            Backtest results dictionary
        """
        try:
            with open(filename, 'r') as f:
                results = json.load(f)
            
            self.logger.info(f"Loaded backtest results from {filename}")
            return results
            
        except FileNotFoundError:
            self.logger.error(f"Results file not found: {filename}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing results file: {e}")
            return {}
    
    def parse_log_file(self, log_file: str) -> List[Dict]:
        """
        Parse trading bot log file to extract trade data.
        
        Args:
            log_file: Path to log file
            
        Returns:
            List of parsed trade records
        """
        trades = []
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if 'TRADE:' in line:
                        # Parse trade line
                        # Expected format: TIMESTAMP - TRADE: SIDE QUANTITY SYMBOL @ PRICE, PnL: $XX.XX
                        trade = self._parse_trade_line(line)
                        if trade:
                            trades.append(trade)
            
            self.logger.info(f"Parsed {len(trades)} trades from {log_file}")
            return trades
            
        except FileNotFoundError:
            self.logger.error(f"Log file not found: {log_file}")
            return []
    
    def _parse_trade_line(self, line: str) -> Optional[Dict]:
        """
        Parse individual trade line from log.
        
        Args:
            line: Log line to parse
            
        Returns:
            Parsed trade dictionary or None
        """
        try:
            # This is a simplified parser - adjust based on your log format
            parts = line.split(' - ')
            if len(parts) < 2:
                return None
            
            timestamp_str = parts[0]
            trade_info = parts[-1]
            
            # Extract trade details
            if 'BUY' in trade_info:
                side = 'BUY'
            elif 'SELL' in trade_info:
                side = 'SELL'
            else:
                return None
            
            # Extract PnL if present
            pnl = 0.0
            if 'PnL:' in trade_info:
                pnl_part = trade_info.split('PnL: $')[1].split()[0]
                pnl = float(pnl_part)
            
            return {
                'timestamp': timestamp_str,
                'side': side,
                'pnl': pnl,
                'raw_line': line.strip()
            }
            
        except Exception as e:
            self.logger.warning(f"Error parsing trade line: {e}")
            return None
    
    def calculate_detailed_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate detailed performance metrics.
        
        Args:
            results: Basic backtest results
            
        Returns:
            Extended metrics dictionary
        """
        metrics = results.copy()
        
        # Time-based metrics
        if 'test_period_days' in results:
            days = results['test_period_days']
            if days > 0:
                metrics['annualized_return'] = (results.get('return_percentage', 0) / days) * 365
                metrics['daily_return_avg'] = results.get('return_percentage', 0) / days
        
        # Risk-adjusted metrics
        if results.get('total_trades', 0) > 0:
            # Calmar ratio (annualized return / max drawdown)
            ann_return = metrics.get('annualized_return', 0)
            max_dd = results.get('max_drawdown', 1)  # Avoid division by zero
            metrics['calmar_ratio'] = ann_return / max_dd if max_dd > 0 else 0
            
            # Sortino ratio (similar to Sharpe but uses downside deviation)
            if 'daily_returns' in results:
                downside_returns = [r for r in results['daily_returns'] if r < 0]
                if downside_returns:
                    downside_std = np.std(downside_returns)
                    metrics['sortino_ratio'] = np.mean(results['daily_returns']) / downside_std
                else:
                    metrics['sortino_ratio'] = float('inf')
        
        # Trading efficiency metrics
        total_trades = results.get('total_trades', 0)
        if total_trades > 0:
            # Average holding period (assuming 1 day per trade for simplification)
            metrics['avg_holding_period'] = 1.0
            
            # Trade frequency
            if 'test_period_days' in results:
                metrics['trades_per_day'] = total_trades / results['test_period_days']
            
            # Recovery factor (net profit / max drawdown)
            net_profit = results.get('total_pnl', 0)
            max_dd_dollar = (results.get('max_drawdown', 0) / 100) * results.get('initial_balance', 1)
            metrics['recovery_factor'] = net_profit / max_dd_dollar if max_dd_dollar > 0 else 0
        
        self.metrics = metrics
        return metrics
    
    def analyze_drawdown_periods(self, equity_curve: List[float]) -> List[Dict]:
        """
        Analyze drawdown periods in equity curve.
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            List of drawdown period information
        """
        if not equity_curve:
            return []
        
        drawdowns = []
        peak = equity_curve[0]
        in_drawdown = False
        drawdown_start = 0
        
        for i, value in enumerate(equity_curve):
            if value > peak:
                # New peak - end drawdown if in one
                if in_drawdown:
                    drawdown_end = i - 1
                    max_dd_value = min(equity_curve[drawdown_start:drawdown_end + 1])
                    max_dd_pct = ((peak - max_dd_value) / peak) * 100
                    
                    drawdowns.append({
                        'start_idx': drawdown_start,
                        'end_idx': drawdown_end,
                        'duration': drawdown_end - drawdown_start + 1,
                        'peak_value': peak,
                        'trough_value': max_dd_value,
                        'drawdown_pct': max_dd_pct,
                        'recovery_idx': i
                    })
                    
                    in_drawdown = False
                
                peak = value
            
            elif value < peak and not in_drawdown:
                # Start of drawdown
                in_drawdown = True
                drawdown_start = i
        
        # Handle ongoing drawdown at end
        if in_drawdown:
            max_dd_value = min(equity_curve[drawdown_start:])
            max_dd_pct = ((peak - max_dd_value) / peak) * 100
            
            drawdowns.append({
                'start_idx': drawdown_start,
                'end_idx': len(equity_curve) - 1,
                'duration': len(equity_curve) - drawdown_start,
                'peak_value': peak,
                'trough_value': max_dd_value,
                'drawdown_pct': max_dd_pct,
                'recovery_idx': None  # Ongoing
            })
        
        self.drawdown_periods = drawdowns
        return drawdowns
    
    def create_performance_report(self, metrics: Dict[str, Any]) -> str:
        """
        Create formatted performance report.
        
        Args:
            metrics: Performance metrics
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE PERFORMANCE ANALYSIS")
        report.append("=" * 80)
        report.append("")
        
        # Basic Performance
        report.append("BASIC PERFORMANCE:")
        report.append(f"  Initial Balance:      ${format_number(metrics.get('initial_balance', 0))}")
        report.append(f"  Final Balance:        ${format_number(metrics.get('final_balance', 0))}")
        report.append(f"  Total Return:         {metrics.get('return_percentage', 0):+.2f}%")
        report.append(f"  Annualized Return:    {metrics.get('annualized_return', 0):+.2f}%")
        report.append(f"  Total PnL:            ${format_number(metrics.get('total_pnl', 0))}")
        report.append("")
        
        # Risk Metrics
        report.append("RISK METRICS:")
        report.append(f"  Maximum Drawdown:     {metrics.get('max_drawdown', 0):.2f}%")
        report.append(f"  Sharpe Ratio:         {metrics.get('sharpe_ratio', 0):.3f}")
        report.append(f"  Sortino Ratio:        {metrics.get('sortino_ratio', 0):.3f}")
        report.append(f"  Calmar Ratio:         {metrics.get('calmar_ratio', 0):.3f}")
        report.append(f"  Recovery Factor:      {metrics.get('recovery_factor', 0):.2f}")
        report.append("")
        
        # Trading Statistics
        report.append("TRADING STATISTICS:")
        report.append(f"  Total Trades:         {metrics.get('total_trades', 0)}")
        report.append(f"  Winning Trades:       {metrics.get('winning_trades', 0)}")
        report.append(f"  Losing Trades:        {metrics.get('losing_trades', 0)}")
        report.append(f"  Win Rate:             {metrics.get('win_rate', 0):.1f}%")
        report.append(f"  Profit Factor:        {metrics.get('profit_factor', 0):.2f}")
        report.append(f"  Average Win:          ${format_number(metrics.get('average_win', 0))}")
        report.append(f"  Average Loss:         ${format_number(metrics.get('average_loss', 0))}")
        report.append("")
        
        # Trading Frequency
        report.append("TRADING FREQUENCY:")
        report.append(f"  Test Period:          {metrics.get('test_period_days', 0)} days")
        report.append(f"  Trades per Day:       {metrics.get('trades_per_day', 0):.2f}")
        report.append(f"  Avg Holding Period:   {metrics.get('avg_holding_period', 0):.1f} days")
        report.append("")
        
        # Strategy Evaluation
        report.append("STRATEGY EVALUATION:")
        
        # Profitability
        if metrics.get('return_percentage', 0) > 0:
            report.append("  ✓ Strategy is profitable")
        else:
            report.append("  ✗ Strategy is unprofitable")
        
        # Risk-adjusted performance
        if metrics.get('sharpe_ratio', 0) > 1.0:
            report.append("  ✓ Good risk-adjusted returns (Sharpe > 1.0)")
        elif metrics.get('sharpe_ratio', 0) > 0.5:
            report.append("  ~ Moderate risk-adjusted returns (Sharpe > 0.5)")
        else:
            report.append("  ✗ Poor risk-adjusted returns (Sharpe < 0.5)")
        
        # Drawdown assessment
        max_dd = metrics.get('max_drawdown', 0)
        if max_dd < 5:
            report.append("  ✓ Low drawdown risk (< 5%)")
        elif max_dd < 10:
            report.append("  ~ Moderate drawdown risk (5-10%)")
        else:
            report.append("  ⚠ High drawdown risk (> 10%)")
        
        # Win rate assessment
        win_rate = metrics.get('win_rate', 0)
        if win_rate > 60:
            report.append("  ✓ High win rate (> 60%)")
        elif win_rate > 50:
            report.append("  ~ Moderate win rate (50-60%)")
        else:
            report.append("  ✗ Low win rate (< 50%)")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def plot_equity_curve(self, equity_curve: List[float], 
                         title: str = "Equity Curve") -> None:
        """
        Plot equity curve with matplotlib.
        
        Args:
            equity_curve: List of equity values
            title: Chart title
        """
        if not HAS_MATPLOTLIB:
            self.logger.warning("Matplotlib not available - skipping chart")
            return
        
        if not equity_curve:
            self.logger.warning("No equity data to plot")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Equity curve
        ax1.plot(equity_curve, linewidth=2, color='blue')
        ax1.set_title(title)
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        peak_curve = np.maximum.accumulate(equity_curve)
        drawdown_curve = ((np.array(equity_curve) - peak_curve) / peak_curve) * 100
        
        ax2.fill_between(range(len(drawdown_curve)), drawdown_curve, 0, 
                        color='red', alpha=0.3, label='Drawdown')
        ax2.plot(drawdown_curve, color='red', linewidth=1)
        ax2.set_ylabel('Drawdown (%)')
        ax2.set_xlabel('Time Period')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
    
    def create_interactive_dashboard(self, metrics: Dict[str, Any], 
                                   equity_curve: List[float]) -> None:
        """
        Create interactive dashboard with Plotly.
        
        Args:
            metrics: Performance metrics
            equity_curve: Equity curve data
        """
        if not HAS_PLOTLY:
            self.logger.warning("Plotly not available - skipping interactive dashboard")
            return
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Equity Curve', 'Drawdown', 'Monthly Returns', 'Trade Distribution'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "bar"}]]
        )
        
        # Equity curve
        fig.add_trace(
            go.Scatter(
                y=equity_curve,
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            ),
            row=1, col=1
        )
        
        # Drawdown
        if equity_curve:
            peak_curve = np.maximum.accumulate(equity_curve)
            drawdown_curve = ((np.array(equity_curve) - peak_curve) / peak_curve) * 100
            
            fig.add_trace(
                go.Scatter(
                    y=drawdown_curve,
                    mode='lines',
                    name='Drawdown',
                    fill='tonexty',
                    line=dict(color='red', width=1)
                ),
                row=1, col=2
            )
        
        # Performance metrics table
        metrics_text = f"""
        <b>Performance Summary:</b><br>
        Total Return: {metrics.get('return_percentage', 0):.2f}%<br>
        Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}<br>
        Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%<br>
        Win Rate: {metrics.get('win_rate', 0):.1f}%<br>
        Total Trades: {metrics.get('total_trades', 0)}
        """
        
        fig.add_annotation(
            text=metrics_text,
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            align="left",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text="Trading Strategy Performance Dashboard",
            showlegend=True
        )
        
        # Save to HTML file
        fig.write_html("performance_dashboard.html")
        self.logger.info("Interactive dashboard saved to performance_dashboard.html")
    
    def compare_strategies(self, results_list: List[Dict[str, Any]], 
                          labels: List[str]) -> None:
        """
        Compare multiple strategy results.
        
        Args:
            results_list: List of strategy results
            labels: Strategy labels
        """
        if len(results_list) != len(labels):
            self.logger.error("Number of results and labels must match")
            return
        
        print("\n" + "=" * 80)
        print("STRATEGY COMPARISON")
        print("=" * 80)
        
        # Create comparison table
        metrics_to_compare = [
            'return_percentage', 'max_drawdown', 'sharpe_ratio',
            'win_rate', 'total_trades', 'profit_factor'
        ]
        
        print(f"{'Metric':<20}", end="")
        for label in labels:
            print(f"{label:>15}", end="")
        print()
        print("-" * (20 + 15 * len(labels)))
        
        for metric in metrics_to_compare:
            print(f"{metric.replace('_', ' ').title():<20}", end="")
            for results in results_list:
                value = results.get(metric, 0)
                if metric == 'return_percentage' or metric == 'max_drawdown' or metric == 'win_rate':
                    print(f"{value:>14.1f}%", end="")
                elif metric == 'sharpe_ratio' or metric == 'profit_factor':
                    print(f"{value:>14.2f}", end="")
                else:
                    print(f"{value:>15.0f}", end="")
            print()
        
        print("=" * 80)


def main():
    """Main entry point for results analysis."""
    parser = argparse.ArgumentParser(description="Analyze trading bot results")
    parser.add_argument("--results-file", help="JSON results file to analyze")
    parser.add_argument("--log-file", help="Log file to parse for trades")
    parser.add_argument("--plot-charts", action="store_true", help="Generate charts")
    parser.add_argument("--interactive", action="store_true", help="Create interactive dashboard")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        analyzer = PerformanceAnalyzer(args.log_file)
        
        if args.results_file:
            # Analyze backtest results
            results = analyzer.load_backtest_results(args.results_file)
            if results:
                metrics = analyzer.calculate_detailed_metrics(results)
                report = analyzer.create_performance_report(metrics)
                print(report)
                
                # Generate charts if requested
                if args.plot_charts and 'equity_curve' in results:
                    analyzer.plot_equity_curve(results['equity_curve'])
                
                if args.interactive and 'equity_curve' in results:
                    analyzer.create_interactive_dashboard(metrics, results['equity_curve'])
        
        elif args.log_file:
            # Parse log file
            trades = analyzer.parse_log_file(args.log_file)
            print(f"Parsed {len(trades)} trades from log file")
            
            # Basic analysis
            if trades:
                total_pnl = sum(trade.get('pnl', 0) for trade in trades)
                winning_trades = len([t for t in trades if t.get('pnl', 0) > 0])
                win_rate = (winning_trades / len(trades)) * 100 if trades else 0
                
                print(f"Total PnL: ${total_pnl:.2f}")
                print(f"Win Rate: {win_rate:.1f}%")
        
        else:
            print("Please provide either --results-file or --log-file")
            return 1
        
        return 0
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
