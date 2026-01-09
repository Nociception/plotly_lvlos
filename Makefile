.PHONY: build test lint format clean ci

PYTHON = uv run python
BUILD_SCRIPT = build.py
CONFIG = config.toml
SRC_DIR = plotly_lvlos
TEST_DIR = tests

build:
	@echo " Building project..."
	@if [ ! -f $(CONFIG) ]; then \
		echo "Config file $(CONFIG) not found!"; \
		exit 1; \
	fi
	$(PYTHON) $(BUILD_SCRIPT)
	@echo "Build complete."

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest $(TEST_DIR) --maxfail=1 --disable-warnings -v

lint:
	@echo "Running lint..."
	$(PYTHON) -m flake8 $(SRC_DIR)

format:
	@echo "Running code formatter..."
	$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR)

clean:
	@echo "Cleaning cache..."
	rm -rf __pycache__ */__pycache__

ci: clean build format lint test
	@echo "CI tasks completed successfully!"
