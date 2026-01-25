import duckdb
from pathlib import Path

from plotly_lvlos.core_data.matches_table_decorator import (
    matches_table_decorator
)
from plotly_lvlos.core_data.DataInfo import DataInfo
from plotly_lvlos.errors.errors_build_core_data import (
    FileReadFailure,
    EntityColumnFailure,
    EntityUniquenessFailure,
)
from plotly_lvlos.core_data.csv_profiles import CSV_PROFILES


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
        config_data: dict = self.config_dict["data"]
        self.entity_column_label: str = config_data["entity_column"]

        self.tables = [
            DataInfo(
                label="data_x",
                file=Path(config_data["x_file"]),
                mandatory=True,
                file_profile=config_data["x_file_profile"]
            ),
            DataInfo(
                label="data_y",
                file=Path(config_data["y_file"]),
                mandatory=True,
                file_profile=config_data["y_file_profile"]
            ),
            DataInfo(
                label="extra_data_point",
                file=Path(config_data["extra_data_point_file"]),
                mandatory=False,
                file_profile=config_data["extra_data_point_file_profile"]
            ),
            DataInfo(
                label="extra_data_x",
                file=Path(config_data["extra_data_x_file"]),
                mandatory=False,
                file_profile=config_data["extra_data_x_file_profile"]
            ),
        ]


    def build(self) -> tuple[
        duckdb.DuckDBPyRelation,
        duckdb.DuckDBPyRelation,
    ]:
        self.load_core_raw_tables()
        self.validate_entity_first_column_label()
        self.validate_first_column_entities()

        print(self.con.execute("SHOW TABLES").fetchall())
        df = self.con.execute(
            "SELECT * FROM extra_data_x LIMIT 1000"
        ).df()

        df.to_html("table.html", index=False)



    @matches_table_decorator
    def load_core_raw_tables(
        self,
        table: DataInfo
    ) -> None:
        profile_kwargs = CSV_PROFILES[table.file_profile]
        try:
            self.con.register(
                table.label,
                self.con.read_csv(
                    str(table.file),
                    header=True,
                    delimiter=",",
                    quotechar='"',
                    **profile_kwargs,
                ),
            )
        except (
            duckdb.IOException,
            duckdb.ParserException,
            duckdb.ConversionException,
            duckdb.InvalidInputException,
            duckdb.InternalException,
        ) as e:
            raise FileReadFailure(table, e)
    

    @matches_table_decorator
    def validate_entity_first_column_label(
        self,
        table: DataInfo,
    ) -> None:

        first_col = self.con.execute(
            f"""
            SELECT
                name
            FROM
                pragma_table_info('{table.label}')
            ORDER BY
                cid
            LIMIT
                1
            """
        ).fetchone()[0]
        if first_col != self.entity_column_label:
            raise EntityColumnFailure(
                f"In table '{table.label}', the first column must be "
                f"`{self.entity_column_label}`, "
                f"found `{first_col}` instead."
            )


    @matches_table_decorator
    def validate_first_column_entities(
        self,
        table: DataInfo,
    ) -> None:

        total_rows, distinct_entities = self.con.execute(
        f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT {self.entity_column_label}) AS distinct_entities
        FROM
            {table.label}
        """
        ).fetchone()

        if total_rows != distinct_entities:
            raise EntityUniquenessFailure(
                f"In {table.label}, entity column "
                f"`{self.entity_column_label}` contains duplicated values "
                f"({total_rows - distinct_entities} duplicate rows detected)."
            )



        # validate_overlap_columns(
        #     data_x_table=data_x_table,
        #     data_y_table=data_y_table,
        #     overlap_start=self.config_dict["data"]["overlap_start"],
        #     overlap_end=self.config_dict["data"]["overlap_end"],
        # )

        # self.matches_table = build_matches_table(
        # )

        # self.core_table = build_core_table()  # uses matches_table


