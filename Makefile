.PHONY: run
run:
	@docker compose up -d --build

.PHONY: lint
lint:
	@flake8 src
	@isort src
	@black src

.PHONY: test
test:
	@echo 'Starting tests...'
	@docker compose exec api pytest -p no:warnings

.PHONY: coverage
coverage:
	@docker compose exec api pytest -p no:warnings --cov="src"
