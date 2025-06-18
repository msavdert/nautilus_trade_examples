# Nautilus Trader Logging Configuration Guide

This document provides a comprehensive guide to configuring logging in Nautilus Trader applications, including best practices, configuration options, and practical examples.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Configuration Options](#configuration-options)
4. [Log Levels](#log-levels)
5. [File Logging](#file-logging)
6. [Log Rotation](#log-rotation)
7. [Component Filtering](#component-filtering)
8. [Log Formats](#log-formats)
9. [LogGuard and Multi-Engine Applications](#logguard-and-multi-engine-applications)
10. [Best Practices](#best-practices)
11. [Examples](#examples)
12. [Troubleshooting](#troubleshooting)

## Overview

Nautilus Trader provides a high-performance logging system implemented in Rust with a Python interface. The logging system operates in a separate thread using a multi-producer single-consumer (MPSC) channel, ensuring optimal performance for your trading applications.

### Key Features

- **High Performance**: Logging operations run in a separate thread to avoid blocking the main trading logic
- **Flexible Output**: Support for both console (stdout/stderr) and file output
- **Log Rotation**: Automatic file rotation based on size or date
- **Component Filtering**: Filter logs by specific components (strategies, engines, etc.)
- **Multiple Formats**: Plain text or JSON formatting
- **Color Support**: ANSI color codes for enhanced readability in terminals

## Quick Start

Here's a minimal logging configuration for getting started:

```python
from nautilus_trader.config import LoggingConfig, TradingNodeConfig

# Basic logging configuration
logging_config = LoggingConfig(
    log_level="INFO",           # Console output level
    log_level_file="DEBUG",     # File output level
    log_directory="logs",       # Directory for log files
    log_colors=True            # Enable colors in console
)

# Use in your trading node configuration
config = TradingNodeConfig(
    trader_id="MY-BOT-001",
    logging=logging_config,
    # ... other configuration
)
```

## Configuration Options

The `LoggingConfig` class provides comprehensive control over logging behavior:

### Basic Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_level` | str | "INFO" | Minimum log level for console output |
| `log_level_file` | str \| None | None | Minimum log level for file output (None = no file logging) |
| `log_directory` | str \| None | None | Directory for log files (None = current working directory) |
| `log_colors` | bool | True | Enable ANSI color codes in console output |

### File Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_file_name` | str \| None | None | Custom log file name (overrides automatic naming) |
| `log_file_format` | str \| None | None | File format: "JSON" for JSON, None for plain text |
| `log_file_max_size` | int \| None | None | Maximum file size in bytes before rotation |
| `log_file_max_backup_count` | int | 5 | Maximum number of backup files to keep |

### Advanced Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_component_levels` | dict[str, str] \| None | None | Per-component log level overrides |
| `bypass_logging` | bool | False | Disable all logging |
| `print_config` | bool | False | Print logging configuration at startup |
| `use_pyo3` | bool | False | Use PyO3 bridge (slower, for debugging Rust components) |
| `clear_log_file` | bool | False | Truncate existing log file on startup |

## Log Levels

Nautilus Trader supports the following log levels (from most verbose to least verbose):

1. **TRACE** - Most detailed logs (only available from Rust components)
2. **DEBUG** - Detailed information for debugging
3. **INFO** - General information about application flow
4. **WARNING** - Warning messages for potentially problematic situations
5. **ERROR** - Error messages for failures and exceptions
6. **OFF** - Disable logging entirely

### Log Level Usage Guidelines

- **Production**: Use INFO or WARNING for console, DEBUG for files
- **Development**: Use DEBUG for console, DEBUG or TRACE for files
- **Testing**: Use WARNING for console to reduce noise
- **Debugging**: Use DEBUG or TRACE levels as needed

## File Logging

### Log File Location Strategy

**Recommendation: Use a dedicated `logs/` subdirectory within each bot project**

This approach provides several benefits:
- **Organization**: Keeps log files separate from source code
- **Clarity**: Makes it obvious where to find logs
- **Version Control**: Easy to add `logs/` to `.gitignore`
- **Deployment**: Simplifies log file management in production

### File Naming Conventions

Nautilus automatically generates meaningful file names based on your configuration:

#### Default Naming (with rotation)
```
{trader_id}_{YYYY-MM-DD_HHMMSS:mmm}_{instance_id}.{log|json}
```
Example: `MY-BOT-001_2024-03-15_143022:521_a1b2c3d4.log`

#### Default Naming (without rotation)
```
{trader_id}_{YYYY-MM-DD}_{instance_id}.{log|json}
```
Example: `MY-BOT-001_2024-03-15_a1b2c3d4.log`

#### Custom Naming
When you specify `log_file_name`:
- Without rotation: `my_custom_log.log`
- With rotation: `my_custom_log_2024-03-15_143022:521.log`

## Log Rotation

Log rotation helps manage disk space and organize historical logs:

### Size-Based Rotation
```python
logging_config = LoggingConfig(
    log_level_file="DEBUG",
    log_directory="logs",
    log_file_max_size=100_000_000,      # 100 MB
    log_file_max_backup_count=10         # Keep 10 backup files
)
```

### Date-Based Rotation (Default)
When no `log_file_max_size` is specified and default naming is used, files automatically rotate at midnight UTC, creating one file per day.

### Backup File Management
- The `log_file_max_backup_count` parameter controls how many rotated files to keep
- When the limit is exceeded, the oldest backup files are automatically deleted
- Default is 5 backup files

## Component Filtering

Filter logs by specific components to reduce noise and focus on relevant information:

```python
logging_config = LoggingConfig(
    log_level="INFO",
    log_level_file="DEBUG",
    log_component_levels={
        "Portfolio": "WARNING",      # Only warnings and errors from Portfolio
        "RiskEngine": "DEBUG",       # Debug level for RiskEngine
        "MyStrategy": "TRACE",       # Maximum detail for MyStrategy
        "DataEngine": "ERROR"        # Only errors from DataEngine
    }
)
```

Component names typically include:
- Strategy names (e.g., "MyFirstBot", "EMACrossStrategy")
- Engine components ("RiskEngine", "DataEngine", "ExecutionEngine")
- System components ("Portfolio", "OrderManager")

## Log Formats

### Plain Text Format (Default)
```
2024-03-15T14:30:22.521000000Z [INFO] MY-BOT-001.MyStrategy: Order filled: BUY 100000 EUR/USD @ 1.08950
```

### JSON Format
```python
logging_config = LoggingConfig(
    log_file_format="JSON"
)
```

JSON output:
```json
{
  "timestamp": "2024-03-15T14:30:22.521000000Z",
  "trader_id": "MY-BOT-001",
  "level": "INFO",
  "color": "NORMAL",
  "component": "MyStrategy",
  "message": "Order filled: BUY 100000 EUR/USD @ 1.08950"
}
```

JSON format is ideal for:
- Log aggregation systems (ELK Stack, Splunk)
- Automated log analysis
- Machine-readable log processing

## LogGuard and Multi-Engine Applications

When running multiple engines or backtests in the same process, use `LogGuard` to maintain logging consistency:

```python
from nautilus_trader.common.component import init_logging, Logger

# Initialize logging once at the application level
log_guard = init_logging()

# Keep the log_guard alive for the entire application lifecycle
# The logging system will remain active as long as log_guard exists

# For multiple backtest engines:
log_guard = None
for i in range(number_of_backtests):
    engine = setup_engine(...)
    
    # Get LogGuard from first engine
    if log_guard is None:
        log_guard = engine.get_log_guard()
    
    # Run backtest
    engine.run()
    engine.dispose()  # Safe to dispose engine, logging remains active
```

### Why LogGuard is Important

Without LogGuard, you may see errors like:
```
Error sending log event: [INFO] ...
```

This occurs because the logging system shuts down when the first engine is disposed, breaking logging for subsequent engines.

## Best Practices

### 1. Log File Storage Location

**Recommendation: Store logs in a `logs/` subdirectory under each bot project.**

**Rationale:**
- **Project Isolation**: Each bot maintains its own log history, making it easier to debug specific strategies
- **Development Workflow**: Logs stay with the code during development and testing
- **Container Deployment**: Easier to mount bot-specific log volumes in Docker
- **Backup and Archival**: Bot-specific logs can be backed up or archived independently
- **Multi-Bot Management**: When running multiple bots, logs don't interfere with each other

**Directory Structure:**
```
bots/
├── my-first-bot/
│   ├── main.py
│   ├── logs/           # ← Bot-specific logs here
│   │   ├── node-MY-FIRST-BOT-001.log
│   │   ├── node-MY-FIRST-BOT-001.log.1
│   │   └── ...
│   └── LOGGING.md
├── scalping-bot/
│   ├── strategy.py
│   ├── logs/           # ← Separate logs for this bot
│   └── ...
└── logs/               # ← Optional: shared logs or system-wide logs
```

**Alternative Approaches:**
- **Centralized Logging**: Use workspace root `/logs` for system-wide logging across all bots
- **Production Deployment**: Use `/var/log/trading/bot-name/` for production systems
- **Cloud Logging**: Stream logs to cloud services (CloudWatch, Stackdriver, etc.)

### 2. Project Structure
```
my-bot/
├── main.py
├── config.py
├── logs/              # Dedicated log directory
│   ├── .gitignore     # Exclude logs from version control
│   └── (log files)
└── README.md
```

### 3. Log Directory Configuration
```python
# Create logs directory if it doesn't exist
import os
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging_config = LoggingConfig(
    log_directory=log_dir,
    # ... other configuration
)
```

### 4. Environment-Specific Configuration
```python
import os

# Different log levels for different environments
log_level = os.getenv("LOG_LEVEL", "INFO")
log_level_file = os.getenv("LOG_LEVEL_FILE", "DEBUG")

logging_config = LoggingConfig(
    log_level=log_level,
    log_level_file=log_level_file,
    log_directory="logs"
)
```

### 5. Strategic Log Messages
```python
# Use appropriate log levels
self.log.info("🚀 Strategy starting")          # General information
self.log.debug(f"📊 Price: {price:.5f}")       # Detailed data
self.log.warning("⚠️ Low liquidity detected")   # Potential issues
self.log.error("❌ Order submission failed")    # Errors

# Use colors for visual distinction
self.log.info("✅ Position opened", color=LogColor.GREEN)
self.log.info("🔴 Position closed", color=LogColor.RED)
```

### 6. Performance Considerations
- Use appropriate log levels to avoid excessive logging
- Consider using DEBUG level for file logging in production
- Avoid string formatting in log calls that might not be written:
  ```python
  # Good: Lazy evaluation
  self.log.debug("Price data: %s", expensive_calculation())
  
  # Avoid: Always evaluates
  self.log.debug(f"Price data: {expensive_calculation()}")
  ```

## Examples

### Complete Bot with Logging Configuration

For a complete, production-ready example of a bot with best-practice logging configuration, see **`logging_example.py`** in this directory. This example demonstrates:

- Environment-specific logging configuration (development vs. production)
- Proper log directory setup under the bot project
- Log rotation and file management
- Component-level filtering
- JSON and plain text format options
- Performance considerations for different environments

### Running the Logging Example

To test the logging configuration:

```bash
# Run with development logging (verbose)
uv run logging_example.py

# Run with production logging (minimal console output)
TRADING_ENV=production uv run logging_example.py
```

### Basic Bot Configuration
```python
from nautilus_trader.config import LoggingConfig, TradingNodeConfig

logging_config = LoggingConfig(
    log_level="INFO",
    log_level_file="DEBUG",
    log_directory="logs",
    log_colors=True,
    log_file_max_size=50_000_000,  # 50 MB
    log_file_max_backup_count=5
)

config = TradingNodeConfig(
    trader_id="MY-FIRST-BOT",
    logging=logging_config
)
```

### Advanced Bot Configuration
```python
logging_config = LoggingConfig(
    log_level="INFO",
    log_level_file="DEBUG",
    log_directory="logs",
    log_file_format="JSON",
    log_file_max_size=100_000_000,
    log_file_max_backup_count=10,
    log_component_levels={
        "MyFirstBot": "DEBUG",
        "RiskEngine": "INFO",
        "Portfolio": "WARNING"
    },
    log_colors=True,
    print_config=False
)
```

### Backtesting Configuration
```python
from nautilus_trader.config import BacktestEngineConfig

# Quieter logging for backtesting
backtest_logging = LoggingConfig(
    log_level="WARNING",      # Reduce console noise
    log_level_file="DEBUG",   # Detailed file logs
    log_directory="logs/backtest",
    log_file_name="backtest_run",
    log_colors=False          # No colors in files
)

backtest_config = BacktestEngineConfig(
    trader_id="BACKTEST-001",
    logging=backtest_logging
)
```

### Direct Logger Usage
```python
from nautilus_trader.common.component import init_logging, Logger

# Initialize logging system
log_guard = init_logging()

# Create logger for specific component
logger = Logger("MyComponent")

# Use logger
logger.info("Application started")
logger.debug("Detailed information")
logger.error("Something went wrong")

# Keep log_guard alive for the application lifetime
```

## Troubleshooting

### Common Issues

#### 1. Log Files Not Created
- Check that the log directory exists or can be created
- Verify `log_level_file` is not None
- Ensure sufficient disk space and write permissions

#### 2. "Error sending log event" Messages
- Use LogGuard when running multiple engines
- Ensure only one logging system is initialized per process

#### 3. Excessive Log Files
- Check log rotation settings (`log_file_max_backup_count`)
- Consider increasing `log_file_max_size` for fewer, larger files
- Review component-level filtering to reduce log volume

#### 4. Missing Logs from Rust Components
- Set `use_pyo3=True` in LoggingConfig (note: performance impact)
- Ensure appropriate log levels are set

#### 5. Colors Not Displaying
- Set `log_colors=True`
- Verify your terminal supports ANSI color codes
- Consider disabling colors for file output

### Performance Tips

1. **Use appropriate log levels**: Don't use DEBUG in production unless necessary
2. **Component filtering**: Filter out noisy components you don't need
3. **File vs. Console**: Use different levels for file and console output
4. **Log rotation**: Configure appropriate file sizes to balance performance and organization

### Environment Variables

You can also configure logging via environment variables:

```bash
# Set log levels
export LOG_LEVEL="INFO"
export LOG_LEVEL_FILE="DEBUG"

# Set log directory
export LOG_DIRECTORY="logs"
```

Then use in your code:
```python
import os

logging_config = LoggingConfig(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    log_level_file=os.getenv("LOG_LEVEL_FILE", "DEBUG"),
    log_directory=os.getenv("LOG_DIRECTORY", "logs")
)
```

## Conclusion

Proper logging configuration is crucial for trading applications. It provides visibility into system behavior, helps with debugging, and creates audit trails for compliance. Follow the best practices outlined in this guide to create a robust logging setup that grows with your trading system.

For more information, refer to the [official Nautilus Trader documentation](https://nautilustrader.io/docs/latest/concepts/logging).
