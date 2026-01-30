.PHONY: up down restart logs logs-app logs-ollama logs-weaviate build clean help

help:
	@echo "Callisto - Docker Commands"
	@echo ""
	@echo "  make up          - Start all services (with logs visible)"
	@echo "  make down        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show all logs (live)"
	@echo "  make logs-app    - Show app logs (live)"
	@echo "  make logs-ollama - Show Ollama logs (live)"
	@echo "  make build       - Rebuild containers"
	@echo "  make clean       - Stop and remove all containers/volumes"
	@echo ""

up:
	docker-compose up

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

logs-app:
	docker-compose logs -f app

logs-ollama:
	docker-compose logs -f ollama

logs-weaviate:
	docker-compose logs -f weaviate

build:
	docker-compose up --build

clean:
	docker-compose down -v
