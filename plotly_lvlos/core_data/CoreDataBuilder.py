import duckdb
from pathlib import Path

from plotly_lvlos.core_data.matches_table_decorator import (
    matches_table_decorator
)
from plotly_lvlos.core_data.DataInfo import DataInfo
from plotly_lvlos.errors.errors_build_core_data import (
    FileReadFailure
)
#     ErrorBuildCoreData,
#     ExtraDataFileReadError,
#     ExtraDataFileReadWarning,
#     EntityColumnError,
#     EntityColumnWarning,
#     EntityUniquenessError,
#     EntityUniquenessWarning,
# )


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
        self.entity_column_label: str = self.config_dict["data"]["entity_column"]

        self.tables = [
            DataInfo(
                label="data_x",
                file=Path(self.config_dict["data"]["x_file"]),
                mandatory=True,
            ),
            DataInfo(
                label="data_y",
                file=Path(self.config_dict["data"]["y_file"]),
                mandatory=True,
            ),
            DataInfo(
                label="extra_data_point",
                file=Path(self.config_dict["data"]["extra_data_point_file"]),
                mandatory=False,
            ),
            DataInfo(
                label="extra_data_x",
                file=Path(self.config_dict["data"]["extra_data_x_file"]),
                mandatory=False,
            ),
        ]


    def build(self) -> tuple[
        duckdb.DuckDBPyRelation,
        duckdb.DuckDBPyRelation,
    ]:
        self.load_core_raw_tables()
        print(self.con.execute("SHOW TABLES").fetchall())
        # self.validate_entity_first_column()


    @matches_table_decorator
    def load_core_raw_tables(
        self,
        table: DataInfo
    ) -> None:
        try:
            self.con.register(
                table.label,
                self.con.read_csv(str(table.file), header=True),
            )
        except (
            duckdb.IOException,
            duckdb.ParserException,
            duckdb.ConversionException,
            duckdb.InvalidInputException,
            duckdb.InternalException,
        ) as e:
            raise FileReadFailure(table, e)
    




    # def validate_entity_first_column(self) -> None:

    #     for table_label in (
    #         self.data_x_table_label,
    #         self.data_y_table_label,
    #         self.extra_data_point_table_label,
    #         self.extra_data_x_table_label,
    #     ):
    #         print("#######")
    #         print(table_label)
    #         print("#######")
    #         try:
    #             first_col = self.con.execute(
    #                 f"""
    #                 SELECT
    #                     name
    #                 FROM
    #                     pragma_table_info('{table_label}')
    #                 ORDER BY
    #                     cid
    #                 LIMIT
    #                     1
    #                 """
    #             ).fetchone()[0]
    #         except TypeError:
    #             continue
    #         if first_col != self.entity_column_label:
    #             fail_text: str =  (
    #                 f"In table '{table_label}', the first column must be "
    #                 f"`{self.entity_column_label}`, "
    #                 f"found `{first_col}` instead."
    #             )
    #             if "extra" in table_label:
    #                 warnings.warn(EntityColumnWarning(fail_text))
    #                 if "point" in table_label:
    #                     self.extra_data_point_table_status = False
    #                 else:
    #                     self.extra_data_x_table_status = False
    #             else:
    #                 raise EntityColumnError(fail_text)


    #         print("#######")
    #         print(table_label)
    #         print("#######")
    #         try:
    #             total_rows, distinct_entities = self.con.execute(
    #                 f"""
    #         SELECT
    #             COUNT(*) AS total_rows,
    #             COUNT(DISTINCT {self.entity_column_label}) AS distinct_entities
    #         FROM
    #             {table_label}
    #                 """
    #             ).fetchone()
    #         except duckdb.CatalogException:
    #             if "extra" in table_label:
    #                 continue

    #         if total_rows != distinct_entities:
    #             if "extra" in table_label:
    #                 warnings.warn(EntityUniquenessWarning)
    #                 if "point" in table_label:
    #                     self.extra_data_point_table_status = False
    #                 else:
    #                     self.extra_data_x_table_status = False
    #             else:
    #                 raise EntityUniquenessError(
    #                     f"In {table_label}, entity column '{self.entity_column_label}' contains duplicated values "
    #                     f"({total_rows - distinct_entities} duplicate rows detected)."
    #             )



        # validate_overlap_columns(
        #     data_x_table=data_x_table,
        #     data_y_table=data_y_table,
        #     overlap_start=self.config_dict["data"]["overlap_start"],
        #     overlap_end=self.config_dict["data"]["overlap_end"],
        # )

        # self.matches_table = build_matches_table(
        # )

        # self.core_table = build_core_table()  # uses matches_table


