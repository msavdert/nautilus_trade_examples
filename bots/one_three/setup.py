#!/usr/bin/env python3
"""
Setup and Installation Script for One-Three Risk Management Bot
==============================================================

This script helps set up the One-Three trading bot environment,
install dependencies, and verify the installation.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is supported")
    return True


def install_dependencies():
    """Install required dependencies."""
    commands = [
        ("pip install --upgrade pip", "Upgrading pip"),
        ("pip install -r requirements.txt", "Installing dependencies"),
    ]
    
    for command, description in commands:
        if not run_command(command, description):
            return False
    return True


def verify_installation():
    """Verify that key components can be imported."""
    print("🔍 Verifying installation...")
    
    try:
        import nautilus_trader
        print(f"✅ Nautilus Trader {nautilus_trader.__version__} installed")
    except ImportError:
        print("❌ Nautilus Trader not found")
        return False
    
    try:
        import pandas as pd
        print(f"✅ Pandas {pd.__version__} installed")
    except ImportError:
        print("❌ Pandas not found")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy {np.__version__} installed")
    except ImportError:
        print("❌ NumPy not found")
        return False
    
    try:
        import matplotlib
        print(f"✅ Matplotlib {matplotlib.__version__} installed")
    except ImportError:
        print("❌ Matplotlib not found")
        return False
    
    return True


def setup_directories():
    """Create necessary directories."""
    directories = ['logs', 'data', 'results']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory '{directory}' created/verified")


def make_scripts_executable():
    """Make Python scripts executable on Unix systems."""
    if os.name != 'nt':  # Not Windows
        scripts = [
            'main.py',
            'run_backtest.py', 
            'run_live.py',
            'analyze_results.py',
            'test_strategy.py'
        ]
        
        for script in scripts:
            if Path(script).exists():
                os.chmod(script, 0o755)
                print(f"✅ Made {script} executable")


def run_quick_test():
    """Run a quick test to verify everything works."""
    print("🧪 Running quick verification test...")
    
    try:
        # Import our main modules
        from one_three_strategy import OneThreeBot, OneThreeConfig
        from utils import RiskCalculator, PerformanceTracker
        
        # Create a simple config
        config = OneThreeConfig()
        strategy = OneThreeBot(config=config)
        
        print("✅ Strategy components imported successfully")
        
        # Test utilities
        risk_calc = RiskCalculator(100_000)
        tracker = PerformanceTracker()
        
        print("✅ Utility components working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Verification test failed: {e}")
        return False


def main():
    """Main setup function."""
    print("🚀 One-Three Risk Management Bot Setup")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        sys.exit(1)
    
    # Verify installation
    if not verify_installation():
        print("\n❌ Installation verification failed")
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Make scripts executable
    make_scripts_executable()
    
    # Run quick test
    if not run_quick_test():
        print("\n❌ Quick test failed")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print()
    print("📚 Next steps:")
    print("   1. Review the README files for detailed instructions")
    print("   2. Run a demo: python main.py --mode demo")
    print("   3. Run a backtest: python main.py --mode backtest")
    print("   4. Configure for live trading (see README)")
    print()
    print("✅ The One-Three bot is ready to use!")


if __name__ == "__main__":
    main()
