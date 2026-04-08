from __future__ import annotations
from typing import TYPE_CHECKING
from .fig_left import build_fig_left
from .fig_right import build_fig_right
from .tracker_js import build_tracker_js
from .fig_right import COLOR_LIN

if TYPE_CHECKING:
    from ..PlotlyGoBuilder import PlotlyGoBuilder


def build_html(builder: "PlotlyGoBuilder") -> None:
    fig_left = build_fig_left(builder)
    fig_right, _ = build_fig_right(builder)

    html_left = fig_left.to_html(full_html=False, include_plotlyjs="cdn")
    html_right = fig_right.to_html(full_html=False, include_plotlyjs=False)

    tracker_js = build_tracker_js()

    labels = builder.labels

    title_left = f"{labels['data_x']} vs {labels['data_y']}"
    title_right = "Statistical indicators"

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
                flex-direction: column;
            }}
            .titles {{
                display: flex;
                height: 32px;
                background: #111;
                flex-shrink: 0;
            }}
            .title-left {{
                flex: 3;
                display: flex;
                align-items: center;
                justify-content: center;
                color: {COLOR_LIN};
                font-family: sans-serif;
                font-size: 13px;
                letter-spacing: 0.05em;
            }}
            .title-right {{
                flex: 1;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #aaaaaa;
                font-family: sans-serif;
                font-size: 13px;
                letter-spacing: 0.05em;
            }}
            .figures {{
                display: flex;
                flex: 1;
                min-height: 0;
            }}
            .fig-left {{
                flex: 3;
                min-width: 0;
                height: 100%;
            }}
            .fig-right {{
                flex: 1;
                min-width: 0;
                height: 100%;
            }}
            .fig-left > div, .fig-right > div {{
                width: 100% !important;
                height: 100% !important;
            }}
        </style>
    </head>
    <body>
        <div class="titles">
            <div class="title-left">{title_left}</div>
            <div class="title-right">{title_right}</div>
        </div>
        <div class="figures">
            <div class="fig-left">{html_left}</div>
            <div class="fig-right">{html_right}</div>
        </div>
        {tracker_js}
    </body>
</html>"""

    with open("index.html", "w") as f:
        f.write(html)
