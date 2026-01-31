.PHONY: help build up down logs test migrate clean create-admin

help:
	@echo "VietCMS Moderation Service - Development Commands"
	@echo ""
	@echo "make build       - Build Docker images"
	@echo "make up          - Start all services"
	@echo "make down        - Stop all services"
	@echo "make logs        - View logs"
	@echo "make migrate     - Run database migrations"
	@echo "make test        - Run tests"
	@echo "make clean       - Clean up volumes and images"
	@echo "make create-admin - Create default admin user"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started. Run 'make logs' to view logs."

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	docker-compose exec moderation-api alembic upgrade head

test:
	docker-compose exec moderation-api pytest tests/

clean:
	docker-compose down -v
	docker system prune -f

create-admin:
	@echo "Creating default admin user..."
	docker-compose exec postgres psql -U vietcms -d vietcms_moderation -f /scripts/create-admin.sql
	@echo "Admin user created! Login: admin@vietcms.com / admin123"

setup-demo:
	@echo "Setting up demo client..."
	powershell -ExecutionPolicy Bypass -File ./scripts/setup-demo-client.ps1

