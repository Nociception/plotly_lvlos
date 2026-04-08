from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

if TYPE_CHECKING:
    from ..PlotlyGoBuilder import PlotlyGoBuilder

COLOR_LIN = "#636efa"
COLOR_LOG = "#ef553b"
COLOR_DIFF = "#00cc96"


def _split_by_dominance(
    years: np.ndarray,
    abs_diff: np.ndarray,
    lin: np.ndarray,
    log: np.ndarray,
) -> tuple[list, list, list, list]:
    """
    Retourne deux séries (y_lin_dom, y_log_dom) où :
    - y_lin_dom[i] = abs_diff[i] si lin[i] >= log[i], sinon None
    - y_log_dom[i] = abs_diff[i] si log[i] >  lin[i], sinon None
    Les None créent des ruptures de ligne dans Plotly.
    """
    y_lin_dom: list = []
    y_log_dom: list = []

    for i in range(len(years)):
        if lin[i] >= log[i]:
            y_lin_dom.append(float(abs_diff[i]))
            y_log_dom.append(None)
        else:
            y_lin_dom.append(None)
            y_log_dom.append(float(abs_diff[i]))

    return years.tolist(), y_lin_dom, years.tolist(), y_log_dom


def build_fig_right(builder: "PlotlyGoBuilder") -> tuple[go.Figure, list[str]]:
    fig = make_subplots(
        rows=6,
        cols=1,
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
    years = builder.analytics_years

    fig.add_trace(
        go.Scatter(
            x=years,
            y=builder.analytics[default]["lin"],
            mode="lines+markers",
            line=dict(width=2, color=COLOR_LIN),
            name=f"{default} lin",
        ),
        row=1,
        col=1,
    )

    x_y, y_lin_dom, x_log, y_log_dom = _split_by_dominance(
        years,
        builder.analytics[default]["abs_diff"],
        builder.analytics[default]["lin"],
        builder.analytics[default]["log"],
    )

    fig.add_trace(
        go.Scatter(
            x=x_y,
            y=y_lin_dom,
            mode="lines+markers",
            line=dict(width=2, color=COLOR_LIN),
            name=f"{default} diff (lin>log)",
            connectgaps=False,
        ),
        row=3,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x_log,
            y=y_log_dom,
            mode="lines+markers",
            line=dict(width=2, color=COLOR_LOG),
            name=f"{default} diff (log>lin)",
            connectgaps=False,
        ),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=years,
            y=builder.analytics[default]["log"],
            mode="lines+markers",
            line=dict(width=2, color=COLOR_LOG),
            name=f"{default} log",
        ),
        row=5,
        col=1,
    )

    fig.update_yaxes(range=[0, 1], row=1, col=1)
    fig.update_yaxes(range=[0, 1], row=5, col=1)

    indicator_labels = {
        "pearson_r": "Pearson r",
        "spearman_rho": "Spearman ρ",
        "r_squared": "R²",
        "ols_slope": "Pente OLS",
        "ols_rmse": "RMSE OLS",
    }
    indicator_buttons = []
    for ind, label in indicator_labels.items():
        _, y_lin_dom, _, y_log_dom = _split_by_dominance(
            years,
            builder.analytics[ind]["abs_diff"],
            builder.analytics[ind]["lin"],
            builder.analytics[ind]["log"],
        )
        indicator_buttons.append(
            dict(
                method="restyle",
                label=label,
                args=[
                    {
                        "y": [
                            builder.analytics[ind]["lin"].tolist(),
                            y_lin_dom,
                            y_log_dom,
                            builder.analytics[ind]["log"].tolist(),
                        ],
                        "x": [years.tolist()] * 4,
                        "name": [
                            f"{label} lin",
                            f"{label} diff (lin>log)",
                            f"{label} diff (log>lin)",
                            f"{label} log",
                        ],
                        "line.color": [COLOR_LIN, COLOR_LIN, COLOR_LOG, COLOR_LOG],
                    },
                    [0, 1, 2, 3],
                ],
            )
        )

    entities: list[str] = sorted(set(builder.frames[0].data[0].ids))  # type: ignore
    entity_buttons = [dict(method="skip", label="Track entity", args=[])] + [
        dict(method="skip", label=entity, args=[]) for entity in entities
    ]

    fig.update_layout(
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

    return fig, entities
