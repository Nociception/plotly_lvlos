.PHONY: build test ruff clean ci

PYTHON = uv run python
BUILD_SCRIPT = build.py
SRC_DIR = plotly_lvlos
TEST_DIR = tests

build:
	@echo " Building project..."

	$(PYTHON) $(BUILD_SCRIPT)
	@echo "Build complete."

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest $(TEST_DIR) --disable-warnings -v

ruff:
	@echo "Linting code with ruff..."
	$(PYTHON) -m ruff format $(SRC_DIR) $(TEST_DIR)
	$(PYTHON) -m ruff check $(SRC_DIR) $(TEST_DIR)

clean:
	@echo "Cleaning cache and generated files..."
	rm -rf __pycache__ */__pycache__
	@if [ -f "core_data.duckdb" ]; then rm core_data.duckdb; echo "Removed core_data.duckdb"; fi
	@if [ -f "config/matches.xlsx" ]; then rm config/matches.xlsx; echo "Removed config/matches.xlsx"; fi
	@if [ -f "core_data.csv" ]; then rm core_data.csv; echo "Removed core_data.csv"; fi
	@if [ -f "index.html" ]; then rm index.html; echo "Removed index.html"; fi

ci: clean build ruff test
	@echo "CI tasks completed successfully!"
