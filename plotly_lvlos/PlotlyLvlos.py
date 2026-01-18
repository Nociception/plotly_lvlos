import duckdb
from plotly_lvlos.core_data.load_raw_tables import load_raw_tables


class PlotlyLvlos:
    def __init__(self, config_dict: dict) -> None:
        self.config_dict = config_dict

        self.con = duckdb.connect()
        self.con.close()

        self.core_table_name: str | None = None
        self.metrics_table_name: str | None = None

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

        data_x_table, data_y_table = load_raw_tables(
            con=self.con,
            config=self.config_dict,
        )

        # validate_entity_and_numeric_columns(
        #     con=self.con,
        #     data_x_table=data_x_table,
        #     data_y_table=data_y_table,
        #     entity_column=self.config_dict["entity_column"],
        # )

        # validate_overlap_and_density(
        #     con=self.con,
        #     data_x_table=data_x_table,
        #     data_y_table=data_y_table,
        #     overlap_start=self.config_dict["overlap_start"],
        #     overlap_end=self.config_dict["overlap_end"],
        # )

        # matched_x_table, matched_y_table = resolve_entity_matching(
        #     con=self.con,
        #     data_x_table=data_x_table,
        #     data_y_table=data_y_table,
        #     entity_column=self.config_dict["entity_column"],
        #     fuzzy=self.config_dict.get("fuzzy_matching", False),
        # )

        # core_table_name = build_core_table(
        #     con=self.con,
        #     data_x_table=matched_x_table,
        #     data_y_table=matched_y_table,
        #     config=self.config_dict,
        # )

        # self.core_table_name = core_table_name

    # def optionnal_data_enrichment(self):
    # def build_analytical_table(self):
    # def build_plotly_frames(self):
    # def build_html(self):
