from __future__ import annotations
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from plotly.subplots import make_subplots

if TYPE_CHECKING:
    from ..PlotlyGoBuilder import PlotlyGoBuilder


def build_fig_right(builder: "PlotlyGoBuilder") -> tuple[go.Figure, list[str]]:
    fig = make_subplots(
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
    years = builder.analytics_years

    fig.add_trace(
        go.Scatter(
            x=years, y=builder.analytics[default]["lin"],
            mode="lines+markers", line=dict(width=2),
            name=f"{default} lin",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=years, y=builder.analytics[default]["diff"],
            mode="lines+markers", line=dict(width=2),
            name=f"{default} diff",
        ),
        row=3, col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=years, y=builder.analytics[default]["log"],
            mode="lines+markers", line=dict(width=2),
            name=f"{default} log",
        ),
        row=5, col=1,
    )

    fig.update_yaxes(range=[0, 1], row=1, col=1)
    fig.update_yaxes(range=[0, 1], row=5, col=1)

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
                        builder.analytics[ind]["lin"].tolist(),
                        builder.analytics[ind]["diff"].tolist(),
                        builder.analytics[ind]["log"].tolist(),
                    ],
                    "x": [years.tolist()] * 3,
                    "name": [f"{label} lin", f"{label} diff", f"{label} log"],
                },
                [0, 1, 2],
            ],
        ))

    entities: list[str] = sorted(set(builder.frames[0].data[0].ids))  # type: ignore
    entity_buttons = [
        dict(method="skip", label="Track entity", args=[])
    ] + [
        dict(method="skip", label=entity, args=[])
        for entity in entities
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