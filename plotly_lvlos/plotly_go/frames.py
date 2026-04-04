from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np
import polars as pl
import plotly.graph_objects as go

if TYPE_CHECKING:
    from .PlotlyGoBuilder import PlotlyGoBuilder


def build_plotly_frames(builder: "PlotlyGoBuilder") -> None:

    df: pl.DataFrame = pl.from_arrow(builder.con.execute(f"""
        SELECT
            {builder.entity_column_label} AS entity,
            {builder.overlap_column_label} AS overlap_value,
            data_x,
            data_x_log,
            COALESCE(
                LAST_VALUE(data_y IGNORE NULLS)
                    OVER (
                        PARTITION BY {builder.entity_column_label}
                        ORDER BY {builder.overlap_column_label}
                        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ),
                FIRST_VALUE(data_y IGNORE NULLS)
                    OVER (
                        PARTITION BY {builder.entity_column_label}
                        ORDER BY {builder.overlap_column_label}
                        ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
                    )
            )                                                               AS data_y_plot,
            CAST(
                CASE WHEN data_y IS NULL THEN 0 ELSE 1 END
            AS DOUBLE)                                                      AS opacity,
            extra_data_point,
            GREATEST(
                SQRT(extra_data_point),
                {builder.config_dict["visualization"]["min_marker_size"]}
            )                                                               AS size,
            extra_data_x
        FROM core_data
        ORDER BY overlap_value, {builder.entity_column_label}
    """).fetch_arrow_table())  # type: ignore

    analytics_df: pl.DataFrame = pl.from_arrow(builder.con.execute(f"""
        SELECT
            {builder.overlap_column_label} AS overlap_value,
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

    builder.analytics_years = lin_df["overlap_value"].to_numpy()

    indicators = ["pearson_r", "spearman_rho", "r_squared", "ols_slope", "ols_rmse"]
    for ind in indicators:
        lin_vals = lin_df[ind].to_numpy()
        log_vals = log_df[ind].to_numpy()
        builder.analytics[ind] = {
            "lin":  lin_vals,
            "log":  log_vals,
            "diff": lin_vals - log_vals,
        }

    sizeref: float = (
        2 * df["size"].max()  # type: ignore
        / (builder.config_dict["visualization"]["max_marker_size"] ** 2)
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
        builder.frames.append(frame)
        start = end