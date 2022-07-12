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

.PHONY: clean-tox
clean-tox: ## Remove tox testing artifacts
	@echo "+ $@"
	@rm -rf .tox/

.PHONY: build
build: ## Build a docker container containing the MacMedia flask app
	@echo "+ $@"
	@docker build --pull --rm -f "Dockerfile" -t macmovies:latest "."

.PHONY: run-dev
run-dev:  ## Run MacMedia in a local docker container in development mode
	@echo "+ $@"
	@docker run -d -p 5000:5000 --env FLASK_ENV=development macmovies

.PHONY: deploy-staging
deploy-staging:  ## Deploy the MacMedia docker container into the staging environment and run it in staging mode
	@echo "+ $@"

.PHONY: deploy-prod
deploy-prod:  ## Deploy the MacMedia docker container into the production environment and run it in production mode
	@echo "+ $@"

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
	#@tox -e py
	@pytest

.PHONY: test-all
test-all: ## Run tests on every Python version with tox
	@echo "+ $@"
	@tox

.PHONY: coverage
coverage: ## Check code coverage quickly with the default Python
	@echo "+ $@"
	@tox -e cov-report
	@$(BROWSER) htmlcov/index.html

.PHONY: ci-coverage
coverage-ci: ## Check code coverage in CI quickly with the default Python
	@echo "+ $@"
	@tox -e cov-report

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
