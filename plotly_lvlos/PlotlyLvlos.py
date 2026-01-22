import duckdb
from plotly_lvlos.core_data.load_raw_tables import load_core_raw_tables
from plotly_lvlos.core_data.validate_entity_first_column import (
    validate_entity_first_column,
)
from plotly_lvlos.core_data.validate_overlap_columns import (
    validate_overlap_columns
)
from plotly_lvlos.core_data.build_matches_table import (
    build_matches_table,
)


class PlotlyLvlos:
    def __init__(self, config_dict: dict) -> None:
        self.config_dict = config_dict

        self.con = duckdb.connect()

        self.data_x_table_label = "data_x"
        self.data_y_table_label = "data_y"

        self.core_table: duckdb.DuckDBPyRelation | None = None
        self.metrics_table: duckdb.DuckDBPyRelation | None = None
        self.matches_table: duckdb.DuckDBPyRelation | None = None

        self.frames = None

        self.html_path: str | None = None

    def build_core_data_table(self):
        """
        At this point, data files exist.
        Checks:
        - entity_column is the first column name
        - overlap :
            the next column are numerical
            overlap_start and overlap_end exist in both data_x and data_y files
            interval between them is dense in both data files

        Fuzz matching
        """

        data_x_table, data_y_table = load_core_raw_tables(
            con=self.con,
            config=self.config_dict,
            data_x_table_label=self.data_x_table_label,
            data_y_table_label=self.data_y_table_label,
        )

        validate_entity_first_column(
            con=self.con,
            data_x_table_label=self.data_x_table_label,
            data_y_table_label=self.data_y_table_label,
            entity_column=self.config_dict["data"]["entity_column"],
        )

        validate_overlap_columns(
            data_x_table=data_x_table,
            data_y_table=data_y_table,
            overlap_start=self.config_dict["data"]["overlap_start"],
            overlap_end=self.config_dict["data"]["overlap_end"],
        )

        self.matches_table = build_matches_table(
            con=self.con,
            data_x_table_label=self.data_x_table_label,
            data_y_table_label=self.data_y_table_label,
            matches_table_path="matches.csv",
            entity_column=self.config_dict["data"]["entity_column"]
        )

        # self.core_table = build_core_table()  # uses matches_table

        

    # def optionnal_data_enrichment(self):
    # def build_analytical_table(self):
    # def build_plotly_frames(self):
    # def build_html(self):
