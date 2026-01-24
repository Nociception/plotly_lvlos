import duckdb
import warnings

from plotly_lvlos.errors.errors_build_core_data import (
    ExtraDataFileReadError,
    ExtraDataFileReadWarning,
)


class CoreDataBuilder:

    def __init__(
        self,
        con : duckdb.DuckDBPyConnection | None,
        config_dict: dict | None,
    ):
        if con is None:
            raise ValueError("con (connection) is missing !")
        if config_dict is None:
            raise ValueError("config_dict is missing !")

        self.con: duckdb.DuckDBPyConnection = con
        self.config_dict: dict = config_dict

        self.data_x_table_label = "data_x"
        self.data_y_table_label = "data_y"
        self.extra_data_point_table_label = "extra_data_point"
        self.extra_data_x_table_label = "extra_data_x"

    def build(self):
        self.load_core_raw_tables()
        print(self.con.execute("SHOW TABLES").fetchall())
    
    def load_core_raw_tables(self):
        config_data = self.config_dict["data"]
        for label, file in (
            (self.data_x_table_label, config_data["x_file"]),
            (self.data_y_table_label, config_data["y_file"]),
            (self.extra_data_point_table_label, config_data["extra_data_point_file"]),
            (self.extra_data_x_table_label, config_data["extra_data_x_file"]),
        ):
                try:
                    self.con.register(label, self.con.read_csv(file, header=True))
                except (
                    duckdb.IOException,
                    duckdb.ParserException,
                    duckdb.ConversionException,
                    duckdb.InvalidInputException,
                    duckdb.InternalException,
                ) as e:
                    if "extra" in label:
                        warnings.warn(ExtraDataFileReadWarning(
                            label=label,
                            file=file,
                            original_exception=e,
                        ))
                    else:
                        raise ExtraDataFileReadError(
                            label=label,
                            file=file,
                            original_exception=e,
                        ) from e
        
        # validate_entity_first_column(
        #     con=self.con,
        #     data_x_table_label=self.data_x_table_label,
        #     data_y_table_label=self.data_y_table_label,
        #     entity_column=self.config_dict["data"]["entity_column"],
        # )

        # validate_overlap_columns(
        #     data_x_table=data_x_table,
        #     data_y_table=data_y_table,
        #     overlap_start=self.config_dict["data"]["overlap_start"],
        #     overlap_end=self.config_dict["data"]["overlap_end"],
        # )

        # self.matches_table = build_matches_table(
        #     con=self.con,
        #     data_x_table_label=self.data_x_table_label,
        #     data_y_table_label=self.data_y_table_label,
        #     matches_table_path="matches.csv",
        #     entity_column=self.config_dict["data"]["entity_column"]
        # )

        # self.core_table = build_core_table()  # uses matches_table


