.PHONY: help install sync fetch test lint check serve

PYTHON ?= python3

.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make install  Install the package and development tools"
	@echo "  make sync     Refresh generated content from researchmap"
	@echo "  make test     Run the Python test suite"
	@echo "  make lint     Run Python and JavaScript static checks"
	@echo "  make check    Run all local validation"
	@echo "  make serve    Serve the site at http://localhost:8000"

install:
	$(PYTHON) -m pip install -e ".[dev]"

sync:
	$(PYTHON) -m researchmap_site

# Compatibility with the old command name.
fetch: sync

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check .
	node --check assets/js/main.js

check: lint test

serve:
	$(PYTHON) -m http.server 8000
