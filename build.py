from pathlib import Path
import webbrowser

import duckdb
from typeguard import typechecked

from plotly_lvlos.config.load_config import load_config
from plotly_lvlos.PlotlyLvlos import PlotlyLvlos


@typechecked
def build(config_path: str = "") -> None:
    config_dict = load_config(config_path=Path(config_path))
    plotly_lvlos = PlotlyLvlos(config_dict=config_dict)
    plotly_lvlos.build_core_data_table()

    # plotly_lvlos.build_analytical_table(self)

    plotly_lvlos.build_plotly_frames()
    plotly_lvlos.build_html()

    plotly_lvlos.close_connection()


if __name__ == "__main__":
    build(config_path="config/config.toml")

    html_path = Path("plotly_lvlos.html").resolve()
    if html_path.exists():
        webbrowser.open(f"file://{html_path}")
    else:
        raise FileNotFoundError(html_path)