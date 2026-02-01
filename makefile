# ========================
# CONFIG
# ========================

APP=app.main:app
VENV=env

PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip
UVICORN=$(VENV)/bin/uvicorn
PYTEST=$(VENV)/bin/pytest
ALEMBIC=$(VENV)/bin/alembic

# ========================
# HELP
# ========================

.PHONY: help
help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install dependencies"
	@echo "  make run            Run FastAPI"
	@echo "  make dev            Run FastAPI with reload"
	@echo "  make test           Run tests"
	@echo "  make cov            Run tests with coverage"
	@echo "  make lint           Run ruff"
	@echo "  make format         Run black"
	@echo "  make migrate        Alembic upgrade head"
	@echo "  make revision       Create alembic revision"
	@echo "  make docker-up      Run docker-compose"
	@echo "  make docker-down    Stop docker-compose"
	@echo "  make clean          Clean caches"
	@echo ""

# ========================
# INSTALL
# ========================

.PHONY: install
install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# ========================
# RUN
# ========================

.PHONY: run
run:
	$(UVICORN) $(APP) --host 0.0.0.0 --port 8000

.PHONY: dev
dev:
	$(UVICORN) $(APP) --reload --host 0.0.0.0 --port 8000

# ========================
# TESTING
# ========================

.PHONY: test
test:
	$(PYTEST) tests

.PHONY: cov
cov:
	$(PYTEST) \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html \
		tests

# ========================
# QUALITY
# ========================

.PHONY: lint
lint:
	$(PYTHON) -m ruff check app tests

.PHONY: format
format:
	$(PYTHON) -m black app tests

# ========================
# DATABASE
# ========================

.PHONY: migrate
migrate:
	$(ALEMBIC) upgrade head

.PHONY: revision
revision:
	$(ALEMBIC) revision --autogenerate -m "auto migration"

# ========================
# DOCKER
# ========================

.PHONY: docker-up
docker-up:
	docker compose up -d

.PHONY: docker-down
docker-down:
	docker compose down

# ========================
# CLEAN
# ========================

.PHONY: clean
clean:
	rm -rf .pytest_cache .coverage htmlcov .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
