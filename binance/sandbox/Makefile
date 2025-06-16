# Binance Spot Trading Client - Docker Commands
# All operations are containerized following Nautilus Trader patterns

.PHONY: help setup dev test prod clean logs health

# Default target
help:
	@echo "Binance Spot Trading Client - Docker Commands"
	@echo ""
	@echo "Setup:"
	@echo "  setup          Copy .env.example to .env (edit manually after)"
	@echo "  build          Build all Docker images"
	@echo ""
	@echo "Development:"
	@echo "  dev            Start development environment"
	@echo "  dev-shell      Access development shell"
	@echo "  dev-logs       View development logs"
	@echo ""
	@echo "Testing:"
	@echo "  test           Run all tests"
	@echo "  test-unit      Run unit tests only"
	@echo "  test-cov       Run tests with coverage"
	@echo "  test-debug     Run tests with debugging"
	@echo ""
	@echo "Production:"
	@echo "  prod           Start production client"
	@echo "  prod-daemon    Start production client in background"
	@echo "  prod-logs      View production logs"
	@echo "  prod-stop      Stop production client"
	@echo ""
	@echo "Monitoring:"
	@echo "  health         Check container health"
	@echo "  logs           View all logs"
	@echo "  status         Show container status"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          Clean up containers and volumes"
	@echo "  syntax-check   Check Python syntax"
	@echo "  format         Format code with black"
	@echo "  lint           Lint code with flake8"

# Setup
setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please edit .env with your API credentials"; \
	else \
		echo ".env file already exists"; \
	fi

build:
	docker-compose build

# Development
dev:
	docker-compose up binance-dev

dev-shell:
	docker-compose exec binance-dev bash

dev-logs:
	docker-compose logs -f binance-dev

# Testing
test:
	docker-compose up binance-test

test-unit:
	docker-compose run --rm binance-test python -m pytest tests/test_basic.py -v

test-cov:
	docker-compose run --rm binance-test python -m pytest tests/ --cov=src/ --cov-report=term-missing

test-debug:
	docker-compose run --rm binance-test python -m pytest tests/ -v --tb=long --pdb

# Production
prod:
	docker-compose up binance-client

prod-daemon:
	docker-compose up -d binance-client

prod-logs:
	docker-compose logs -f binance-client

prod-stop:
	docker-compose stop binance-client

# Monitoring
health:
	docker-compose ps
	@echo ""
	@echo "Container Health Status:"
	@docker inspect --format='{{.Name}}: {{.State.Health.Status}}' $$(docker-compose ps -q) 2>/dev/null || echo "No health checks available"

logs:
	docker-compose logs -f

status:
	docker-compose ps
	@echo ""
	@echo "Resource Usage:"
	@docker stats --no-stream $$(docker-compose ps -q) 2>/dev/null || echo "No running containers"

# Maintenance
clean:
	docker-compose down -v
	docker system prune -f

syntax-check:
	docker-compose run --rm binance-test python -m py_compile src/*.py
	docker-compose run --rm binance-test python -m py_compile tests/*.py
	@echo "Python syntax check completed"

format:
	docker-compose run --rm binance-dev black src/ tests/
	@echo "Code formatting completed"

lint:
	docker-compose run --rm binance-dev flake8 src/ tests/ --max-line-length=100
	@echo "Code linting completed"

# Docker config validation
validate-compose:
	docker-compose config

# Quick development setup
quick-start: setup build dev

# Full test suite
test-all: syntax-check test test-cov

# Production deployment check
deploy-check: syntax-check test build
	@echo "Deployment checks passed"
