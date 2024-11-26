define BROWSER_PYSCRIPT
import os, webbrowser, sys

# Hack to handle WSL2 ubuntu
if 'microsoft-standard-WSL2' in str(os.uname()):
	os.system('wslview ' + sys.argv[1])
else:
	try:
		from urllib import pathname2url
	except:
		from urllib.request import pathname2url
	webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

.DEFAULT_GOAL := help

SHELL := /bin/bash

.PHONY: build
build: ## Build a docker container containing the MacMedia flask app
	@echo "+ $@"
	@docker build --pull --rm -f "Dockerfile" -t macmedia:latest "."

.PHONY: build-db
build-db: ## Build a docker postgres container 
	@echo "+ $@"
	@docker build --pull --rm -f "Dockerfile-db" -t macmedia-db:latest "."

.PHONY: run-docker-dev
run-docker-dev:  ## Run MacMedia in a local docker container in development mode
	@echo "+ $@"
	@docker run -d -p 5000:5000 --env FLASK_ENV=development macmedia:latest

.PHONY: run-docker-db
run-docker-db: ## Run MacMedia database in a local docker container 
	@echo "+ $@"
	@docker run -d -p 5342:5342 macmedia-db:latest

.PHONY: run-dev
run-dev:  ## Run the MacMedia full stack (webapp and db) in local docker container
	@echo "+ $@"
	@source .env
	echo ${POSTGRES_DB} > postgres_db.txt
	echo ${POSTGRES_PASSWORD} > postgres_password.txt
	echo ${POSTGRES_USER} > postgres_user.txt
	@docker compose up -d
	rm postgres_db.txt postgres_password.txt postgres_user.txt

.PHONY: deploy-staging
deploy-staging:  ## Deploy the MacMedia docker container into the staging environment and run it in staging mode
	@echo "+ $@"
	@echo "Unimplemented"

.PHONY: deploy-prod
deploy-prod:  ## Deploy the MacMedia docker container into the production environment and run it in production mode
	@echo "+ $@"
	@echo "Unimplemented"

.PHONY: clean-build
clean-build: ## Remove build artifacts
	@echo "+ $@"
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	@echo "+ $@"
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type f -name '*.py[co]' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +

.PHONY: clean
clean: clean-build clean-pyc ## Remove all file artifacts

.PHONY: lint
lint: ## Check code style with flake8
	@echo "+ $@"
	@bin/lint.sh

.PHONY: test
test: ## Run tests quickly with the default Python
	@echo "+ $@"
	@export APP_ENV=Test; python -m pytest tests

.PHONY: coverage
coverage: ## Check code coverage quickly with the default Python
	@echo "+ $@"
	@export PYTHONPATH="."; export APP_ENV=Test; pytest --cov-report=html:app/docs/htmlcov --cov=app tests/
	@$(BROWSER) app/docs/htmlcov/index.html

.PHONY: ci-coverage
coverage-ci: ## Check code coverage in CI quickly with the default Python
	@echo "+ $@"
	@export PYTHONPATH="."; export APP_ENV=Test; pytest --cov-report term --cov-report xml:coverage.xml --cov=app tests/

.PHONY: docs
docs: ## Generate Sphinx HTML documentation, including API docs
	@echo "+ $@"
	#@cd app
	@rm -f app/docs/MacMedia.rst
	@sphinx-apidoc -o app/docs/source .
	#@rm -f docs/modules.rst
	@$(MAKE) -C app/docs clean
	@$(MAKE) -C app/docs html
	@$(BROWSER) app/docs/_build/html/index.html

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
