.PHONY: build test lint format clean ci

PYTHON = uv run python
BUILD_SCRIPT = build.py
CONFIG = config/config.toml
SRC_DIR = plotly_lvlos
TEST_DIR = tests

build:

	@if [ -f core_data.duckdb ]; then \
		rm core_data.duckdb; \
	fi

	@echo " Building project..."

	$(PYTHON) $(BUILD_SCRIPT)
	@echo "Build complete."

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest $(TEST_DIR) --disable-warnings -v

ruff:
	@echo "Linting code with ruff..."
	$(PYTHON) -m ruff check $(SRC_DIR) $(TEST_DIR)

clean:
	@echo "Cleaning cache..."
	rm -rf __pycache__ */__pycache__

ci: clean build ruff test
	@echo "CI tasks completed successfully!"
