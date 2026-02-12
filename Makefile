.PHONY: up down restart logs logs-app logs-api logs-weaviate build clean proxy-up proxy-down help

help:
	@echo "Callisto - Docker Commands"
	@echo ""
	@echo "  make up          - Start all services (Docker + Proxy)"
	@echo "  make down        - Stop all services (Docker + Proxy)"
	@echo "  make proxy-up    - Start proxy server only"
	@echo "  make proxy-down  - Stop proxy server only"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show all logs (live)"
	@echo "  make logs-app    - Show app logs (live)"
	@echo "  make logs-api    - Show API logs (live)"
	@echo "  make build       - Rebuild containers"
	@echo "  make clean       - Stop and remove all containers/volumes"
	@echo ""

proxy-up:
	@echo "Starting proxy server on port 7000..."
	@export PATH="$$HOME/.local/bin:$$PATH" && \
		export PYENV_VERSION=3.12.12 && \
		nohup poetry run python proxy_server.py > proxy.log 2>&1 & echo $$! > .proxy.pid
	@sleep 1
	@if ps -p $$(cat .proxy.pid 2>/dev/null) > /dev/null 2>&1; then \
		echo "✓ Proxy started (PID: $$(cat .proxy.pid)). Logs: proxy.log"; \
	else \
		echo "✗ Proxy failed to start. Check proxy.log for errors"; \
		exit 1; \
	fi

proxy-down:
	@if [ -f .proxy.pid ]; then \
		pkill -P $$(cat .proxy.pid) 2>/dev/null || true; \
		kill $$(cat .proxy.pid) 2>/dev/null || true; \
		rm .proxy.pid; \
		echo "Proxy stopped"; \
	else \
		echo "Proxy not running (no .proxy.pid file)"; \
	fi
	@pkill -f "python proxy_server.py" 2>/dev/null || true

up: proxy-up
	@sleep 2
	docker-compose up -d
	@echo ""
	@echo "✓ Proxy running on http://localhost:7000"
	@echo "✓ Streamlit UI: http://localhost:8501"
	@echo "✓ FastAPI docs: http://localhost:8000/docs"

down: proxy-down
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-api:
	docker-compose logs -f api

logs-weaviate:
	docker-compose logs -f weaviate

build:
	docker-compose up --build

clean: proxy-down
	docker-compose down -v
