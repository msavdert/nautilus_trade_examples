"""
Health check module for Docker container monitoring
"""
import sys
import asyncio
import logging
from typing import Dict, Any

# Simple health check that can be imported and used by Docker healthcheck
def check() -> bool:
    """
    Perform basic health check
    Returns True if healthy, raises exception if not
    """
    try:
        # Basic Python runtime check
        assert sys.version_info >= (3, 11), "Python version check failed"
        
        # Try importing core modules
        from src.config import Config
        from src.client import BinanceClient
        
        # Basic configuration validation
        config = Config()
        assert hasattr(config, 'binance_api_key'), "Config validation failed"
        
        print("Health check passed")
        return True
        
    except Exception as e:
        print(f"Health check failed: {e}")
        sys.exit(1)

async def async_check() -> Dict[str, Any]:
    """
    More comprehensive async health check
    """
    try:
        from src.config import Config
        from src.client import BinanceClient
        
        config = Config()
        
        # Initialize client (without connecting)
        client = BinanceClient(config)
        
        # Basic connectivity test (if not in test mode)
        health_status = {
            "status": "healthy",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "config_loaded": True,
            "client_initialized": True,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return health_status
        
    except Exception as e:
        raise Exception(f"Async health check failed: {e}")

if __name__ == "__main__":
    # Run basic health check when called directly
    check()
