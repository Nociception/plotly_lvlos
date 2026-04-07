from pathlib import Path

import duckdb
import plotly.graph_objects as go

from plotly_lvlos.core_data.CoreDataBuilder import CoreDataBuilder
from plotly_lvlos.plotly_go.PlotlyGoBuilder import PlotlyGoBuilder


class PlotlyLvlos:
    def __init__(self, config_dict: dict) -> None:
        self.config_dict = config_dict
        self.con = duckdb.connect("core_data.duckdb")
        self.frames: list[go.Frame]
        self.html_path: str | None = None
        self.core_data_table_label = "core_data"

    def build_core_data_table(self) -> None:
        if not Path("core_data.csv").resolve().exists():
            core_data_builder = CoreDataBuilder(
                con=self.con,
                config_dict=self.config_dict,
                core_data_table_label=self.core_data_table_label,
            )
            core_data_builder.build()

    def build_plotly_graphic_object(self) -> None:
        plotly_go_builder = PlotlyGoBuilder(
            con=self.con,
            config_dict=self.config_dict,
        )
        plotly_go_builder.build()

    def close_connection(self) -> None:
        self.con.close()
