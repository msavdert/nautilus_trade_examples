#!/usr/bin/env python3
"""
Setup script for the One-Three-Melih Trading Bot
================================================

This script handles installation and setup of the trading bot package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README_EN.md").read_text()

# Read requirements
requirements = [
    "nautilus_trader>=1.218.0",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "pyarrow>=12.0.0",
    "asyncio-mqtt>=0.16.0",
    "uvloop>=0.19.0",
]

dev_requirements = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

backtest_requirements = [
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "plotly>=5.15.0",
]

live_requirements = [
    "ccxt>=4.0.0",
    "websockets>=11.0.0",
    "redis>=4.6.0",
]

setup(
    name="one-three-melih-bot",
    version="1.0.0",
    description="Advanced Step-Back Risk Management EUR/USD Trading Bot using Nautilus Trader",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Melih Savdert",
    author_email="melih@example.com",
    url="https://github.com/melihsavdert/one-three-melih-bot",
    packages=find_packages(),
    py_modules=[
        "one_three_melih_strategy",
        "main",
        "run_backtest",
        "utils",
        "analyze_results",
        "test_strategy",
    ],
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "backtest": backtest_requirements,
        "live": live_requirements,
        "all": dev_requirements + backtest_requirements + live_requirements,
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="trading forex algorithmic-trading nautilus-trader risk-management",
    entry_points={
        "console_scripts": [
            "one-three-melih=main:main",
            "one-three-melih-backtest=run_backtest:main",
            "one-three-melih-analyze=analyze_results:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
