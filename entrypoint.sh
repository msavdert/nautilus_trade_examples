#!/bin/bash

# entrypoint script for Nautilus Trader Docker setup

echo "=== Nautilus Trader Minimal Setup ==="
echo "Python version: $(python --version)"
echo "Working directory: $(pwd)"
echo

echo "=== Environment ready! ==="
echo "You can now run for example:"
echo "  uv add nautilus_trader                                      # Install nautilus_trader"
echo "  uv run python -c \"import nautilus_trader; print('OK')\"       # Test installation"
echo "  uv run python your_script.py                               # Run your trading script"
echo

# If no command is provided, check if we have a TTY and start appropriate shell
if [ $# -eq 0 ]; then
    if [ -t 0 ]; then
        echo "Starting interactive shell..."
        exec bash
    else
        echo "No TTY detected. Use docker run -it for interactive mode."
        echo "Container ready for commands. Example:"
        echo "  docker-compose exec nautilus-trader bash"
    fi
else
    exec "$@"
fi
