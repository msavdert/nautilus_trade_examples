# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Sistem bağımlılıklarını yükle
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Python bağımlılıklarını yükle
COPY pyproject.toml .
RUN uv pip install --system .

# Uygulama kodunu kopyala
COPY . .

# Log dizini oluştur
RUN mkdir -p /app/logs

# Entrypoint script'ini kopyala ve çalıştırılabilir yap
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Entrypoint script'ini kullan
ENTRYPOINT ["/entrypoint.sh"]

# Varsayılan komut
CMD ["python", "sandbox_trader.py"]
