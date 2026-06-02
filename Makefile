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

CMD ?=

exec:
	docker exec -it web $(CMD)

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

test-deprecations:
	docker exec web python3 \
		-W error::DeprecationWarning \
		-W error::PendingDeprecationWarning \
		-W ignore::DeprecationWarning:pkg_resources \
		-W ignore::DeprecationWarning:coreapi \
		manage.py test

.PHONY: test-deprecations

test-verbose:
	docker exec web python3 manage.py test --verbosity=2
.PHONY: test-verbose

check:
	docker exec web python3 manage.py check --deploy
.PHONY: check

shell:
	docker exec -it web python3 manage.py shell
.PHONY: shell

pip-freeze:
	docker exec web pip freeze > requirements.lock.txt
.PHONY: pip-freeze