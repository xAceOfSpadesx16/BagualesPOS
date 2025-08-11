DOCKER_DEV=docker compose -f docker-compose.dev.yml --env-file .env.development
DOCKER_TEST=docker compose -f docker-compose.test.yml

# Levantar entorno de desarrollo
build:
	$(DOCKER_DEV) build

build-no-cache:
	$(DOCKER_DEV) build --no-cache
	
up --build:
	$(DOCKER_DEV) up --build

up:
	$(DOCKER_DEV) up
# Cerrar entorno de desarrollo
down:
	$(DOCKER_DEV) down

down-all:
	$(DOCKER_DEV) down --volumes --remove-orphans

# Correr tests
test:
	$(DOCKER_TEST) run --rm web

# Limpiar volúmenes (opcional)
clean:
	docker volume prune -f

# Correr migraciones (útil para desarrollo)
migrate:
	$(DOCKER_DEV) exec web uv run --python 3.13 manage.py migrate

makemigrations:
	$(DOCKER_DEV) exec web uv run --python 3.13 manage.py makemigrations

command:
	$(DOCKER_DEV) exec web /bin/bash