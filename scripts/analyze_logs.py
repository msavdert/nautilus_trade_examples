#!/usr/bin/env python3
"""
Log Analysis Tool for Nautilus Trading Bot
Enhanced with Nautilus Trader best practices
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import re


def analyze_json_logs(log_file: Path):
    """Analyze JSON formatted logs"""
    print(f"\n📊 Analyzing JSON logs: {log_file.name}")
    print("=" * 60)
    
    events = defaultdict(int)
    trading_events = []
    metrics = []
    
    try:
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Count events by type
                    if 'component' in log_entry:
                        events[log_entry['component']] += 1
                    
                    # Extract trading events
                    if 'TRADING_EVENT' in log_entry.get('message', ''):
                        try:
                            event_data = json.loads(log_entry['message'].split('TRADING_EVENT: ')[1])
                            trading_events.append(event_data)
                        except:
                            pass
                    
                    # Extract metrics
                    if 'METRIC' in log_entry.get('message', ''):
                        try:
                            metric_data = json.loads(log_entry['message'].split('METRIC: ')[1])
                            metrics.append(metric_data)
                        except:
                            pass
                            
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON on line {line_num}")
                    
    except FileNotFoundError:
        print(f"❌ File not found: {log_file}")
        return
    
    # Display results
    print(f"\n📈 Event Summary:")
    for component, count in sorted(events.items()):
        print(f"  {component}: {count} events")
    
    print(f"\n💰 Trading Events: {len(trading_events)}")
    for event in trading_events:
        event_type = event.get('event_type', 'unknown')
        timestamp = event.get('timestamp', 'unknown')
        print(f"  {timestamp}: {event_type}")
        if event_type == 'account_balance':
            print(f"    💳 {event.get('currency', 'N/A')}: {event.get('balance', 'N/A')}")
        elif event_type == 'bot_startup':
            print(f"    🚀 Instrument: {event.get('instrument', 'N/A')}")
    
    print(f"\n📊 Performance Metrics: {len(metrics)}")
    for metric in metrics:
        print(f"  {metric.get('metric_name', 'unknown')}: {metric.get('value', 'N/A')} {metric.get('unit', '')}")


def analyze_nautilus_logs(log_file: Path):
    """Analyze Nautilus Trader native JSON logs"""
    print(f"\n🚀 Analyzing Nautilus logs: {log_file.name}")
    print("=" * 60)
    
    components = defaultdict(int)
    levels = defaultdict(int)
    errors = []
    
    try:
        with open(log_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    log_entry = json.loads(line.strip())
                    
                    component = log_entry.get('component', 'unknown')
                    level = log_entry.get('level', 'unknown')
                    
                    components[component] += 1
                    levels[level] += 1
                    
                    # Collect errors and warnings
                    if level in ['ERROR', 'WARN']:
                        errors.append({
                            'level': level,
                            'component': component,
                            'message': log_entry.get('message', ''),
                            'timestamp': log_entry.get('timestamp', '')
                        })
                        
                except json.JSONDecodeError:
                    print(f"⚠️  Invalid JSON on line {line_num}")
                    
    except FileNotFoundError:
        print(f"❌ File not found: {log_file}")
        return
    
    # Display results
    print(f"\n📊 Log Level Summary:")
    for level, count in sorted(levels.items()):
        emoji = {"INFO": "ℹ️", "WARN": "⚠️", "ERROR": "❌", "DEBUG": "🐛"}.get(level, "📋")
        print(f"  {emoji} {level}: {count}")
    
    print(f"\n🔧 Component Activity:")
    for component, count in sorted(components.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {component}: {count} logs")
    
    print(f"\n⚠️  Errors and Warnings: {len(errors)}")
    for error in errors:
        print(f"  {error['level']} [{error['component']}]: {error['message'][:100]}...")


def get_log_stats(logs_dir: Path):
    """Get overall statistics about log files"""
    print(f"\n📁 Log Directory: {logs_dir}")
    print("=" * 60)
    
    log_files = list(logs_dir.glob("*.log")) + list(logs_dir.glob("*.json"))
    
    if not log_files:
        print("❌ No log files found")
        return
    
    total_size = 0
    for log_file in log_files:
        size = log_file.stat().st_size
        total_size += size
        modified = datetime.fromtimestamp(log_file.stat().st_mtime)
        
        print(f"📄 {log_file.name}")
        print(f"   Size: {size:,} bytes ({size/1024/1024:.2f} MB)")
        print(f"   Modified: {modified.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    print(f"💾 Total log size: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")


def main():
    parser = argparse.ArgumentParser(description="Analyze Nautilus Trading Bot Logs")
    parser.add_argument("--logs-dir", default="/workspace/logs", help="Log directory path")
    parser.add_argument("--file", help="Specific log file to analyze")
    parser.add_argument("--stats", action="store_true", help="Show log file statistics")
    
    args = parser.parse_args()
    
    logs_dir = Path(args.logs_dir)
    
    if args.stats:
        get_log_stats(logs_dir)
        return
    
    if args.file:
        log_file = Path(args.file)
        if not log_file.exists():
            log_file = logs_dir / args.file
        
        if log_file.suffix == '.json':
            if 'nautilus_bot' in log_file.name:
                analyze_nautilus_logs(log_file)
            else:
                analyze_json_logs(log_file)
        else:
            print(f"📄 Text log file: {log_file.name}")
            print("Use 'tail -f' or 'cat' to view text logs")
    else:
        # Analyze all logs
        get_log_stats(logs_dir)
        
        # Analyze custom JSON logs
        json_files = list(logs_dir.glob("bot_activity.json"))
        for json_file in json_files:
            analyze_json_logs(json_file)
        
        # Analyze Nautilus logs
        nautilus_files = list(logs_dir.glob("nautilus_bot_*.json"))
        for nautilus_file in nautilus_files:
            analyze_nautilus_logs(nautilus_file)


if __name__ == "__main__":
    main()
