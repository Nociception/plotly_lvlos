.PHONY: build test lint format clean ci

PYTHON = uv run python
BUILD_SCRIPT = build.py
CONFIG = config/config.toml
SRC_DIR = plotly_lvlos
TEST_DIR = tests

build:

	@if [ -f data_x_debug.csv ]; then \
		rm data_x_debug.csv; \
	fi
	@if [ -f data_x_debug.csv ]; then \
		data_x_debug.csv; \
	fi
	@if [ -f extra_data_point.csv ]; then \
		rm extra_data_point.csv; \
	fi
	@if [ -f extra_data_x.csv ]; then \
		rm extra_data_x.csv; \
	fi

	@if [ -f table.html ]; then \
		rm table.html; \
	fi

	@if [ -f core_data.duckdb ]; then \
		rm core_data.duckdb; \
	fi

	@if [ -f matches.csv ]; then \
		echo CAREFUL ! matches.csv is rm each time make is called ! Rm the rm before final push; \
		rm matches.csv; \
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
