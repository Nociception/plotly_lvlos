# 📊 plotly-lvlos — Lin vs Log on Scatter

> An interactive [Gapminder like](https://www.gapminder.org/tools/#$chart-type=bubbles&url=v2) data visualization tool that animates scatter plots across time and compares the effect of linear vs. logarithmic x-axis scaling on statistical indicators.

🌐 **[Live demo](https://nociception.github.io/plotly_lvlos/)**


<video src="https://github.com/user-attachments/assets/91e2179e-b168-46dd-a320-a4c575566524" autoplay muted loop playsinline style="max-width:100%;">
</video>


---

## What this project shows

Two animated scatter plots run in parallel — one with a linear x-axis, one with a logarithmic x-axis — on the same dataset. A side panel tracks how key statistical indicators (Pearson r, Spearman ρ, R², OLS slope, OLS RMSE) evolve over time, and how differently they behave depending on the scale chosen.

The takeaway: **scale is not neutral**. The choice between linear and logarithmic x-axis can dramatically change what a statistical indicator tells you — and this tool makes that visible, frame by frame.

The current dataset maps GDP per capita (data_x) against life expectancy (data_y) across 195 countries from 1800 to 2050. Point size encodes population (extra_data_point); color encodes the Gini coefficient (extra_data_x) when available.

> This tool is dataset-agnostic: any wide-format CSV dataset can be substituted. See [Swapping the dataset](#swapping-the-dataset).

---

## Features

- Animated scatter plots (linear & log scale) with a shared time slider
- Real-time statistical indicators panel with dropdown selector
- Entity tracker: highlight and follow any country across frames
- extra_data_x color gradient on data points (green → yellow → orange → red)
- Fully static HTML output — no server required, GitHub Pages compatible

---

## Tech stack

| Layer | Tool | Why |
|---|---|---|
| SQL analytics | **DuckDB** | In-process analytical SQL engine — native window functions, UNPIVOT, direct Arrow integration. Purpose-built for this kind of aggregation workload, unlike SQLite (transactional) or pandas (verbose and slower on columnar ops). |
| DataFrame | **Polars** | Rust-backed, parallel execution, consistently faster than pandas. Zero-copy integration with DuckDB via Apache Arrow. |
| Visualization | **Plotly (Graph Objects)** | Only library offering the level of control required: animated frames, custom JS hooks, multi-subplot layout, static HTML export. |
| Build | **uv** | Fast, reproducible Python environment management. |
| Output | **Static HTML** | Self-contained, no backend, deployable anywhere. |

---

## Quickstart

**Requirements:** [uv](https://github.com/astral-sh/uv)
```bash
git clone https://github.com/nociception/plotly_lvlos.git
cd plotly_lvlos
make
```

The outputs are :
- core_data.csv: a long-format CSV, result of the merge of the input wide-format CSVs.
- self-contained HTML file. Open it in any modern browser.

> **Note for 42 school machines:** `uv` requires write access to `~/.local`. You may need to adjust `$HOME`, or run inside a Docker container or VM.

---

## Swapping the dataset

All data parameters are defined in `config/config.toml`:
```toml
[data]
x_file                    = "data/your_x_data.csv"
y_file                    = "data/your_y_data.csv"
extra_data_point_file     = "data/your_size_data.csv"
extra_data_x_file         = "data/your_color_data.csv"
entity_column             = "country"
overlap_column            = "year"
```

Input files must be in **wide format**: entities as rows, time periods as columns. The code handles alignment, unpivoting, and missing values automatically.

---

## Statistical indicators computed

All indicators are computed independently for linear and log x-axis, per time period, across all entities with available data.

| Indicator | Description |
|---|---|
| **Pearson r** | Linear correlation between x and y |
| **Spearman ρ** | Rank-based correlation — robust to outliers |
| **R²** | Coefficient of determination |
| **OLS slope** | Slope of the ordinary least squares regression line |
| **OLS RMSE** | Root mean square error of OLS residuals |

The middle panel displays the absolute difference between the linear and log values of the selected indicator, colored by which scale produces the larger value.

---

## About

This project was built as part of the [42 Nice](https://42nice.fr) curriculum.

It serves as a practical demonstration of:

- Python : OOP, modular architecture
- Data engineering: polars, duckDB's SQL, fuzzy matching for entity tracking, wide-to-long data transformation
- Analytical SQL
- Data-aware visualization design

📬 [GitHub profile](https://github.com/nociception)

---

## License

[MIT](LICENSE)
