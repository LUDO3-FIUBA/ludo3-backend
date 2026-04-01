SHELL := /bin/bash
PWD := $(shell pwd)

all:

up:
	docker compose -f docker-compose.yml up -d --build --remove-orphans
.PHONY: up

down:
	docker compose -f docker-compose.yml down
.PHONY: down

test:
	docker exec -it web python3 manage.py test
.PHONY: test