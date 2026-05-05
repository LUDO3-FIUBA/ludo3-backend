SHELL := /bin/bash
PWD := $(shell pwd)

all:

up: up-local
.PHONY: up

up-local:
	docker compose -f docker-compose.yml up -d --build --remove-orphans
.PHONY: up-local

up-remote:
	docker compose -f docker-compose.remote.yml up -d --build --remove-orphans
.PHONY: up-remote

migrate:
	docker exec -it web python3 manage.py migrate
	docker exec -it web python3 manage.py initdata
.PHONY: migrate

down:
	docker compose -f docker-compose.yml down
.PHONY: down

prune:
	docker compose -f docker-compose.yml down --rmi all --volumes --remove-orphans
.PHONY: prune

restart: down up-local
.PHONY: restart

test:
	docker exec web python3 manage.py test
.PHONY: test
