.PHONY: build test lint format clean ci

PYTHON = uv run python
BUILD_SCRIPT = build.py
CONFIG = config/config.toml
SRC_DIR = plotly_lvlos
TEST_DIR = tests

build:

	@if [ -f matches.csv ]; then \
		echo CAREFUL ! matches.csv is rm each time make is called ! Rm the rm before final push; \
		rm matches.csv; \
	fi

	@echo " Building project..."
	@if [ ! -f $(CONFIG) ]; then \
		echo "Config file $(CONFIG) not found!"; \
		exit 1; \
	fi
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
