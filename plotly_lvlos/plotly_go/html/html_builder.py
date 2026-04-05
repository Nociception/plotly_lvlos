from __future__ import annotations
from typing import TYPE_CHECKING

from .fig_left import build_fig_left
from .fig_right import build_fig_right
from .tracker_js import build_tracker_js

if TYPE_CHECKING:
    from ..PlotlyGoBuilder import PlotlyGoBuilder


def build_html(builder: "PlotlyGoBuilder") -> None:
    fig_left = build_fig_left(builder)
    fig_right, _ = build_fig_right(builder)

    html_left = fig_left.to_html(full_html=False, include_plotlyjs="cdn")
    html_right = fig_right.to_html(full_html=False, include_plotlyjs=False)

    tracker_js = build_tracker_js()

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
