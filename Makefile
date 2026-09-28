BACKEND := backend
FRONTEND := frontend
UV := uv run --directory $(BACKEND)

.PHONY: setup env migrate seed seed-reset dev backend frontend test test-backend test-frontend \
	lint lint-backend lint-frontend format e2e storybook docker-up docker-down

setup: env
	cd $(BACKEND) && uv sync --extra dev
	npm --prefix $(FRONTEND) ci
	$(MAKE) migrate seed

env:
	test -f $(BACKEND)/.env || cp $(BACKEND)/.env.example $(BACKEND)/.env

migrate:
	$(UV) alembic upgrade head

seed:
	$(UV) python -m app.cli seed

seed-reset:
	$(UV) python -m app.cli seed --reset

dev:
	$(MAKE) -j2 backend frontend

backend:
	$(UV) uvicorn app.main:app --reload --port 8000

frontend:
	npm --prefix $(FRONTEND) run dev

test: test-backend test-frontend

test-backend:
	$(UV) pytest --cov

test-frontend:
	npm --prefix $(FRONTEND) run test:coverage

lint: lint-backend lint-frontend

lint-backend:
	$(UV) ruff check .
	$(UV) ruff format --check .
	$(UV) mypy app

lint-frontend:
	npm --prefix $(FRONTEND) run lint
	npm --prefix $(FRONTEND) run typecheck
	npm --prefix $(FRONTEND) run format:check

format:
	$(UV) ruff format .
	$(UV) ruff check --fix .
	npm --prefix $(FRONTEND) run format

e2e:
	npm --prefix $(FRONTEND) run e2e

storybook:
	npm --prefix $(FRONTEND) run storybook

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
