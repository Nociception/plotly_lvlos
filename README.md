Project overview — motivation, scope and current state
General idea of the project

This project explores how the choice of scale on one axis (linear vs logarithmic) fundamentally alters the interpretation of statistical relationships, using animated scatter plots over time.

The core question is deliberately simple, but often underestimated:

How much of what we “see” in a scatter plot is a property of the data — and how much is an artefact of the scale we chose?

The project focuses on datasets such as:

GDP per capita

Life expectancy

Population

Inequality indicators (e.g. Gini coefficient)

These variables typically span several orders of magnitude. On a linear scale, most of the structure is visually compressed; on a logarithmic scale, different patterns emerge, correlations shift, and trends become legible in a different way.

The goal is therefore not merely to display two static plots, but to:

animate the data over time,

compute and display analytical metrics per year,

and allow a direct visual comparison between linear-scale and log-scale interpretations of the same underlying data.

Relation to the original project

In its original form, the project required users to:

clone the repository,

install dependencies,

create a virtual environment,

and run Python scripts locally.

The codebase was exploratory rather than architectural:

data validation and schema enforcement were minimal,

entity alignment logic was implicit and fragile,

missing or mismatched data was often silently dropped,

intermediate artefacts were not clearly defined or reusable.

As a result, despite the relevance of the underlying idea, the project was poorly suited for portfolio use or for review by non-technical audiences.

Objectives of the refactor

The refactored project explicitly addresses those limitations.

Its goals are to:

Produce a fully static output

a single HTML file,

no runtime backend,

no Python execution required to view the result,

directly openable in a browser.

Use Plotly for interactive and animated visualizations

smooth animations over time,

hover metadata,

dual linear / logarithmic representations,

explicit annotation of analytical metrics.

Treat data engineering as a first-class concern

strict schema validation,

explicit error and warning semantics,

deterministic handling of missing or misaligned data,

reproducible and inspectable intermediate artefacts.

Make the project readable and auditable

clear separation of pipeline phases,

explicit contracts between steps,

configuration-driven behaviour,

no hidden assumptions or “magic” joins.

The intended result is a project that is:

easy to run once,

easy to inspect,

easy to share,

and easy to reason about.

High-level pipeline overview

The project is structured as a multi-phase data pipeline.
Each phase produces explicit artefacts and enforces strict invariants.

Phase 0 — Configuration validation

A strict config.toml file defines:

project metadata,

data sources,

analytical parameters,

visualization parameters.

The configuration is validated against:

a closed declarative schema,

type constraints,

value bounds,

file existence rules (mandatory vs optional datasets).

No data is read at this stage.
Only structure, constraints and internal consistency are validated.

Phase 1 — Unified core data construction (entity resolution & alignment)

This phase is the conceptual and technical core of the project.

Objective

Build a single canonical analytical table that integrates all datasets — mandatory and optional — in one pass.

There is no longer a notion of “core” versus “enriched” data.
All datasets participate equally in the construction of the analytical table.

Role of the matches table

The matches table is the central alignment contract of the pipeline.

It defines, for each logical entity:

the reference entity label in data_x,

the corresponding entity labels in other datasets (or their absence),

the nature of each match (exact, fuzzy, unmatched),

an associated confidence score.

Unmatched entities are explicitly represented, rather than silently discarded.

This ensures that:

entity resolution is auditable and user-editable,

fuzzy matching is never irreversible,

missing or ambiguous entities are visible as data, not hidden control flow.

Construction logic

The unified construction phase performs the following steps:

Load and validate all input tables

Mandatory and optional datasets are treated uniformly.

Structural validation is applied consistently.

Tables failing validation are excluded if optional, or raise blocking errors if mandatory.

Resolve the entity space

data_x defines the reference entity axis.

Other datasets are aligned to it using the matches table.

Orphan entities are preserved explicitly as unmatched rows.

Resolve the temporal / numerical axis

Overlapping columns (typically years) are detected per table.

Tables may have different coverage; only the valid overlap is considered.

Wide tables are normalized into a long (entity_id, year) representation using SQL UNPIVOT.

Materialize the analytical table

All datasets are merged into a single long-format table.

Each row represents one (entity_id, year) pair.

Values from different datasets may be null independently.

Output artefact

The result of Phase 1 is a single canonical table, persisted as a parquet file:

entity_id | year | x_value | y_value | extra_data_point | extra_data_x


Key invariants:

No row is dropped due to partial missing data.

Optional datasets never invalidate the table.

Missing values are explicit and traceable.

Entity mismatches are handled upstream via the matches table, not hidden downstream.

This table is the only input for all subsequent analytical and visualization phases.

At the current stage of the project, this phase is essentially complete.

Error and warning semantics

Structural violations or invalid values in mandatory datasets produce blocking errors.

Issues in optional datasets (missing entities, missing years) produce warnings.

Entity resolution issues are diagnosed at the matches table level, not during merging.

Failures are therefore:

early,

localized,

explicit,

and explainable.

Conceptual simplification

This unified approach removes several ambiguities present in the earlier design:

Before	Now
Core vs enriched tables	Single canonical table
Implicit entity joins	Explicit matches table
Silent data loss	Explicit unmatched rows
Dataset-specific logic	Uniform integration

As a result, the pipeline is simpler to reason about, easier to debug, and more robust to future extensions.

Phase 2 — Analytical transformations

Rows with missing x_value or y_value are excluded from analysis.

Logarithmic transformation of x_value is computed.

Zero or negative values trigger blocking errors.

Per-year analytical metrics are computed once:

regression coefficients,

correlations,

dispersion metrics.

Years with insufficient data emit warnings and produce null metrics.

Phase 3 — Frame materialization

Metric tables are materialized explicitly.

Plotly animation frames (linear and logarithmic) are precomputed.

No computation occurs at visualization time.

Phase 4 — Final Plotly figure assembly

All frames are assembled into a single Plotly figure.

Layout, animation, annotations and interactions are configured.

The final output is exported as a fully static HTML file.

Current implementation status & working methodology

Already implemented

Strict, declarative config.toml schema.

Full configuration parsing and validation.

Explicit constraint handling.

File existence checks.

Construction of entity matching tables.

Unified core data construction using SQL and UNPIVOT.

Not yet implemented

Full analytical metric computation.

Final Plotly animation assembly.

Development follows a deliberately disciplined approach:

test-driven development using pytest,

incremental implementation with explicit failure modes,

strict separation between validation, transformation and visualization,

CI with formatting, linting and tests,

protected main branch with PR-based merging, even as a solo developer.

The emphasis is on correctness, explicitness and auditability rather than speed or cleverness.