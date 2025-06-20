#!/usr/bin/env python3
"""
Results Analysis Tool for Binance Futures Testnet Bot

This script analyzes trading results, generates performance reports,
and provides detailed insights into strategy performance.

Features:
- Performance metrics calculation
- Risk analysis
- Trade pattern analysis
- Visual performance charts
- Detailed reporting

Usage:
    python analyze_results.py --log-file logs/binance_testnet_bot_20241218.log
    python analyze_results.py --backtest-results backtest_results/
    python analyze_results.py --generate-report --output reports/
"""

import argparse
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns

from utils import PerformanceTracker, LoggingUtils, DataUtils, MathUtils


class ResultsAnalyzer:
    """
    Comprehensive results analysis for the trading bot.
    
    Analyzes trading performance from various sources:
    - Log files
    - Backtest results
    - Real-time trading data
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize results analyzer.
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = output_dir or Path(__file__).parent / "analysis_results"
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.logger = LoggingUtils.setup_logger(
            "ResultsAnalyzer", 
            "INFO", 
            self.output_dir / "logs"
        )
        
        # Data storage
        self.trades: List[Dict] = []
        self.portfolio_snapshots: List[Dict] = []
        self.risk_events: List[Dict] = []
        self.performance_metrics: Dict = {}
        
        self.logger.info("Results Analyzer initialized")
    
    def analyze_log_file(self, log_file: Path) -> Dict[str, Any]:
        """
        Analyze trading bot log file.
        
        Args:
            log_file: Path to log file
            
        Returns:
            Analysis results dictionary
        """
        self.logger.info(f"Analyzing log file: {log_file}")
        
        if not log_file.exists():
            raise FileNotFoundError(f"Log file not found: {log_file}")
        
        # Parse log file
        trades, portfolio_data, risk_events = self._parse_log_file(log_file)
        
        # Store data
        self.trades.extend(trades)
        self.portfolio_snapshots.extend(portfolio_data)
        self.risk_events.extend(risk_events)
        
        # Calculate metrics
        metrics = self._calculate_performance_metrics()
        
        self.logger.info(f"Analysis complete: {len(trades)} trades, {len(risk_events)} risk events")
        return metrics
    
    def analyze_backtest_results(self, results_dir: Path) -> Dict[str, Any]:
        """
        Analyze backtest results directory.
        
        Args:
            results_dir: Directory containing backtest results
            
        Returns:
            Analysis results dictionary
        """
        self.logger.info(f"Analyzing backtest results: {results_dir}")
        
        if not results_dir.exists():
            raise FileNotFoundError(f"Results directory not found: {results_dir}")
        
        # Find result files
        json_files = list(results_dir.glob("**/backtest_results.json"))
        
        if not json_files:
            raise FileNotFoundError("No backtest results found")
        
        all_results = {}
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                result_name = json_file.parent.name
                all_results[result_name] = data
                
                # Extract trades if available
                if 'trades' in data:
                    self.trades.extend(data['trades'])
                
            except Exception as e:
                self.logger.error(f"Error reading {json_file}: {e}")
        
        # Calculate aggregate metrics
        metrics = self._calculate_backtest_metrics(all_results)
        
        self.logger.info(f"Backtest analysis complete: {len(all_results)} result sets")
        return metrics
    
    def _parse_log_file(self, log_file: Path) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Parse trading bot log file."""
        trades = []
        portfolio_data = []
        risk_events = []
        
        # Regex patterns for log parsing
        trade_pattern = r'Position (opened|closed): (\w+) (\w+) ([\d.]+).*PnL: ([-\d.]+)'
        portfolio_pattern = r'Portfolio value: \$([\d,.]+)'
        risk_pattern = r'RISK VIOLATION: (.+)'
        
        try:
            with open(log_file, 'r') as f:
                for line_no, line in enumerate(f, 1):
                    try:
                        # Extract timestamp
                        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', line)
                        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S') if timestamp_match else None
                        
                        # Parse trades
                        trade_match = re.search(trade_pattern, line)
                        if trade_match:
                            action, instrument, side, quantity, pnl = trade_match.groups()
                            
                            trade = {
                                'timestamp': timestamp,
                                'action': action,
                                'instrument': instrument,
                                'side': side,
                                'quantity': float(quantity),
                                'pnl': float(pnl) if action == 'closed' else 0.0,
                                'line_no': line_no
                            }
                            trades.append(trade)
                        
                        # Parse portfolio snapshots
                        portfolio_match = re.search(portfolio_pattern, line)
                        if portfolio_match:
                            value = float(portfolio_match.group(1).replace(',', ''))
                            
                            snapshot = {
                                'timestamp': timestamp,
                                'portfolio_value': value,
                                'line_no': line_no
                            }
                            portfolio_data.append(snapshot)
                        
                        # Parse risk events
                        risk_match = re.search(risk_pattern, line)
                        if risk_match:
                            event = {
                                'timestamp': timestamp,
                                'violation': risk_match.group(1),
                                'line_no': line_no
                            }
                            risk_events.append(event)
                    
                    except Exception as e:
                        self.logger.warning(f"Error parsing line {line_no}: {e}")
                        continue
        
        except Exception as e:
            self.logger.error(f"Error reading log file: {e}")
            raise
        
        return trades, portfolio_data, risk_events
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        if not self.trades:
            return {"error": "No trades found for analysis"}
        
        # Convert trades to DataFrame
        df_trades = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(df_trades)
        closed_trades = df_trades[df_trades['action'] == 'closed']
        
        if len(closed_trades) == 0:
            return {"error": "No closed trades found"}
        
        # P&L analysis
        total_pnl = closed_trades['pnl'].sum()
        winning_trades = closed_trades[closed_trades['pnl'] > 0]
        losing_trades = closed_trades[closed_trades['pnl'] < 0]
        
        # Win rate
        win_rate = len(winning_trades) / len(closed_trades) if len(closed_trades) > 0 else 0
        
        # Profit factor
        gross_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Average metrics
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        # Risk metrics
        max_win = winning_trades['pnl'].max() if len(winning_trades) > 0 else 0
        max_loss = losing_trades['pnl'].min() if len(losing_trades) > 0 else 0
        
        # Portfolio analysis
        if self.portfolio_snapshots:
            df_portfolio = pd.DataFrame(self.portfolio_snapshots)
            df_portfolio = df_portfolio.sort_values('timestamp')
            
            initial_value = df_portfolio['portfolio_value'].iloc[0]
            final_value = df_portfolio['portfolio_value'].iloc[-1]
            total_return = (final_value - initial_value) / initial_value
            
            # Calculate max drawdown
            rolling_max = df_portfolio['portfolio_value'].expanding().max()
            drawdown = (df_portfolio['portfolio_value'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
        else:
            total_return = 0
            max_drawdown = 0
        
        # Trading frequency
        if len(closed_trades) > 1:
            time_span = (closed_trades['timestamp'].max() - closed_trades['timestamp'].min()).days
            trades_per_day = len(closed_trades) / max(time_span, 1)
        else:
            trades_per_day = 0
        
        # Instrument analysis
        instrument_stats = closed_trades.groupby('instrument')['pnl'].agg([
            'count', 'sum', 'mean', 'std'
        ]).round(4)
        
        metrics = {
            'summary': {
                'total_trades': total_trades,
                'closed_trades': len(closed_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'win_rate_pct': win_rate * 100,
            },
            'pnl': {
                'total_pnl': total_pnl,
                'gross_profit': gross_profit,
                'gross_loss': gross_loss,
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'max_win': max_win,
                'max_loss': max_loss,
            },
            'portfolio': {
                'total_return': total_return,
                'total_return_pct': total_return * 100,
                'max_drawdown': max_drawdown,
                'max_drawdown_pct': max_drawdown * 100,
            },
            'activity': {
                'trades_per_day': trades_per_day,
                'risk_events': len(self.risk_events),
            },
            'instruments': instrument_stats.to_dict('index') if not instrument_stats.empty else {},
            'analysis_timestamp': datetime.now().isoformat(),
        }
        
        self.performance_metrics = metrics
        return metrics
    
    def _calculate_backtest_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics from backtest results."""
        if not results:
            return {"error": "No backtest results found"}
        
        # Aggregate results from multiple backtests
        aggregate_metrics = {
            'total_backtests': len(results),
            'backtest_summaries': {},
            'average_metrics': {},
        }
        
        # Collect metrics from each backtest
        all_returns = []
        all_win_rates = []
        all_profit_factors = []
        
        for name, data in results.items():
            if 'analysis' in data:
                analysis = data['analysis']
                
                # Extract key metrics
                total_return = analysis.get('summary', {}).get('total_return_pct', 0)
                win_rate = analysis.get('trades', {}).get('win_rate_pct', 0)
                
                all_returns.append(total_return)
                all_win_rates.append(win_rate)
                
                # Store summary
                aggregate_metrics['backtest_summaries'][name] = {
                    'total_return_pct': total_return,
                    'win_rate_pct': win_rate,
                    'total_trades': analysis.get('trades', {}).get('total_trades', 0),
                }
        
        # Calculate averages
        if all_returns:
            aggregate_metrics['average_metrics'] = {
                'avg_return_pct': np.mean(all_returns),
                'avg_win_rate_pct': np.mean(all_win_rates),
                'return_std': np.std(all_returns),
                'win_rate_std': np.std(all_win_rates),
                'best_return_pct': max(all_returns),
                'worst_return_pct': min(all_returns),
            }
        
        return aggregate_metrics
    
    def generate_performance_charts(self) -> None:
        """Generate comprehensive performance charts."""
        self.logger.info("Generating performance charts...")
        
        try:
            # Create charts directory
            charts_dir = self.output_dir / "charts"
            charts_dir.mkdir(exist_ok=True)
            
            # 1. Portfolio value chart
            if self.portfolio_snapshots:
                self._create_portfolio_chart(charts_dir)
            
            # 2. P&L distribution chart
            if self.trades:
                self._create_pnl_distribution_chart(charts_dir)
            
            # 3. Trade frequency chart
            if self.trades:
                self._create_trade_frequency_chart(charts_dir)
            
            # 4. Risk events chart
            if self.risk_events:
                self._create_risk_events_chart(charts_dir)
            
            # 5. Performance metrics dashboard
            self._create_performance_dashboard(charts_dir)
            
            self.logger.info(f"Charts saved to {charts_dir}")
            
        except Exception as e:
            self.logger.error(f"Error generating charts: {e}")
    
    def _create_portfolio_chart(self, charts_dir: Path) -> None:
        """Create portfolio value over time chart."""
        df = pd.DataFrame(self.portfolio_snapshots)
        df = df.sort_values('timestamp')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['portfolio_value'],
            mode='lines',
            name='Portfolio Value',
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Value Over Time',
            xaxis_title='Time',
            yaxis_title='Portfolio Value ($)',
            showlegend=True,
            height=400
        )
        
        fig.write_html(charts_dir / "portfolio_value.html")
    
    def _create_pnl_distribution_chart(self, charts_dir: Path) -> None:
        """Create P&L distribution chart."""
        closed_trades = [t for t in self.trades if t['action'] == 'closed']
        
        if not closed_trades:
            return
        
        pnl_values = [t['pnl'] for t in closed_trades]
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=pnl_values,
            nbinsx=20,
            name='P&L Distribution',
            marker_color='green'
        ))
        
        fig.update_layout(
            title='P&L Distribution',
            xaxis_title='P&L ($)',
            yaxis_title='Frequency',
            showlegend=False,
            height=400
        )
        
        fig.write_html(charts_dir / "pnl_distribution.html")
    
    def _create_trade_frequency_chart(self, charts_dir: Path) -> None:
        """Create trade frequency over time chart."""
        df = pd.DataFrame(self.trades)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        daily_trades = df.groupby('date').size()
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=daily_trades.index,
            y=daily_trades.values,
            name='Trades per Day',
            marker_color='orange'
        ))
        
        fig.update_layout(
            title='Trading Frequency',
            xaxis_title='Date',
            yaxis_title='Number of Trades',
            showlegend=False,
            height=400
        )
        
        fig.write_html(charts_dir / "trade_frequency.html")
    
    def _create_risk_events_chart(self, charts_dir: Path) -> None:
        """Create risk events timeline chart."""
        df = pd.DataFrame(self.risk_events)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        daily_events = df.groupby('date').size()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_events.index,
            y=daily_events.values,
            mode='markers+lines',
            name='Risk Events',
            marker=dict(color='red', size=8),
            line=dict(color='red')
        ))
        
        fig.update_layout(
            title='Risk Events Over Time',
            xaxis_title='Date',
            yaxis_title='Number of Events',
            showlegend=False,
            height=400
        )
        
        fig.write_html(charts_dir / "risk_events.html")
    
    def _create_performance_dashboard(self, charts_dir: Path) -> None:
        """Create comprehensive performance dashboard."""
        if not self.performance_metrics:
            return
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Win Rate & Profit Factor',
                'P&L Summary', 
                'Trading Activity',
                'Risk Metrics'
            ],
            specs=[[{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        metrics = self.performance_metrics
        
        # Win Rate indicator
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=metrics['summary']['win_rate_pct'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Win Rate (%)"},
            gauge={'axis': {'range': [None, 100]},
                  'bar': {'color': "darkblue"},
                  'bgcolor': "white",
                  'borderwidth': 2,
                  'bordercolor': "gray",
                  'steps': [{'range': [0, 50], 'color': 'lightgray'},
                           {'range': [50, 80], 'color': 'yellow'},
                           {'range': [80, 100], 'color': 'green'}]}
        ), row=1, col=1)
        
        # P&L bars
        pnl_data = metrics['pnl']
        fig.add_trace(go.Bar(
            x=['Gross Profit', 'Gross Loss', 'Net P&L'],
            y=[pnl_data['gross_profit'], pnl_data['gross_loss'], pnl_data['total_pnl']],
            marker_color=['green', 'red', 'blue']
        ), row=1, col=2)
        
        # Trading activity
        activity_data = metrics['summary']
        fig.add_trace(go.Bar(
            x=['Total Trades', 'Winning', 'Losing'],
            y=[activity_data['total_trades'], activity_data['winning_trades'], activity_data['losing_trades']],
            marker_color=['blue', 'green', 'red']
        ), row=2, col=1)
        
        # Drawdown indicator
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=abs(metrics['portfolio']['max_drawdown_pct']),
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Max Drawdown (%)"},
            gauge={'axis': {'range': [0, 50]},
                  'bar': {'color': "red"},
                  'bgcolor': "white",
                  'borderwidth': 2,
                  'bordercolor': "gray",
                  'steps': [{'range': [0, 10], 'color': 'lightgreen'},
                           {'range': [10, 25], 'color': 'yellow'},
                           {'range': [25, 50], 'color': 'lightcoral'}]}
        ), row=2, col=2)
        
        fig.update_layout(
            title_text="Performance Dashboard",
            showlegend=False,
            height=600
        )
        
        fig.write_html(charts_dir / "performance_dashboard.html")
    
    def generate_report(self, format: str = "html") -> Path:
        """
        Generate comprehensive analysis report.
        
        Args:
            format: Report format ('html', 'json', 'txt')
            
        Returns:
            Path to generated report
        """
        self.logger.info(f"Generating {format} report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "html":
            return self._generate_html_report(timestamp)
        elif format == "json":
            return self._generate_json_report(timestamp)
        elif format == "txt":
            return self._generate_text_report(timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_html_report(self, timestamp: str) -> Path:
        """Generate HTML report."""
        report_file = self.output_dir / f"analysis_report_{timestamp}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Trading Bot Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; color: #333; }}
                .section {{ margin: 20px 0; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Trading Bot Analysis Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Performance Summary</h2>
                {self._format_metrics_html()}
            </div>
            
            <div class="section">
                <h2>Trade Analysis</h2>
                {self._format_trades_html()}
            </div>
            
            <div class="section">
                <h2>Risk Events</h2>
                {self._format_risk_events_html()}
            </div>
        </body>
        </html>
        """
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report saved to {report_file}")
        return report_file
    
    def _format_metrics_html(self) -> str:
        """Format metrics for HTML display."""
        if not self.performance_metrics:
            return "<p>No performance metrics available</p>"
        
        metrics = self.performance_metrics
        
        html = f"""
        <div class="metric">
            <h3>Trading Performance</h3>
            <p>Total Trades: {metrics['summary']['total_trades']}</p>
            <p>Win Rate: {metrics['summary']['win_rate_pct']:.2f}%</p>
            <p>Total P&L: ${metrics['pnl']['total_pnl']:.2f}</p>
        </div>
        
        <div class="metric">
            <h3>Portfolio Performance</h3>
            <p>Total Return: {metrics['portfolio']['total_return_pct']:.2f}%</p>
            <p>Max Drawdown: {metrics['portfolio']['max_drawdown_pct']:.2f}%</p>
        </div>
        """
        
        return html
    
    def _format_trades_html(self) -> str:
        """Format trades for HTML display."""
        if not self.trades:
            return "<p>No trades found</p>"
        
        # Show recent trades
        recent_trades = sorted(self.trades, key=lambda x: x['timestamp'], reverse=True)[:10]
        
        html = "<table><tr><th>Timestamp</th><th>Action</th><th>Instrument</th><th>Side</th><th>P&L</th></tr>"
        
        for trade in recent_trades:
            html += f"""
            <tr>
                <td>{trade['timestamp']}</td>
                <td>{trade['action']}</td>
                <td>{trade['instrument']}</td>
                <td>{trade['side']}</td>
                <td>${trade['pnl']:.2f}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _format_risk_events_html(self) -> str:
        """Format risk events for HTML display."""
        if not self.risk_events:
            return "<p>No risk events found</p>"
        
        html = "<table><tr><th>Timestamp</th><th>Violation</th></tr>"
        
        for event in self.risk_events[-10:]:  # Show last 10 events
            html += f"""
            <tr>
                <td>{event['timestamp']}</td>
                <td>{event['violation']}</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_json_report(self, timestamp: str) -> Path:
        """Generate JSON report."""
        report_file = self.output_dir / f"analysis_report_{timestamp}.json"
        
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'analyzer_version': '2.0.0',
            },
            'performance_metrics': self.performance_metrics,
            'trades': self.trades,
            'portfolio_snapshots': self.portfolio_snapshots,
            'risk_events': self.risk_events,
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"JSON report saved to {report_file}")
        return report_file
    
    def _generate_text_report(self, timestamp: str) -> Path:
        """Generate text report."""
        report_file = self.output_dir / f"analysis_report_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write("BINANCE FUTURES TESTNET BOT - ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Generated: {datetime.now()}\n\n")
            
            if self.performance_metrics:
                metrics = self.performance_metrics
                
                f.write("PERFORMANCE SUMMARY\n")
                f.write("-" * 20 + "\n")
                f.write(f"Total Trades:        {metrics['summary']['total_trades']}\n")
                f.write(f"Win Rate:            {metrics['summary']['win_rate_pct']:.2f}%\n")
                f.write(f"Total P&L:           ${metrics['pnl']['total_pnl']:.2f}\n")
                f.write(f"Total Return:        {metrics['portfolio']['total_return_pct']:.2f}%\n")
                f.write(f"Max Drawdown:        {metrics['portfolio']['max_drawdown_pct']:.2f}%\n")
                f.write(f"Profit Factor:       {metrics['pnl']['profit_factor']:.2f}\n\n")
            
            f.write(f"DATA SUMMARY\n")
            f.write("-" * 12 + "\n")
            f.write(f"Trades Analyzed:     {len(self.trades)}\n")
            f.write(f"Portfolio Snapshots: {len(self.portfolio_snapshots)}\n")
            f.write(f"Risk Events:         {len(self.risk_events)}\n\n")
        
        self.logger.info(f"Text report saved to {report_file}")
        return report_file


async def main():
    """Main entry point for results analyzer."""
    parser = argparse.ArgumentParser(description="Analyze trading bot results")
    
    parser.add_argument("--log-file", type=str, help="Path to log file to analyze")
    parser.add_argument("--backtest-results", type=str, help="Path to backtest results directory")
    parser.add_argument("--output", type=str, help="Output directory for reports")
    parser.add_argument("--format", choices=["html", "json", "txt"], default="html", help="Report format")
    parser.add_argument("--generate-charts", action="store_true", help="Generate performance charts")
    
    args = parser.parse_args()
    
    # Create analyzer
    output_dir = Path(args.output) if args.output else None
    analyzer = ResultsAnalyzer(output_dir)
    
    try:
        # Analyze data sources
        if args.log_file:
            log_path = Path(args.log_file)
            metrics = analyzer.analyze_log_file(log_path)
            print(f"Log file analysis complete: {metrics.get('summary', {}).get('total_trades', 0)} trades")
        
        if args.backtest_results:
            results_path = Path(args.backtest_results)
            metrics = analyzer.analyze_backtest_results(results_path)
            print(f"Backtest analysis complete: {metrics.get('total_backtests', 0)} result sets")
        
        # Generate charts
        if args.generate_charts:
            analyzer.generate_performance_charts()
            print("Performance charts generated")
        
        # Generate report
        report_path = analyzer.generate_report(args.format)
        print(f"Report generated: {report_path}")
        
        # Print summary
        if analyzer.performance_metrics:
            metrics = analyzer.performance_metrics
            print("\n" + "=" * 40)
            print("ANALYSIS SUMMARY")
            print("=" * 40)
            print(f"Total Trades: {metrics['summary']['total_trades']}")
            print(f"Win Rate: {metrics['summary']['win_rate_pct']:.2f}%")
            print(f"Total P&L: ${metrics['pnl']['total_pnl']:.2f}")
            print(f"Total Return: {metrics['portfolio']['total_return_pct']:.2f}%")
            print("=" * 40)
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    exit(exit_code)
