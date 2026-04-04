import duckdb
import plotly.graph_objects as go
import numpy as np
import polars as pl
from plotly.subplots import make_subplots
import json


class PlotlyGoBuilder:
    def __init__(self, con: duckdb.DuckDBPyConnection, config_dict: dict) -> None:
        self.con = con
        self.config_dict = config_dict
        self.overlap_column_label = self.config_dict["data"]["overlap_column"]
        self.entity_column_label = self.config_dict["data"]["entity_column"]
        self.frames: list[go.Frame] = []

    def build(self) -> None:
        self.build_analytics()
        self.build_plotly_frames()
        self.build_html()


    def build_analytics(self) -> None:
        self.con.execute("DROP TABLE IF EXISTS analytics")
        self.con.execute(f"""
            CREATE TABLE analytics AS
            
                WITH
                    cleaned AS (
                        SELECT
                            {self.entity_column_label},
                            {self.overlap_column_label},
                            data_x,
                            data_x_log,
                            data_y
                        FROM core_data
                        WHERE
                            data_x IS NOT NULL
                            AND data_y IS NOT NULL
                    ),

                    oc_agg AS (
                        SELECT
                            {self.overlap_column_label},
                            avg(data_y)                         AS avg_y,
                            avg(data_x)                         AS avg_x_lin,
                            avg(data_x_log)                     AS avg_x_log,
                            covar_pop(data_x, data_y)           AS covar_lin,
                            covar_pop(data_x_log, data_y)       AS covar_log,
                            var_pop(data_x)                     AS var_x_lin,
                            var_pop(data_x_log)                 AS var_x_log
                        FROM cleaned
                        GROUP BY {self.overlap_column_label}
                    ),

                    ranked AS (
                        SELECT
                            c.{self.overlap_column_label},
                            c.data_x,
                            c.data_x_log,
                            c.data_y,

                            RANK() OVER (
                                PARTITION BY c.{self.overlap_column_label}
                                ORDER BY c.data_x
                            ) AS rank_x,
                            RANK() OVER (
                                PARTITION BY c.{self.overlap_column_label}
                                ORDER BY c.data_y
                            ) AS rank_y,

                            oca.covar_lin / NULLIF(oca.var_x_lin, 0)                               AS slope_lin,
                            oca.avg_y - (oca.covar_lin / NULLIF(oca.var_x_lin, 0)) * oca.avg_x_lin AS intercept_lin,

                            oca.covar_log / NULLIF(oca.var_x_log, 0)                               AS slope_log,
                            oca.avg_y - (oca.covar_log / NULLIF(oca.var_x_log, 0)) * oca.avg_x_log AS intercept_log

                        FROM
                            cleaned AS c
                            JOIN oc_agg AS oca
                                ON oca.{self.overlap_column_label} = c.{self.overlap_column_label}
                    ),

                    lin_scale AS (
                        SELECT
                            {self.overlap_column_label},
                            'lin'                                                               AS scale,
                            corr(data_x, data_y)                                                AS pearson_r,
                            corr(rank_x, rank_y)                                                AS spearman_rho,
                            avg(slope_lin)                                                      AS ols_slope,
                            avg(intercept_lin)                                                  AS ols_intercept,
                            POWER(corr(data_x, data_y), 2)                                      AS r_squared,
                            SQRT(avg(POWER(data_y - (slope_lin * data_x + intercept_lin), 2)))  AS ols_rmse,
                            COUNT(*)                                                            AS n_entities
                        FROM ranked
                        GROUP BY {self.overlap_column_label}
                    ),

                    log_scale AS (
                        SELECT
                            {self.overlap_column_label},
                            'log'                                                                       AS scale,
                            corr(data_x_log, data_y)                                                    AS pearson_r,
                            corr(rank_x, rank_y)                                                        AS spearman_rho,
                            avg(slope_log)                                                              AS ols_slope,
                            avg(intercept_log)                                                          AS ols_intercept,
                            POWER(corr(data_x_log, data_y), 2)                                          AS r_squared,
                            SQRT(avg(POWER(data_y - (slope_log * data_x_log + intercept_log), 2)))      AS ols_rmse,
                            COUNT(*)                                                                    AS n_entities
                        FROM ranked
                        GROUP BY {self.overlap_column_label}
                    )

                SELECT * FROM lin_scale
                UNION ALL
                SELECT * FROM log_scale
                ORDER BY
                    {self.overlap_column_label},
                    scale
            """)
        # print(self.con.execute("SELECT * FROM analytics").fetchdf())


    def build_plotly_frames(self) -> None:

        df: pl.DataFrame = pl.from_arrow(self.con.execute(f"""
            SELECT
                {self.entity_column_label} AS entity,
                {self.overlap_column_label} AS overlap_value,
                data_x,
                data_x_log,
                COALESCE(
                    LAST_VALUE(data_y IGNORE NULLS)
                        OVER (
                            PARTITION BY {self.entity_column_label}
                            ORDER BY {self.overlap_column_label}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                        ),
                    FIRST_VALUE(data_y IGNORE NULLS)
                        OVER (
                            PARTITION BY {self.entity_column_label}
                            ORDER BY {self.overlap_column_label}
                            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
                        )
                )                                                               AS data_y_plot,
                CAST(
                    CASE WHEN data_y IS NULL THEN 0 ELSE 1 END
                AS DOUBLE)                                                      AS opacity,
                extra_data_point,
                GREATEST(
                    SQRT(extra_data_point),
                    {self.config_dict["visualization"]["min_marker_size"]}
                )                                                               AS size,
                extra_data_x
            FROM core_data
            ORDER BY overlap_value, {self.entity_column_label}
        """).fetch_arrow_table())  # type: ignore

        analytics_df: pl.DataFrame = pl.from_arrow(self.con.execute(f"""
            SELECT
                {self.overlap_column_label} AS overlap_value,
                scale,
                pearson_r,
                spearman_rho,
                r_squared,
                ols_slope,
                ols_rmse
            FROM analytics
            ORDER BY overlap_value, scale
        """).fetch_arrow_table())  # type: ignore

        lin_df = analytics_df.filter(pl.col("scale") == "lin")
        log_df = analytics_df.filter(pl.col("scale") == "log")

        self.analytics_years: np.ndarray = lin_df["overlap_value"].to_numpy()

        indicators = ["pearson_r", "spearman_rho", "r_squared", "ols_slope", "ols_rmse"]
        self.analytics: dict[str, dict[str, np.ndarray]] = {}
        for ind in indicators:
            lin_vals = lin_df[ind].to_numpy()
            log_vals = log_df[ind].to_numpy()
            self.analytics[ind] = {
                "lin":  lin_vals,
                "log":  log_vals,
                "diff": lin_vals - log_vals,
            }

        sizeref: float = (
            2 * df["size"].max()  # type: ignore
            / (self.config_dict["visualization"]["max_marker_size"] ** 2)
        )

        x_lin: np.ndarray = df["data_x"].to_numpy()
        x_log: np.ndarray = df["data_x_log"].to_numpy()
        y: np.ndarray = df["data_y_plot"].to_numpy()
        size: np.ndarray = df["size"].to_numpy()
        opacity: np.ndarray = df["opacity"].to_numpy()
        entity: list[str] = df["entity"].to_list()
        year: np.ndarray = df["overlap_value"].to_numpy()

        start: int = 0
        for frame_df in df.partition_by("overlap_value", maintain_order=True):
            n: int = frame_df.height
            end: int = start + n
            frame: go.Frame = go.Frame(
                data=[
                    go.Scatter(
                        x=x_lin[start:end],
                        y=y[start:end],
                        mode="markers",
                        marker=dict(
                            size=size[start:end],
                            opacity=opacity[start:end] * 0.8,
                            sizeref=sizeref,
                            sizemode="area",
                        ),
                        text=entity[start:end],
                        ids=entity[start:end],
                    ),
                    go.Scatter(
                        x=x_log[start:end],
                        y=y[start:end],
                        mode="markers",
                        marker=dict(
                            size=size[start:end],
                            opacity=opacity[start:end] * 0.8,
                            sizeref=sizeref,
                            sizemode="area",
                        ),
                        text=entity[start:end],
                        ids=entity[start:end],
                    ),
                ],
                name=str(year[start]),
                traces=[0, 1],
            )
            self.frames.append(frame)
            start = end


    def build_html(self) -> None:

        fig_left = make_subplots(rows=2, cols=1, vertical_spacing=0.08)

        first_frame = self.frames[0]
        fig_left.add_trace(first_frame.data[0], row=1, col=1)
        fig_left.add_trace(first_frame.data[1], row=2, col=1)

        fig_left.frames = self.frames

        fig_left.update_layout(
            autosize=True,
            sliders=[dict(
                active=0,
                steps=[
                    dict(
                        method="animate",
                        label=frame.name,
                        args=[
                            [frame.name],
                            dict(
                                mode="immediate",
                                frame=dict(duration=80, redraw=True),
                                transition=dict(duration=0),
                            ),
                        ],
                    )
                    for frame in self.frames
                ],
            )],
        )

        fig_right = make_subplots(
            rows=6, cols=1,
            specs=[
                [{"rowspan": 2}],
                [None],
                [{"rowspan": 2}],
                [None],
                [{"rowspan": 2}],
                [None],
            ],
            vertical_spacing=0.08,
        )

        default = "pearson_r"
        years = self.analytics_years

        fig_right.add_trace(
            go.Scatter(
                x=years, y=self.analytics[default]["lin"],
                mode="lines+markers", line=dict(width=2),
                name=f"{default} lin",
            ),
            row=1, col=1,
        )
        fig_right.add_trace(
            go.Scatter(
                x=years, y=self.analytics[default]["diff"],
                mode="lines+markers", line=dict(width=2),
                name=f"{default} diff",
            ),
            row=3, col=1,
        )
        fig_right.add_trace(
            go.Scatter(
                x=years, y=self.analytics[default]["log"],
                mode="lines+markers", line=dict(width=2),
                name=f"{default} log",
            ),
            row=5, col=1,
        )

        fig_right.update_yaxes(range=[0, 1], row=1, col=1)
        fig_right.update_yaxes(range=[0, 1], row=5, col=1)

        indicator_labels = {
            "pearson_r":    "Pearson r",
            "spearman_rho": "Spearman ρ",
            "r_squared":    "R²",
            "ols_slope":    "Pente OLS",
            "ols_rmse":     "RMSE OLS",
        }

        indicator_buttons = []
        for ind, label in indicator_labels.items():
            indicator_buttons.append(dict(
                method="restyle",
                label=label,
                args=[
                    {
                        "y": [
                            self.analytics[ind]["lin"].tolist(),
                            self.analytics[ind]["diff"].tolist(),
                            self.analytics[ind]["log"].tolist(),
                        ],
                        "x": [years.tolist()] * 3,
                        "name": [f"{label} lin", f"{label} diff", f"{label} log"],
                    },
                    [0, 1, 2],
                ],
            ))

        entities: list[str] = sorted(set(self.frames[0].data[0].ids))  # type: ignore
        entity_buttons = [
            dict(method="skip", label="Track entity", args=[])
        ] + [
            dict(method="skip", label=entity, args=[])
            for entity in entities
        ]

        fig_right.update_layout(
            autosize=True,
            updatemenus=[
                dict(
                    type="dropdown",
                    direction="down",
                    active=0,
                    x=0.5,
                    xanchor="center",
                    y=1.05,
                    yanchor="bottom",
                    buttons=indicator_buttons,
                ),
                dict(
                    type="dropdown",
                    direction="up",
                    active=0,
                    x=0.5,
                    xanchor="center",
                    y=-0.05,
                    yanchor="top",
                    buttons=entity_buttons,
                ),
            ],
        )

        html_left  = fig_left.to_html(full_html=False, include_plotlyjs="cdn")
        html_right = fig_right.to_html(full_html=False, include_plotlyjs=False)

        entities_json = json.dumps(entities)

        tracker_js = f"""
        <script>
        (function() {{
            const DEFAULT_COLOR = '#636efa';
            const HIGHLIGHT_COLOR = '#00e5ff';
            const HIGHLIGHT_SIZE_FACTOR = 1.8;

            let selectedEntity = null;

            function getLeftDiv() {{
                return document.querySelector('.fig-left .plotly-graph-div');
            }}

            function getRightDiv() {{
                return document.querySelector('.fig-right .plotly-graph-div');
            }}

            function applyHighlight() {{
                const gd = getLeftDiv();
                if (!gd || !gd._fullData) return;

                [0, 1].forEach(function(traceIdx) {{
                    const trace = gd._fullData[traceIdx];
                    if (!trace || !trace.ids) return;

                    const ids = trace.ids;
                    const baseSizes = gd.data[traceIdx].marker.size;

                    const colors = ids.map(function(id) {{
                        return id === selectedEntity ? HIGHLIGHT_COLOR : DEFAULT_COLOR;
                    }});

                    const sizes = Array.isArray(baseSizes)
                        ? baseSizes.map(function(s, i) {{
                            return ids[i] === selectedEntity
                                ? s * HIGHLIGHT_SIZE_FACTOR
                                : s;
                        }})
                        : baseSizes;

                    const lineWidths = ids.map(function(id) {{
                        return id === selectedEntity ? 3 : 0;
                    }});

                    const lineColors = ids.map(function(id) {{
                        return id === selectedEntity ? '#000000' : 'rgba(0,0,0,0)';
                    }});

                    Plotly.restyle(gd, {{
                        'marker.color': [colors],
                        'marker.size': [sizes],
                        'marker.line.width': [lineWidths],
                        'marker.line.color': [lineColors],
                    }}, [traceIdx]);
                }});
            }}

            function hookAnimationEnd() {{
                const gd = getLeftDiv();
                if (!gd) return;
                gd.on('plotly_animated', function() {{
                    applyHighlight();
                }});
            }}

            function hookEntityMenu() {{
                const gd = getRightDiv();
                if (!gd) return;

                gd.on('plotly_buttonclicked', function(data) {{
                    if (data.menu._index !== 1) return;

                    const label = data.button.label;
                    selectedEntity = (label === 'Track entity') ? null : label;
                    applyHighlight();
                }});
            }}

            window.addEventListener('load', function() {{
                setTimeout(function() {{
                    window.dispatchEvent(new Event('resize'));
                    hookAnimationEnd();
                    hookEntityMenu();
                }}, 100);
            }});
        }})();
        </script>
        """

        html = f"""<!DOCTYPE html>
        <html>
            <head>
                <meta charset="utf-8">
                <style>
                    html, body {{
                        margin: 0;
                        height: 100%;
                        overflow: hidden;
                    }}
                    body {{
                        display: flex;
                    }}
                    .fig-left {{
                        flex: 3;
                        min-width: 0;
                        height: 100vh;
                    }}
                    .fig-right {{
                        flex: 1;
                        min-width: 0;
                        height: 100vh;
                    }}
                    .fig-left > div, .fig-right > div {{
                        width: 100% !important;
                        height: 100% !important;
                    }}
                </style>
            </head>
            <body>
                <div class="fig-left">{html_left}</div>
                <div class="fig-right">{html_right}</div>
                {tracker_js}
            </body>
        </html>"""

        with open("plotly_lvlos.html", "w") as f:
            f.write(html)