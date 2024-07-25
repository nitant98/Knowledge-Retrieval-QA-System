COMPOSE_BASE := docker-compose
LOG_FILE := build.log

# pytest:
#   pytest -v fastapi;

build-up:
	$(COMPOSE_BASE) up -d --build --remove-orphans

up:	
	$(COMPOSE_BASE) up -d

restart:	
	$(COMPOSE_BASE) restart

down:
	$(COMPOSE_BASE) down
