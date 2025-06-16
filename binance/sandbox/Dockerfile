# Multi-stage Dockerfile for Binance Spot Trading Client
# Following Nautilus Trader Docker patterns exactly

FROM python:3.13-slim AS base

# Set environment variables following Nautilus patterns
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    PYO3_PYTHON="/usr/local/bin/python3" \
    PYSETUP_PATH="/opt/pysetup" \
    BUILD_MODE="release"

ENV PATH="/root/.local/bin:$PATH"
WORKDIR $PYSETUP_PATH

FROM base AS builder

# Install build dependencies (following Nautilus pattern)
RUN apt-get update && \
    apt-get install -y curl gcc git libssl-dev make pkg-config && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install UV (following Nautilus pattern)
COPY uv-version ./
RUN UV_VERSION=$(cat uv-version) && curl -LsSf https://astral.sh/uv/$UV_VERSION/install.sh | sh

# Install package requirements (following Nautilus pattern)
COPY uv.lock pyproject.toml requirements.txt ./
RUN uv sync --no-install-package binance-spot-trader || uv pip install --system -r requirements.txt

# Copy source code for building
COPY src/ ./src/
COPY health.py ./
COPY README.md ./

# Install the package
RUN uv build --wheel || (pip install build && python -m build --wheel)
RUN uv pip install --system dist/*.whl || pip install dist/*.whl

# Clean up bytecode files (following Nautilus pattern)
RUN find /usr/local/lib/python3.13/site-packages -name "*.pyc" -exec rm -f {} \;

# Development stage
FROM base AS development

# Copy installed packages from builder (following Nautilus pattern)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Install development dependencies
RUN curl -LsSf https://astral.sh/uv/0.7.13/install.sh | sh
RUN uv pip install --system \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython \
    jupyter

# Copy source code
COPY . .

# Create directories for logs and data
RUN mkdir -p logs data

# Default command for development
CMD ["python", "-c", "print('Development environment ready'); import time; time.sleep(3600)"]

# Testing stage  
FROM development AS testing

# Run tests by default
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]

# Final application image (following Nautilus pattern)
FROM base AS application

# Copy installed packages from builder (following Nautilus pattern)
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set working directory
WORKDIR /app

# Copy only necessary files
COPY src/ ./src/
COPY health.py ./

# Create non-root user for security
RUN groupadd -r trader && useradd -r -g trader trader && \
    mkdir -p logs data && \
    chown -R trader:trader /app

# Switch to non-root user
USER trader

# Health check script
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import health; health.check()"

# Default command
CMD ["python", "src/main.py"]

# Production stage alias (for docker-compose compatibility)
FROM application AS production
