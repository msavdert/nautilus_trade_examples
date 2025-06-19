#!/usr/bin/env python3
"""
Data Download and Conversion Utilities

This script provides utilities to:
1. Download sample data from Yahoo Finance
2. Convert HistData format to NautilusTrader format
3. Validate CSV files
"""

import os
import sys
from io import StringIO
from pathlib import Path

import pandas as pd
import requests


def download_yahoo_data(symbol: str = "EURUSD=X", period: str = "7d", interval: str = "1m"):
    """
    Download data from Yahoo Finance.
    
    Parameters:
    -----------
    symbol : str
        Yahoo Finance symbol (e.g., "EURUSD=X", "GBPUSD=X")
    period : str
        Period to download ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
    interval : str
        Data interval ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo")
    """
    try:
        import yfinance as yf
    except ImportError:
        print("❌ yfinance not installed. Install with: pip install yfinance")
        return None
    
    print(f"📥 Downloading {symbol} data from Yahoo Finance...")
    print(f"   Period: {period}, Interval: {interval}")
    
    try:
        # Download data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            print("❌ No data received")
            return None
        
        # Convert to required format
        data.reset_index(inplace=True)
        
        # Handle different datetime column names
        datetime_col = None
        for col in ["Datetime", "Date"]:
            if col in data.columns:
                datetime_col = col
                break
        
        if datetime_col is None:
            print("❌ No datetime column found")
            return None
            
        data["timestamp_utc"] = data[datetime_col].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Select and rename columns
        result = data[["timestamp_utc", "Open", "High", "Low", "Close", "Volume"]].copy()
        result.columns = ["timestamp_utc", "open", "high", "low", "close", "volume"]
        
        # Remove NaN values
        result = result.dropna()
        
        print(f"✅ Downloaded {len(result)} bars")
        print(f"📊 Range: {result['timestamp_utc'].min()} to {result['timestamp_utc'].max()}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return None


def download_alpha_vantage_data(from_symbol: str, to_symbol: str, api_key: str, interval: str = "1min"):
    """
    Download forex data from Alpha Vantage.
    
    Parameters:
    -----------
    from_symbol : str
        Base currency (e.g., "EUR")
    to_symbol : str
        Quote currency (e.g., "USD")
    api_key : str
        Alpha Vantage API key
    interval : str
        Data interval ("1min", "5min", "15min", "30min", "60min")
    """
    print(f"📥 Downloading {from_symbol}/{to_symbol} from Alpha Vantage...")
    
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'FX_INTRADAY',
        'from_symbol': from_symbol,
        'to_symbol': to_symbol,
        'interval': interval,
        'apikey': api_key,
        'datatype': 'csv'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Parse CSV response
        data = pd.read_csv(StringIO(response.text))
        
        if "Error Message" in data.columns or len(data.columns) < 5:
            print("❌ API error or invalid response")
            print("Check your API key and parameters")
            return None
        
        # Convert to required format
        data["timestamp_utc"] = pd.to_datetime(data["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
        
        result = data[["timestamp_utc", "open", "high", "low", "close"]].copy()
        result["volume"] = 100  # Dummy volume for forex
        
        result = result.dropna()
        result = result.sort_values("timestamp_utc")
        
        print(f"✅ Downloaded {len(result)} bars")
        return result
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return None


def convert_histdata_format(input_file: str, output_file: str):
    """
    Convert HistData.com format to NautilusTrader format.
    
    HistData format: YYYYMMDD HHMMSSMMM,bid_price,ask_price
    NautilusTrader format: timestamp_utc;open;high;low;close;volume
    """
    print(f"🔄 Converting HistData format: {input_file} -> {output_file}")
    
    try:
        # Read HistData CSV
        df = pd.read_csv(input_file, header=None, names=['timestamp', 'bid', 'ask'])
        
        print(f"📖 Loaded {len(df)} tick records")
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d %H%M%S%f')
        
        # Calculate mid price
        df['mid'] = (df['bid'] + df['ask']) / 2
        
        # Create OHLC bars by resampling to 1-minute intervals
        df.set_index('timestamp', inplace=True)
        ohlc = df['mid'].resample('1min').ohlc()
        ohlc['volume'] = 100  # Dummy volume
        
        # Remove any empty periods
        ohlc = ohlc.dropna()
        
        # Format for NautilusTrader
        ohlc.reset_index(inplace=True)
        ohlc['timestamp_utc'] = ohlc['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        result = ohlc[['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save to CSV
        result.to_csv(output_file, sep=';', index=False)
        
        print(f"✅ Converted to {len(result)} 1-minute bars")
        print(f"📊 Range: {result['timestamp_utc'].min()} to {result['timestamp_utc'].max()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error converting data: {e}")
        return False


def validate_csv_format(csv_file: str):
    """
    Validate CSV file format for NautilusTrader.
    
    Parameters:
    -----------
    csv_file : str
        Path to CSV file to validate
    """
    print(f"🔍 Validating CSV format: {csv_file}")
    
    try:
        df = pd.read_csv(csv_file, sep=';')
        
        # Check required columns
        required_columns = ['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
            return False
        
        # Check data types
        try:
            pd.to_datetime(df['timestamp_utc'])
        except:
            print("❌ Invalid timestamp format")
            return False
        
        # Check for numeric columns
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                print(f"❌ Column '{col}' is not numeric")
                return False
        
        # Check for missing values
        if df.isnull().any().any():
            print("⚠️  Warning: Data contains missing values")
        
        print(f"✅ CSV format is valid")
        print(f"📊 {len(df)} rows, Range: {df['timestamp_utc'].min()} to {df['timestamp_utc'].max()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating CSV: {e}")
        return False


def main():
    """Main function with command-line interface."""
    if len(sys.argv) < 2:
        print("📋 Data Download and Conversion Utilities")
        print("\nUsage:")
        print("  python download_data.py yahoo [symbol] [period] [interval]")
        print("  python download_data.py alphavantage [from_symbol] [to_symbol] [api_key]")
        print("  python download_data.py convert [input_file] [output_file]")
        print("  python download_data.py validate [csv_file]")
        print("\nExamples:")
        print("  python download_data.py yahoo EURUSD=X 7d 1m")
        print("  python download_data.py alphavantage EUR USD your_api_key")
        print("  python download_data.py convert histdata_raw.csv data/EURUSD_1min.csv")
        print("  python download_data.py validate data/EURUSD_1min.csv")
        return
    
    command = sys.argv[1].lower()
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    if command == "yahoo":
        symbol = sys.argv[2] if len(sys.argv) > 2 else "EURUSD=X"
        period = sys.argv[3] if len(sys.argv) > 3 else "7d"
        interval = sys.argv[4] if len(sys.argv) > 4 else "1m"
        
        data = download_yahoo_data(symbol, period, interval)
        if data is not None:
            output_file = f"data/{symbol.replace('=X', '').replace('/', '')}_{interval}.csv"
            data.to_csv(output_file, sep=';', index=False)
            print(f"💾 Saved to: {output_file}")
    
    elif command == "alphavantage":
        if len(sys.argv) < 5:
            print("❌ Alpha Vantage requires: from_symbol to_symbol api_key")
            return
        
        from_symbol = sys.argv[2]
        to_symbol = sys.argv[3]
        api_key = sys.argv[4]
        
        data = download_alpha_vantage_data(from_symbol, to_symbol, api_key)
        if data is not None:
            output_file = f"data/{from_symbol}{to_symbol}_1min.csv"
            data.to_csv(output_file, sep=';', index=False)
            print(f"💾 Saved to: {output_file}")
    
    elif command == "convert":
        if len(sys.argv) < 4:
            print("❌ Convert requires: input_file output_file")
            return
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        convert_histdata_format(input_file, output_file)
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("❌ Validate requires: csv_file")
            return
        
        csv_file = sys.argv[2]
        validate_csv_format(csv_file)
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
