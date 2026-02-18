DOCKER_DEV=docker compose -f docker-compose.dev.yml --env-file .env.development
DOCKER_TEST=docker compose -f docker-compose.test.yml

.PHONY: help build up down test clean migrate

# Default target
help:
	@echo "BagualesPOS - Makefile commands"
	@echo ""
	@echo "Development:"
	@echo "  make build          - Build development containers"
	@echo "  make build-no-cache - Build without cache"
	@echo "  make up             - Start development environment"
	@echo "  make up-build       - Build and start"
	@echo "  make down           - Stop development environment"
	@echo "  make down-all       - Stop and remove volumes"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run migrations"
	@echo "  make makemigrations - Create new migrations"
	@echo "  make createsuperuser - Create superuser"
	@echo ""
	@echo "Testing:"
	@echo "  make test               - Run all tests"
	@echo "  make test-app           - Run tests for specific app (e.g., app=cash)"
	@echo "  make test-file          - Run specific test file (e.g., file=cash/tests.py)"
	@echo "  make test-fast          - Run tests without migrations"
	@echo "  make test-coverage      - Run tests with coverage report"
	@echo "  make test-coverage-app  - Run coverage for specific app (e.g., app=cash)"
	@echo "  make test-local         - Run tests locally (not Docker)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean Docker volumes"
	@echo "  make command        - Open bash in web container"
	@echo "  make startapp       - Create new app (e.g., app=myapp)"
	@echo "  make logs           - Show logs"

# ====================================
# DEVELOPMENT
# ====================================

build:
	$(DOCKER_DEV) build

build-no-cache:
	$(DOCKER_DEV) build --no-cache

up-build:
	$(DOCKER_DEV) up --build

up:
	$(DOCKER_DEV) up

down:
	$(DOCKER_DEV) down

down-all:
	$(DOCKER_DEV) down --volumes --remove-orphans

logs:
	$(DOCKER_DEV) logs -f

# ====================================
# DATABASE
# ====================================

migrate:
	$(DOCKER_DEV) exec web uv run --python 3.13 python manage.py migrate

makemigrations:
	$(DOCKER_DEV) exec web uv run --python 3.13 python manage.py makemigrations

createsuperuser:
	$(DOCKER_DEV) exec web uv run --python 3.13 python manage.py createsuperuser

# ====================================
# TESTING
# ====================================

test:
	@echo "Running all tests in Docker..."
	$(DOCKER_TEST) run --rm web_test

test-app:
	@echo "Running tests for app: $(app)"
	$(DOCKER_TEST) run --rm web_test sh -c "uv run --python 3.13 python manage.py test $(app) -v 2"


test-file:
	@echo "Running test file: $(file)"
	$(DOCKER_TEST) run --rm web_test sh -c "uv run --python 3.13 python manage.py test $(file) --parallel --keepdb"

test-fast:
	@echo "Running tests without migrations (fast mode)..."
	$(DOCKER_TEST) run --rm web_test sh -c "uv run --python 3.13 python manage.py test --parallel --keepdb --nomigrations"

test-coverage:
	@echo "Running tests with coverage..."
	$(DOCKER_TEST) run --rm web_test sh -c " \
		uv run --python 3.13 coverage run --source='.' manage.py test && \
		uv run --python 3.13 coverage report && \
		uv run --python 3.13 coverage html \
	"
	@echo "Coverage report generated in htmlcov/index.html"

test-coverage-app:
	@echo "Running coverage for app: $(app)"
	$(DOCKER_TEST) run --rm web_test sh -c " \
		uv run --python 3.13 coverage run --source='$(app)' manage.py test $(app) && \
		uv run --python 3.13 coverage report && \
		uv run --python 3.13 coverage html \
	"
	@echo "Coverage report for $(app) generated in htmlcov/index.html"


test-local:
	@echo "Running tests locally (requires local Python environment)..."
	@export DJANGO_SETTINGS_MODULE=BagualesPOS.settings.testing && \
	uv run --python 3.13 python manage.py test --parallel

test-verbose:
	@echo "Running tests with verbose output..."
	$(DOCKER_TEST) run --rm web_test sh -c "uv run --python 3.13 python manage.py test --verbosity=2"

# ====================================
# UTILITIES
# ====================================

clean:
	docker volume prune -f

command:
	$(DOCKER_DEV) exec web /bin/bash

shell:
	$(DOCKER_DEV) exec web uv run --python 3.13 python manage.py shell

startapp:
	$(DOCKER_DEV) exec --user $(shell id -u):$(shell id -g) -e UV_CACHE_DIR=/tmp/uv_cache web uv run --python 3.13 python manage.py startapp $(app)

ps:
	$(DOCKER_DEV) ps

restart:
	$(DOCKER_DEV) restart

# ====================================
# CI/CD
# ====================================

ci-test:
	@echo "Running CI tests..."
	@export DJANGO_SETTINGS_MODULE=BagualesPOS.settings.testing && \
	uv run --python 3.13 python manage.py migrate --noinput && \
	uv run --python 3.13 python manage.py test --parallel --no-input

ci-lint:
	@echo "Running linters..."
	@uv run --python 3.13 ruff check .
	@uv run --python 3.13 black --check .