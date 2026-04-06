from __future__ import annotations
from typing import TYPE_CHECKING
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

    return fig