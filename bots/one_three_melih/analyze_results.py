#!/usr/bin/env python3
"""
Results analysis and visualization for One-Three-Melih Trading Bot
==================================================================

This module provides comprehensive analysis tools for trading results,
including statistical analysis, performance metrics, and visualization.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from utils import PerformanceAnalyzer, BalanceCalculator


class ResultsAnalyzer:
    """Comprehensive analysis of trading bot results."""
    
    def __init__(self, results_file: Optional[str] = None):
        """
        Initialize the results analyzer.
        
        Args:
            results_file: Path to JSON results file
        """
        self.logger = logging.getLogger(__name__)
        self.performance_analyzer = PerformanceAnalyzer()
        self.balance_calculator = BalanceCalculator()
        
        if results_file and Path(results_file).exists():
            self.load_results(results_file)
        else:
            self.results = None
    
    def load_results(self, file_path: str) -> None:
        """Load results from JSON file."""
        try:
            with open(file_path, 'r') as f:
                self.results = json.load(f)
            self.logger.info(f"Results loaded from {file_path}")
        except Exception as e:
            self.logger.error(f"Error loading results: {e}")
            self.results = None
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report."""
        if not self.results:
            return {"error": "No results loaded"}
        
        report = {
            "summary": self.generate_summary(),
            "performance_metrics": self.calculate_performance_metrics(),
            "risk_analysis": self.analyze_risk_metrics(),
            "balance_analysis": self.analyze_balance_progression(),
            "recommendations": self.generate_recommendations(),
        }
        
        return report
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary."""
        balance = self.results["balance_performance"]
        trading = self.results["trading_statistics"]
        
        return {
            "initial_balance": balance["initial_balance"],
            "final_balance": balance["final_balance"],
            "total_return_pct": balance["total_return_pct"],
            "total_trades": trading["total_trades"],
            "win_rate_pct": trading["win_rate_pct"],
            "max_step_reached": balance["max_step_reached"],
            "strategy_effectiveness": self.assess_strategy_effectiveness(),
        }
    
    def calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate detailed performance metrics."""
        balance = self.results["balance_performance"]
        trading = self.results["trading_statistics"]
        risk = self.results["risk_metrics"]
        
        # Calculate returns series
        balance_history = balance["balance_history"]
        returns = []
        for i in range(1, len(balance_history)):
            ret = (balance_history[i] - balance_history[i-1]) / balance_history[i-1]
            returns.append(ret)
        
        # Performance metrics
        metrics = {
            "sharpe_ratio": self.performance_analyzer.calculate_sharpe_ratio(returns),
            "max_drawdown": self.performance_analyzer.calculate_max_drawdown(balance_history),
            "profit_factor": risk["profit_factor"],
            "total_return_pct": balance["total_return_pct"],
            "annualized_return": self.calculate_annualized_return(balance_history),
            "volatility": np.std(returns) * 100 if returns else 0,
            "win_loss_ratio": risk["avg_win"] / max(risk["avg_loss"], 0.01),
        }
        
        return metrics
    
    def analyze_risk_metrics(self) -> Dict[str, Any]:
        """Analyze risk characteristics."""
        balance = self.results["balance_performance"]
        trading = self.results["trading_statistics"]
        risk = self.results["risk_metrics"]
        
        risk_analysis = {
            "max_consecutive_losses": trading["max_consecutive_losses"],
            "max_drawdown_steps": risk["max_drawdown_steps"],
            "risk_rating": self.assess_risk_level(),
            "balance_volatility": self.calculate_balance_volatility(),
            "recovery_analysis": self.analyze_recovery_patterns(),
        }
        
        return risk_analysis
    
    def analyze_balance_progression(self) -> Dict[str, Any]:
        """Analyze balance progression patterns."""
        balance_history = self.results["balance_performance"]["balance_history"]
        
        # Step analysis
        step_changes = []
        for i in range(1, len(balance_history)):
            change = balance_history[i] - balance_history[i-1]
            step_changes.append(change)
        
        # Progression patterns
        ups = [c for c in step_changes if c > 0]
        downs = [c for c in step_changes if c < 0]
        
        analysis = {
            "total_steps": len(balance_history) - 1,
            "upward_steps": len(ups),
            "downward_steps": len(downs),
            "avg_step_up": np.mean(ups) if ups else 0,
            "avg_step_down": np.mean(downs) if downs else 0,
            "step_efficiency": len(ups) / max(len(step_changes), 1) * 100,
            "balance_progression_trend": self.analyze_progression_trend(balance_history),
        }
        
        return analysis
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        performance = self.calculate_performance_metrics()
        trading = self.results["trading_statistics"]
        balance = self.results["balance_performance"]
        
        # Win rate recommendations
        if trading["win_rate_pct"] < 45:
            recommendations.append("Consider improving entry signals or market timing to increase win rate above 50%")
        elif trading["win_rate_pct"] > 70:
            recommendations.append("Excellent win rate - consider testing with larger position sizes or different markets")
        
        # Return recommendations
        if balance["total_return_pct"] < 0:
            recommendations.append("Strategy shows negative returns - reconsider parameters or market conditions")
        elif balance["total_return_pct"] > 100:
            recommendations.append("Strong performance - consider scaling up with proper risk management")
        
        # Risk recommendations
        if performance["max_drawdown"]["max_drawdown_pct"] > 50:
            recommendations.append("High maximum drawdown detected - consider implementing additional risk controls")
        
        # Sharpe ratio recommendations
        if performance["sharpe_ratio"] < 1.0:
            recommendations.append("Low risk-adjusted returns - consider optimizing risk-reward ratios")
        elif performance["sharpe_ratio"] > 2.0:
            recommendations.append("Excellent risk-adjusted returns - strategy shows strong potential")
        
        # Step progression recommendations
        max_step = balance["max_step_reached"]
        if max_step < 3:
            recommendations.append("Low step progression - strategy may benefit from improved consistency")
        elif max_step > 5:
            recommendations.append("High step progression achieved - monitor for sustainability")
        
        return recommendations
    
    def assess_strategy_effectiveness(self) -> str:
        """Assess overall strategy effectiveness."""
        balance = self.results["balance_performance"]
        trading = self.results["trading_statistics"]
        risk = self.results["risk_metrics"]
        
        score = 0
        
        # Return component (40%)
        if balance["total_return_pct"] > 50:
            score += 40
        elif balance["total_return_pct"] > 20:
            score += 30
        elif balance["total_return_pct"] > 0:
            score += 20
        
        # Win rate component (30%)
        if trading["win_rate_pct"] > 60:
            score += 30
        elif trading["win_rate_pct"] > 50:
            score += 20
        elif trading["win_rate_pct"] > 40:
            score += 10
        
        # Risk component (30%)
        if risk["profit_factor"] > 2.0:
            score += 30
        elif risk["profit_factor"] > 1.5:
            score += 20
        elif risk["profit_factor"] > 1.0:
            score += 10
        
        if score >= 80:
            return "EXCELLENT"
        elif score >= 60:
            return "GOOD"
        elif score >= 40:
            return "AVERAGE"
        else:
            return "POOR"
    
    def assess_risk_level(self) -> str:
        """Assess overall risk level."""
        trading = self.results["trading_statistics"]
        risk = self.results["risk_metrics"]
        
        risk_factors = 0
        
        if trading["max_consecutive_losses"] > 5:
            risk_factors += 1
        if risk["max_drawdown_steps"] > 3:
            risk_factors += 1
        if risk["profit_factor"] < 1.2:
            risk_factors += 1
        
        if risk_factors == 0:
            return "LOW"
        elif risk_factors == 1:
            return "MODERATE"
        else:
            return "HIGH"
    
    def calculate_balance_volatility(self) -> float:
        """Calculate balance volatility."""
        balance_history = self.results["balance_performance"]["balance_history"]
        
        if len(balance_history) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(balance_history)):
            ret = (balance_history[i] - balance_history[i-1]) / balance_history[i-1]
            returns.append(ret)
        
        return np.std(returns) * 100
    
    def analyze_recovery_patterns(self) -> Dict[str, Any]:
        """Analyze recovery patterns after losses."""
        balance_history = self.results["balance_performance"]["balance_history"]
        
        # Find loss periods and subsequent recoveries
        losses = []
        recoveries = []
        
        peak = balance_history[0]
        in_drawdown = False
        drawdown_start_idx = 0
        
        for i, balance in enumerate(balance_history):
            if balance > peak:
                if in_drawdown:
                    # Recovery completed
                    recovery_time = i - drawdown_start_idx
                    recoveries.append(recovery_time)
                    in_drawdown = False
                peak = balance
            elif balance < peak and not in_drawdown:
                # Start of drawdown
                in_drawdown = True
                drawdown_start_idx = i
                losses.append((peak - balance) / peak * 100)
        
        return {
            "total_loss_periods": len(losses),
            "avg_recovery_time": np.mean(recoveries) if recoveries else 0,
            "max_recovery_time": max(recoveries) if recoveries else 0,
            "avg_loss_depth_pct": np.mean(losses) if losses else 0,
        }
    
    def analyze_progression_trend(self, balance_history: List[float]) -> str:
        """Analyze overall progression trend."""
        if len(balance_history) < 3:
            return "INSUFFICIENT_DATA"
        
        # Calculate linear trend
        x = np.arange(len(balance_history))
        y = np.array(balance_history)
        slope, _ = np.polyfit(x, y, 1)
        
        if slope > 1.0:
            return "STRONG_UPWARD"
        elif slope > 0.1:
            return "UPWARD"
        elif slope > -0.1:
            return "SIDEWAYS"
        elif slope > -1.0:
            return "DOWNWARD"
        else:
            return "STRONG_DOWNWARD"
    
    def calculate_annualized_return(self, balance_history: List[float]) -> float:
        """Calculate annualized return based on balance progression."""
        if len(balance_history) < 2:
            return 0.0
        
        initial = balance_history[0]
        final = balance_history[-1]
        periods = len(balance_history) - 1
        
        # Assume each period represents one trade (for annualization)
        # This is a simplified calculation
        total_return = (final - initial) / initial
        
        # Annualize assuming 250 trading days per year and average trade frequency
        trades_per_year = 250 / max(periods, 1)  # Simplified assumption
        annualized = ((1 + total_return) ** trades_per_year - 1) * 100
        
        return annualized
    
    def create_visualizations(self, output_dir: str = "charts") -> None:
        """Create comprehensive visualizations of results."""
        if not self.results:
            self.logger.error("No results to visualize")
            return
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. Balance progression chart
        self.plot_balance_progression(output_dir)
        
        # 2. Performance metrics dashboard
        self.plot_performance_dashboard(output_dir)
        
        # 3. Risk analysis charts
        self.plot_risk_analysis(output_dir)
        
        # 4. Trade distribution analysis
        self.plot_trade_distribution(output_dir)
        
        self.logger.info(f"Visualizations saved to {output_dir}")
    
    def plot_balance_progression(self, output_dir: str) -> None:
        """Plot balance progression over time."""
        balance_history = self.results["balance_performance"]["balance_history"]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Balance progression
        steps = range(len(balance_history))
        ax1.plot(steps, balance_history, 'b-', linewidth=2, marker='o', markersize=4)
        ax1.set_title('Balance Progression Over Time', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Step Number')
        ax1.set_ylabel('Balance ($)')
        ax1.grid(True, alpha=0.3)
        
        # Add annotations for key points
        max_balance = max(balance_history)
        max_idx = balance_history.index(max_balance)
        ax1.annotate(f'Peak: ${max_balance:.2f}', 
                    xy=(max_idx, max_balance), 
                    xytext=(max_idx + 1, max_balance + 10),
                    arrowprops=dict(arrowstyle='->', color='red'))
        
        # Returns per step
        returns = []
        for i in range(1, len(balance_history)):
            ret = (balance_history[i] - balance_history[i-1]) / balance_history[i-1] * 100
            returns.append(ret)
        
        step_returns = range(1, len(balance_history))
        colors = ['green' if r > 0 else 'red' for r in returns]
        ax2.bar(step_returns, returns, color=colors, alpha=0.7)
        ax2.set_title('Returns per Step', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Step Number')
        ax2.set_ylabel('Return (%)')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/balance_progression.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_performance_dashboard(self, output_dir: str) -> None:
        """Create performance metrics dashboard."""
        metrics = self.calculate_performance_metrics()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Key metrics
        metric_names = ['Total Return', 'Sharpe Ratio', 'Win Rate', 'Profit Factor']
        metric_values = [
            metrics['total_return_pct'],
            metrics['sharpe_ratio'],
            self.results['trading_statistics']['win_rate_pct'],
            metrics['profit_factor']
        ]
        
        colors = ['green', 'blue', 'orange', 'purple']
        bars = ax1.bar(metric_names, metric_values, color=colors, alpha=0.7)
        ax1.set_title('Key Performance Metrics', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Value')
        
        # Add value labels on bars
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.2f}', ha='center', va='bottom')
        
        # Drawdown analysis
        balance_history = self.results["balance_performance"]["balance_history"]
        peak = balance_history[0]
        drawdowns = []
        
        for balance in balance_history:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak * 100
            drawdowns.append(drawdown)
        
        ax2.fill_between(range(len(drawdowns)), drawdowns, 0, alpha=0.3, color='red')
        ax2.set_title('Drawdown Analysis', fontsize=12, fontweight='bold')
        ax2.set_xlabel('Step')
        ax2.set_ylabel('Drawdown (%)')
        ax2.invert_yaxis()
        
        # Risk metrics
        risk_metrics = ['Max Consecutive\nLosses', 'Max Drawdown\nSteps', 'Volatility']
        risk_values = [
            self.results['trading_statistics']['max_consecutive_losses'],
            self.results['risk_metrics']['max_drawdown_steps'],
            metrics['volatility']
        ]
        
        ax3.bar(risk_metrics, risk_values, color='red', alpha=0.6)
        ax3.set_title('Risk Metrics', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Value')
        
        # Win/Loss distribution
        wins = self.results['trading_statistics']['winning_trades']
        losses = self.results['trading_statistics']['losing_trades']
        
        ax4.pie([wins, losses], labels=['Wins', 'Losses'], autopct='%1.1f%%',
               colors=['green', 'red'], startangle=90)
        ax4.set_title('Win/Loss Distribution', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{output_dir}/performance_dashboard.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_risk_analysis(self, output_dir: str) -> None:
        """Create risk analysis visualizations."""
        # Implementation for risk analysis plots
        pass
    
    def plot_trade_distribution(self, output_dir: str) -> None:
        """Create trade distribution analysis."""
        # Implementation for trade distribution plots
        pass


def main():
    """Main function for results analysis."""
    # Load and analyze results
    analyzer = ResultsAnalyzer("backtest_results.json")
    
    if analyzer.results:
        # Generate comprehensive report
        report = analyzer.generate_comprehensive_report()
        
        # Save report
        with open("analysis_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Create visualizations
        analyzer.create_visualizations("analysis_charts")
        
        # Print summary
        print("RESULTS ANALYSIS COMPLETE")
        print("=" * 40)
        summary = report["summary"]
        print(f"Strategy Effectiveness: {summary['strategy_effectiveness']}")
        print(f"Total Return: {summary['total_return_pct']:.2f}%")
        print(f"Win Rate: {summary['win_rate_pct']:.1f}%")
        print(f"Max Step Reached: {summary['max_step_reached']}")
        
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")
    
    else:
        print("No results file found. Run a backtest first.")


if __name__ == "__main__":
    main()
