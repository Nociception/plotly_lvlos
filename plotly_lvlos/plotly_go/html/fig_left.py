from __future__ import annotations
from typing import TYPE_CHECKING
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from .fig_right import COLOR_LIN, COLOR_LOG

if TYPE_CHECKING:
    from ..PlotlyGoBuilder import PlotlyGoBuilder


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def build_fig_left(builder: "PlotlyGoBuilder") -> go.Figure:
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.08)

    fig.add_trace(builder.frames[0].data[0], row=1, col=1)  # type: ignore
    fig.add_trace(builder.frames[0].data[1], row=2, col=1)  # type: ignore

    fig.frames = builder.frames

    labels = builder.labels

    # Calcul des tickvals log — puissances de 10 couvrant la plage de data_x
    all_x = np.concatenate([
        frame.data[0].x for frame in builder.frames  # type: ignore
    ])
    x_min = np.nanmin(all_x)
    x_max = np.nanmax(all_x)
    log_min = int(np.floor(np.log10(x_min)))
    log_max = int(np.ceil(np.log10(x_max)))
    log_tickvals = list(range(log_min, log_max + 1))
    log_ticktext = [
        f"{10**v:,.0f}" for v in log_tickvals
    ]

    fig.update_layout(
        autosize=True,
        annotations=[
            dict(
                text="LIN",
                xref="x domain",
                yref="y domain",
                x=0.5,
                y=0.5,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(size=200, color=_hex_to_rgba(COLOR_LIN, 0.15)),
            ),
            dict(
                text="LOG",
                xref="x2 domain",
                yref="y2 domain",
                x=0.5,
                y=0.5,
                xanchor="center",
                yanchor="middle",
                showarrow=False,
                font=dict(size=200, color=_hex_to_rgba(COLOR_LOG, 0.15)),
            ),
        ],
        sliders=[
            dict(
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
                    for frame in builder.frames
                ],
            )
        ],
    )

    # Légendes axes — subplot lin (row=1)
    fig.update_xaxes(title_text=labels["data_x"], row=1, col=1)
    fig.update_yaxes(title_text=labels["data_y"], row=1, col=1)

    # Légendes axes — subplot log (row=2)
    # L'axe X affiche log10(data_x) → on reconvertit les ticks en valeurs brutes
    fig.update_xaxes(
        title_text=f"{labels['data_x']} (log)",
        tickvals=log_tickvals,
        ticktext=log_ticktext,
        row=2, col=1,
    )
    fig.update_yaxes(title_text=labels["data_y"], row=2, col=1)

    return fig