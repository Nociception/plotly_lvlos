import duckdb
import plotly.graph_objects as go
import numpy as np
import polars as pl
from plotly.subplots import make_subplots


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
        print(self.con.execute("SELECT * FROM analytics").fetchdf())


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
                pearson_r
            FROM analytics
            ORDER BY overlap_value, scale
        """).fetch_arrow_table())  # type: ignore

        lin_df = analytics_df.filter(pl.col("scale") == "lin")
        log_df = analytics_df.filter(pl.col("scale") == "log")

        self.corr_year: np.ndarray = lin_df["overlap_value"].to_numpy()
        self.corr_lin: np.ndarray  = lin_df["pearson_r"].to_numpy()
        self.corr_log: np.ndarray  = log_df["pearson_r"].to_numpy()

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
                    go.Scatter(
                        x=self.corr_year,
                        y=self.corr_lin,
                        mode="lines+markers",
                        line=dict(width=2),
                    ),
                    go.Scatter(
                        mode="lines+markers",
                    ),
                    go.Scatter(
                        x=self.corr_year,
                        y=self.corr_log,
                        mode="lines+markers",
                        line=dict(width=2),
                    ),
                ],
                name=str(year[start]),
                traces=[0, 1, 2, 3, 4],
            )
            self.frames.append(frame)
            start = end

    def build_html(self) -> None:

        fig = make_subplots(
            rows=6,
            cols=4,
            specs=[
                [{"rowspan": 3, "colspan": 3}, None, None, {"rowspan": 2}],
                [None, None, None, None],
                [None, None, None, {"rowspan": 2}],
                [{"rowspan": 3, "colspan": 3}, None, None, None],
                [None, None, None, {"rowspan": 2}],
                [None, None, None, None],
            ],
            column_widths=[0.25, 0.25, 0.25, 0.25],
            horizontal_spacing=0.06,
            vertical_spacing=0.08,
        )

        first_frame = self.frames[0]

        fig.add_trace(first_frame.data[0], row=1, col=1)  # type: ignore
        fig.add_trace(first_frame.data[1], row=4, col=1)  # type: ignore


        fig.add_trace(
            go.Scatter(
                x=self.corr_year,
                y=self.corr_lin,
                mode="lines+markers",
                line=dict(width=2),
                name="pearson_lin",
            ),
            row=1,
            col=4,
        )


        fig.add_trace(
            go.Scatter(mode="lines+markers", name="corr_diff"),
            row=3,
            col=4,
        )


        fig.add_trace(
            go.Scatter(
                x=self.corr_year,
                y=self.corr_log,
                mode="lines+markers",
                line=dict(width=2),
                name="pearson_log",
            ),
            row=5,
            col=4,
        )

        fig.update_xaxes(
            range=[self.corr_year.min(), self.corr_year.max()],
            row=1,
            col=4,
        )

        fig.update_xaxes(
            range=[self.corr_year.min(), self.corr_year.max()],
            row=5,
            col=4,
        )

        fig.update_xaxes(autorange=True, row=1, col=4)
        fig.update_xaxes(autorange=True, row=5, col=4)

        fig.frames = self.frames


        slider_steps = [
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
        ]


        fig.update_layout(
            sliders=[dict(active=0, steps=slider_steps)],
        )

        fig.write_html("plotly_lvlos.html", auto_play=True)
