Choice : so far, handle only csv input datafiles


Why a materialized core table?

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
