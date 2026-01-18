# Sentinel Scan Makefile
# Common tasks for development and distribution

.PHONY: install install-dev test test-cov lint format type-check check build clean publish publish-test

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=sentinel_scan --cov-report=term-missing --cov-report=html

test-e2e:
	python scripts/e2e_test.py

# Code quality
lint:
	ruff check sentinel_scan tests

format:
	ruff format sentinel_scan tests

type-check:
	mypy sentinel_scan

# Run all checks (lint, format check, type check, tests)
check: lint type-check test
	@echo "All checks passed!"

# Build distribution
build: clean
	python -m build

# Clean build artifacts
clean:
	rm -rf dist/ build/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Publish to PyPI (requires TWINE_USERNAME and TWINE_PASSWORD env vars)
publish: build
	twine upload dist/*

# Publish to Test PyPI
publish-test: build
	twine upload --repository testpypi dist/*

# Help
help:
	@echo "Sentinel Scan Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install      - Install package in editable mode"
	@echo "  make install-dev  - Install with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make test-e2e     - Run end-to-end tests"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo "  make type-check   - Run type checker"
	@echo "  make check        - Run all checks"
	@echo ""
	@echo "Distribution:"
	@echo "  make build        - Build distribution packages"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make publish      - Publish to PyPI"
	@echo "  make publish-test - Publish to Test PyPI"
