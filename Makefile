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
	docker compose -f docker-compose.yml -f docker-compose.remote.yml down --remove-orphans
.PHONY: down