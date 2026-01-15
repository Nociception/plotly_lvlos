PLOTLY-LVLOS

Plotly-LVLOS is a Python project for generating interactive visualizations comparing linear and logarithmic x-scales on time series.
This branch load_parse_config.toml focuses on loading and validating configuration.

Table of contents:

Installation

Project structure

Configuration

Usage

Validation and constraints

Tests

Future work

CONFIGURATION

The project relies on a config.toml file.
The expected sections and keys are defined in CONFIG_TOML_DICT_SCHEMA.

Example minimal config.toml:

[project]
name = "plotly-lvlos"
description = "Animated comparison of linear vs logarithmic x-scale effects"
output_dir = "build"

[data]
x_file = "data/x.csv"
y_file = "data/y.csv"
extra_data_point_file = "data/edpf.csv"
extra_data_x_file = "data/edxf.csv"
entity_column = "country"
overlap_column = "year"

[analysis]
min_points_per_year = 5

[visualization]
width = 1200
height = 800
frame_duration_ms = 300
transition_duration_ms = 0

USAGE

from plotly_lvlos.build import build

build("config.toml")

Current pipeline steps:

Load the TOML file (load_config)

Validate sections, keys and values (parse_config_toml_dict, validate_config_values)

Check existence of required files (validate_files_exist)

Future steps: data loading and HTML generation using Plotly.

VALIDATION AND CONSTRAINTS

Types, string lengths, and numeric bounds are checked using CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.

Mandatory files must exist, optional files raise a warning if missing.

Violations raise specific exceptions:

ConfigConstraintError

ConfigFileNotFoundFatalError

ConfigFileNotFoundWarning

TESTS

Uses pytest, covering:

Required sections and keys

String constraints (len_min, len_max, strip)

Numeric constraints (min, max)

File existence

Run tests:

pytest tests --disable-warnings -v

FUTURE WORK

Load and merge CSV data files

Generate interactive Plotly HTML output from data

Optionally add filtering and animation features





















# Choice : so far, handle only csv input datafiles


# Why a materialized core table?

This project relies on a materialized core table as the primary analytical dataset used to generate Plotly animation frames.

This is a deliberate design choice, not a technical limitation.

Alternative approach: dynamic joins

An alternative design would consist in keeping each dataset (GDP, life expectancy, population, inequality, etc.) in separate normalized tables and generating each animation frame through SQL joins based on a shared entity_id and year.

This approach is perfectly viable and would typically involve:

a canonical entities table produced after fuzzy matching,

one table per source dataset in long format,

per-year SQL queries joining the relevant tables to assemble frame data on demand.

Why this approach was not retained

While technically correct, this fully normalized approach was intentionally not selected for the following reasons:

Analytical clarity
A single long-form core table provides an explicit, self-contained analytical dataset where all relevant variables are immediately visible and interpretable.

Explorability
The core table can be reused directly for ad-hoc analysis, validation, or alternative visualizations without re-running joins or relying on pipeline-specific logic.

Deterministic build pipeline
All joins, alignments, transformations (including derived features such as log_gdp) are resolved once at build time, producing a stable and reproducible dataset.

Separation of concerns
The visualization layer operates on precomputed frames derived from the core table, while data integration complexity remains isolated in earlier pipeline stages.

Project intent
As a showcase project, the objective is not only to demonstrate the ability to perform joins and normalization, but also to justify architectural choices based on downstream usage and maintainability.

Scope and implications

The core table is not intended to model a transactional or normalized production system.
It is a materialized analytical artifact, designed to:

support efficient frame generation,

simplify reasoning about temporal data completeness,

and remain reusable for further exploratory analysis if the project is extended.

This choice reflects a common data engineering trade-off: preferring a denormalized analytical dataset when it improves clarity, reusability, and downstream simplicity without introducing meaningful cost or ambiguity.


# why a public repo during dev
because rule set is not effective with a free plan on a private repo