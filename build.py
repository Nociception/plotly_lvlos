from pathlib import Path

from typeguard import typechecked

from plotly_lvlos.config.load_config import load_config
from plotly_lvlos.PlotlyLvlos import PlotlyLvlos


@typechecked
def build(config_path: str = "") -> None:
    config_dict = load_config(config_path=Path(config_path))
    plotly_lvlos = PlotlyLvlos(config_dict=config_dict)
    plotly_lvlos.build_core_data_table()

    # plotly_lvlos.build_analytical_table(self):
    # plotly_lvlos.build_plotly_frames(self):
    # plotly_lvlos.build_html()

    plotly_lvlos.close_connection()


if __name__ == "__main__":
    build(config_path="config/config.toml")
