SHELL := bash

.PHONY: install
install: install-uv ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@set -o pipefail; uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml --junitxml=tests/pytest.xml | tee tests/pytest-coverage.txt

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: install-uv
install-uv: ## Install uv (pre-requisite for initialize)
	@echo "🚀 Installing uv"
	@command -v uv &> /dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh || true

.PHONY: install-pipx
install-pipx: ## Install pipx (pre-requisite for external tools)
	@echo "🚀 Installing pipx"
	@command -v pipx &> /dev/null || pip install --user pipx || true

.PHONY: install-copier
install-copier: install-pipx ## Install copier (pre-requisite for init-project)
	@echo "🚀 Installing copier"
	@command -v copier &> /dev/null || pipx install copier || true

.PHONY: init-project
init-project: initialize ## Initialize the project (Warning: do this only once!)
	@echo "🚀 Initializing project from template"
	@copier copy --trust --answers-file .copier-config.yaml gh:entelecheia/hyperfast-uv-template .

.PHONY: reinit-project
reinit-project: install-copier ## Reinitialize the project (Warning: this may overwrite existing files!)
	@echo "🚀 Reinitializing project from template"
	@bash -c 'args=(); while IFS= read -r file; do args+=("--skip" "$$file"); done < .copierignore; copier copy --trust "$${args[@]}" --answers-file .copier-config.yaml gh:entelecheia/hyperfast-uv-template .'
.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<25}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
