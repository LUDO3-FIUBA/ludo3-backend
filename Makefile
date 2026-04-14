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

down:
	docker compose -f docker-compose.yml down
.PHONY: down

test:
	docker exec web python3 manage.py test
.PHONY: test
