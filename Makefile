# Makefile for db repo
# Ensures db + tb3_workbench + langgraph build together and compile.

.PHONY: build install test db-test db-up db-down

build: install
	@./scripts/build.sh

install:
	@uv venv .venv 2>/dev/null || true
	@. .venv/bin/activate && uv pip install -r requirements.txt -q
	@if [ -d ../pluto/tb3_workbench ]; then \
		. .venv/bin/activate && uv pip install -e ../pluto/tb3_workbench -q; \
	fi

test:
	@. .venv/bin/activate && ./scripts/run_all_tests.sh -a

# PostgreSQL test instance for db consistency/ACID/query tests (port 5433)
db-up:
	docker compose -f docker/docker-compose.test-postgresql.yml up -d
	@echo "Waiting for PostgreSQL..."
	@sleep 3

db-down:
	docker compose -f docker/docker-compose.test-postgresql.yml down

db-test: db-up
	@. .venv/bin/activate && python3 scripts/test_all_databases_consistency_acid.py
