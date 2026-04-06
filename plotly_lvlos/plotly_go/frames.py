from __future__ import annotations
from typing import TYPE_CHECKING
from pathlib import Path

import numpy as np
import polars as pl
import plotly.graph_objects as go

if TYPE_CHECKING:
    from .PlotlyGoBuilder import PlotlyGoBuilder


GINI_COLOR_NULL = "#aaaaaa"

GINI_COLORSCALE = [
    (0.0, (0, 176, 80)),
    (0.35, (255, 255, 0)),
    (0.65, (255, 128, 0)),
    (1.0, (255, 0, 0)),
]


def _label_from_path(filepath: str) -> str:
    return Path(filepath).stem.replace("_", " ").capitalize()


def _interpolate_color(t: float) -> str:
    for i in range(len(GINI_COLORSCALE) - 1):
        t0, c0 = GINI_COLORSCALE[i]
        t1, c1 = GINI_COLORSCALE[i + 1]
        if t0 <= t <= t1:
            ratio = (t - t0) / (t1 - t0)
            r = int(c0[0] + ratio * (c1[0] - c0[0]))
            g = int(c0[1] + ratio * (c1[1] - c0[1]))
            b = int(c0[2] + ratio * (c1[2] - c0[2]))
            return f"#{r:02x}{g:02x}{b:02x}"
    return GINI_COLOR_NULL


def _gini_to_colors(gini_values: np.ndarray) -> list[str]:
    colors = []
    for v in gini_values:
        if np.isnan(v):
            colors.append(GINI_COLOR_NULL)
        else:
            t = float(np.clip(v / 100.0, 0.0, 1.0))
            colors.append(_interpolate_color(t))
    return colors


def build_plotly_frames(builder: "PlotlyGoBuilder") -> None:
    df: pl.DataFrame = pl.from_arrow(
        builder.con.execute(f"""
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
            CAST(extra_data_x AS DOUBLE)                                    AS gini
        FROM core_data
        ORDER BY overlap_value, {builder.entity_column_label}
    """).fetch_arrow_table()
    )  # type: ignore

    analytics_df: pl.DataFrame = pl.from_arrow(
        builder.con.execute(f"""
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
    """).fetch_arrow_table()
    )  # type: ignore

    lin_df = analytics_df.filter(pl.col("scale") == "lin")
    log_df = analytics_df.filter(pl.col("scale") == "log")

    builder.analytics_years = lin_df["overlap_value"].to_numpy()

    indicators = ["pearson_r", "spearman_rho", "r_squared", "ols_slope", "ols_rmse"]
    for ind in indicators:
        lin_vals = lin_df[ind].to_numpy()
        log_vals = log_df[ind].to_numpy()
        builder.analytics[ind] = {
            "lin":      lin_vals,
            "log":      log_vals,
            "diff":     lin_vals - log_vals,
            "abs_diff": np.abs(lin_vals - log_vals),
        }

    sizeref: float = (
        2
        * df["size"].max()  # type: ignore
        / (builder.config_dict["visualization"]["max_marker_size"] ** 2)
    )

    x_lin: np.ndarray = df["data_x"].to_numpy()
    x_log: np.ndarray = df["data_x_log"].to_numpy()
    y: np.ndarray = df["data_y_plot"].to_numpy()
    size: np.ndarray = df["size"].to_numpy()
    opacity: np.ndarray = df["opacity"].to_numpy()
    gini: np.ndarray = df["gini"].to_numpy(allow_copy=True).astype(float)
    extra_data_point: np.ndarray = df["extra_data_point"].to_numpy()
    entity: list[str] = df["entity"].to_list()
    year: np.ndarray = df["overlap_value"].to_numpy()

    labels = builder.labels

    hovertemplate = (
        f"<b>%{{id}}</b><br>"
        f"{labels['data_x']} : %{{customdata[0]:,.0f}}<br>"
        f"{labels['data_y']} : %{{customdata[1]:.2f}}<br>"
        f"{labels['extra_data_point']} : %{{customdata[2]:,.0f}}<br>"
        f"{labels['extra_data_x']} : %{{customdata[3]:.1f}}<br>"
        f"<extra></extra>"
    )

    start: int = 0
    for frame_df in df.partition_by("overlap_value", maintain_order=True):
        n: int = frame_df.height
        end: int = start + n

        colors: list[str] = _gini_to_colors(gini[start:end])

        customdata = np.column_stack(
            [
                x_lin[start:end],
                y[start:end],
                extra_data_point[start:end],
                gini[start:end],
            ]
        )

        marker_common = dict(
            color=colors,
            size=size[start:end],
            opacity=opacity[start:end] * 0.8,
            sizeref=sizeref,
            sizemode="area",
        )

        frame: go.Frame = go.Frame(
            data=[
                go.Scatter(
                    x=x_lin[start:end],
                    y=y[start:end],
                    mode="markers",
                    marker=marker_common,
                    text=entity[start:end],
                    ids=entity[start:end],
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                ),
                go.Scatter(
                    x=x_log[start:end],
                    y=y[start:end],
                    mode="markers",
                    marker=marker_common,
                    text=entity[start:end],
                    ids=entity[start:end],
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                ),
            ],
            name=str(year[start]),
            traces=[0, 1],
        )
        builder.frames.append(frame)
        start = end
