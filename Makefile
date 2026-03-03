.PHONY: help deps-freeze deps-install deps-check deps-tree dev test test-cov test-smoke test-last clean logs shell db-shell migrate

# Цвета для вывода
BLUE := "\\033[34m"
GREEN := "\\033[32m"
RED := "\\033[31m"
RESET := "\\033[0m"

help:
	@echo "$(BLUE)╔════════════════════════════════════════╗$(RESET)"
	@echo "$(BLUE)║     Dating Site API Makefile          ║$(RESET)"
	@echo "$(BLUE)╚════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(GREEN)Доступные команды:$(RESET)"
	@echo ""
	@echo "  $(GREEN)Зависимости:$(RESET)"
	@echo "    make deps-freeze     - обновить requirements.base.txt из контейнера"
	@echo "    make deps-install    - установить dev-зависимости локально"
	@echo "    make deps-check      - проверить устаревшие пакеты"
	@echo "    make deps-tree       - показать дерево зависимостей"
	@echo ""
	@echo "  $(GREEN)Разработка:$(RESET)"
	@echo "    make dev             - запустить дев-сервер с логами"
	@echo "    make logs            - показать логи всех контейнеров"
	@echo "    make shell           - зайти в контейнер api"
	@echo "    make db-shell        - зайти в PostgreSQL"
	@echo ""
	@echo "  $(GREEN)Тестирование:$(RESET)"
	@echo "    make test            - запустить все тесты"
	@echo "    make test-cov        - тесты с отчетом о покрытии"
	@echo "    make test-smoke      - только smoke тесты"
	@echo "    make test-last       - перезапустить упавшие тесты"
	@echo ""
	@echo "  $(GREEN)Очистка:$(RESET)"
	@echo "    make clean           - очистить кэш и временные файлы"
	@echo "    make clean-docker    - остановить и удалить контейнеры"
	@echo ""
	@echo "  $(GREEN)Миграции:$(RESET)"
	@echo "    make migrate         - показать текущую миграцию"
	@echo "    make migrate-create  - создать новую миграцию"
	@echo "    make migrate-up      - применить миграции"
	@echo "    make migrate-down    - откатить последнюю миграцию"
	@echo ""

# Зависимости
deps-freeze:
	@echo "$(GREEN)Freezing production dependencies...$(RESET)"
	@docker exec dating-api pip freeze | findstr /v "pytest ipython black ruff pytest-cov Faker" > app/settings/requirements.base.txt
	@echo "$(GREEN)Base requirements updated$(RESET)"

deps-install:
	@echo "$(GREEN)Installing development dependencies...$(RESET)"
	pip install -r app/settings/requirements.dev.txt
	@echo "$(GREEN)Done$(RESET)"

deps-check:
	@echo "$(GREEN)🔍 Checking for outdated packages...$(RESET)"
	pip list --outdated

deps-tree:
	@echo "$(GREEN) Dependency tree...$(RESET)"
	pipdeptree

# Разработка
dev:
	@echo "$(GREEN) Starting dev server...$(RESET)"
	docker compose up -d
	docker logs -f dating-api

logs:
	@echo "$(GREEN) Showing logs...$(RESET)"
	docker compose logs -f

shell:
	@echo "$(GREEN) Entering api container...$(RESET)"
	docker exec -it dating-api bash

db-shell:
	@echo "$(GREEN) Entering PostgreSQL...$(RESET)"
	docker exec -it dating-postgres psql -U postgres -d Dating_site

# Тестирование
test:
	@echo "$(GREEN) Running all tests...$(RESET)"
	docker exec dating-api pytest tests/ -v

test-cov:
	@echo "$(GREEN) Running tests with coverage...$(RESET)"
	docker exec dating-api pytest tests/ --cov=app --cov-report=term-missing --cov-report=html
	@echo "$(GREEN) HTML report: ./htmlcov/index.html$(RESET)"

test-smoke:
	@echo "$(GREEN) Running smoke tests...$(RESET)"
	docker exec dating-api pytest tests/ -m smoke -v

test-last:
	@echo "$(GREEN) Rerunning last failed tests...$(RESET)"
	docker exec dating-api pytest tests/ --lf -v

# Очистка
clean:
	@echo "$(GREEN) Cleaning cache and temp files...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>nul || echo "  No pycache found"
	@find . -type f -name "*.pyc" -delete 2>nul || echo "  No pyc files found"
	@rm -rf .pytest_cache 2>nul || echo "  No pytest cache found"
	@rm -rf htmlcov 2>nul || echo "  No htmlcov found"
	@rm -rf .coverage 2>nul || echo "  No coverage found"
	@rm -f pytest.log 2>nul || echo "  No pytest.log found"
	@echo "$(GREEN) Clean complete$(RESET)"

clean-docker:
	@echo "$(GREEN) Stopping and removing containers...$(RESET)"
	docker compose down -v
	@echo "$(GREEN) Docker clean complete$(RESET)"

# Миграции
migrate:
	@echo "$(GREEN) Current migration:$(RESET)"
	docker exec dating-api alembic current

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker exec dating-api alembic revision --autogenerate -m "$$msg"

migrate-up:
	@echo "$(GREEN) Applying migrations...$(RESET)"
	docker exec dating-api alembic upgrade head

migrate-down:
	@echo "$(GREEN) Rolling back last migration...$(RESET)"
	docker exec dating-api alembic downgrade -1