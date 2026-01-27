import duckdb

from plotly_lvlos.core_data.CoreDataBuilder import CoreDataBuilder


class PlotlyLvlos:

    def __init__(self, config_dict: dict) -> None:

        self.config_dict = config_dict

        self.con = duckdb.connect()

        self.frames = None

        self.html_path: str | None = None

    def build_core_data_table(self):

        core_data_builder = CoreDataBuilder(
            con=self.con,
            config_dict=self.config_dict,
        )
        core_data_builder.build()
        

    # def build_analytical_table(self):
    # def build_plotly_frames(self):
    # def build_html(self):

    def close_connection(self) -> None:
        self.con.close()