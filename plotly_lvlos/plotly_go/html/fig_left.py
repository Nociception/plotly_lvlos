from __future__ import annotations
from typing import TYPE_CHECKING

import plotly.graph_objects as go
from plotly.subplots import make_subplots

if TYPE_CHECKING:
    from ..PlotlyGoBuilder import PlotlyGoBuilder


def build_fig_left(builder: "PlotlyGoBuilder") -> go.Figure:
    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.08)

    fig.add_trace(builder.frames[0].data[0], row=1, col=1)  # type: ignore
    fig.add_trace(builder.frames[0].data[1], row=2, col=1)  # type: ignore

    fig.frames = builder.frames

    fig.update_layout(
        autosize=True,
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
