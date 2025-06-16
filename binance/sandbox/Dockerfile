# Multi-stage Dockerfile for Binance Spot Trading Client
# Inspired by Nautilus Trader Docker patterns

# Base stage with common dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
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
FROM development as testing

# Run tests by default
CMD ["python", "-m", "pytest", "tests/", "-v", "--tb=short"]

# Production stage
FROM base as production

# Copy only necessary files
COPY src/ ./src/
COPY health.py .
COPY requirements.txt .

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
