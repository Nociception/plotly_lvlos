import duckdb
import os.path

import polars as pl

from plotly_lvlos.core_data.all_tables_decorator import (
    all_tables_decorator
)
from plotly_lvlos.core_data.extract_parse_transform_load import (
    _extract_as_all_varchar,
    _validate_entity_first_column_label,
    _validate_first_column_entities_uniqueness,
    _convert_according_to_suffixes,
)
from plotly_lvlos.core_data.DataFileInfo import (
    DataFileInfo,
    create_DataFileInfo_objects,
)
from plotly_lvlos.core_data.overlap_columns import (
    _validate_overlap_columns,
    _fill_overlap_columns_DataFileInfo_field,
    _fill_overlap_columns_sql_DataFileInfo_field,
)
from plotly_lvlos.core_data.build_matches_table import (
    _create_empty_matches_table,
    _insert_data_x_entities,
    _get_entities_from_table,
    _export_matches_excel,
    _load_matches_file,
)
from plotly_lvlos.core_data.core_data_table_builder import (
    _build_core_data_table,
)
from plotly_lvlos.errors.errors_build_core_data import (
    FileReadFailure,
    EntityColumnFailure,
    EntityUniquenessFailure,
)


class CoreDataBuilder:
    def __init__(
        self,
        con : duckdb.DuckDBPyConnection | None,
        config_dict: dict | None,
        core_data_table_label: str = "",
    ):
        if con is None:
            raise ValueError("con (connection) is missing !")
        if config_dict is None:
            raise ValueError("config_dict is missing !")

        self.con: duckdb.DuckDBPyConnection = con
        self.config_dict: dict = config_dict
        self.config_data: dict = self.config_dict["data"]
        self.entity_column_label: str = self.config_data["entity_column"]
        self.matches_table_path = "config/matches.xlsx"
        self.matches_table_label = "matches"
        self.core_data_table_label = core_data_table_label
        self.overlap_column_label = self.config_data["overlap_column"]
        self.x_entities: list[str] | None = None
        self.tables: dict[str, DataFileInfo] | None = None

    def build(self) -> tuple[
        duckdb.DuckDBPyRelation,
        duckdb.DuckDBPyRelation,
    ]:
        self.tables = create_DataFileInfo_objects(self.config_dict)
        
        
        self.extract_parse_transform_load()


        
        # self.build_matches_table()
        # _load_matches_file(
        #     con=self.con,
        #     matches_file_path=self.matches_table_path,
        #     matches_table_label=self.matches_table_label,
        # )
        # _build_core_data_table(
        #     con=self.con,
        #     entity_column_label=self.entity_column_label,
        #     overlap_column_label=self.overlap_column_label,
        #     tables=self.tables,
        # )



        # print(self.con.execute("SHOW TABLES").fetchall())
        # print("######")
        # df = self.con.execute(
        #     "SELECT * FROM core_data"
        # ).df()
        # print(df.head())
        # df.to_html("table.html", index=False)
        # # print(self.con.execute("DESCRIBE data_x").fetchall())
        # print("######")
        # self.print_tables_info()
        # print(self.config_dict)

    @all_tables_decorator
    def extract_parse_transform_load(self, table: DataFileInfo):
        _extract_as_all_varchar(table=table)
        _validate_entity_first_column_label(
            table=table,
            entity_column_label=self.entity_column_label,
        )
        _validate_first_column_entities_uniqueness(
            table=table,
            entity_column_label=self.entity_column_label,
        )
        _validate_overlap_columns(
            table=table,
            overlap_start=str(self.config_data["overlap_start"]),
            overlap_end=str(self.config_data["overlap_end"]),
        )
        _fill_overlap_columns_DataFileInfo_field(
            table=table,
            overlap_start=self.config_data["overlap_start"],
            overlap_end=self.config_data["overlap_end"],
        )
        _fill_overlap_columns_sql_DataFileInfo_field(table=table)
        _convert_according_to_suffixes(
            table=table,
            default_suffixes=self.config_dict["suffixes"]["default"],
        )



        # print("################")
        # table.df.write_csv(f"{table.label}_debug.csv")
        # print(table.df.describe())
        # print("################")

        # load into duckdb



    
    # def fill_overlap_columns_sql_DataFileInfo_field(
    #     self,
    #     table: DataFileInfo,
    # ) -> None:
    #     overlap_columns = _get_overlap_columns(
    #         con=self.con,
    #         table_name=table.label,
    #         overlap_start=self.config_data["overlap_start"],
    #         overlap_end=self.config_data["overlap_end"],
    #     )

    #     table.overlap_columns_sql = ", ".join(
    #         f'"{col}"' for col in overlap_columns
    #     )

    # @all_tables_decorator
    # def merge_entities_into_matches_table(
    #     self,
    #     table: DataFileInfo,
    # ) -> None:
    #     if table.label == "data_x":
    #         return
     
    #     from rapidfuzz import fuzz, process

    #     match_threshold: int = 90
    #     table_entities = _get_entities_from_table(
    #         con=self.con,
    #         table_label=table.label,
    #         entity_column_label=self.entity_column_label
    #     )
    #     matches = []
    #     for table_entity in table_entities:
    #         best_match_in_x, score, _ = process.extractOne(
    #             table_entity,
    #             self.x_entities,
    #             scorer=fuzz.WRatio
    #         )
    #         if score >= 100:
    #             matches.append((table_entity, best_match_in_x, "exact", 1.0))
    #         elif score >= match_threshold:
    #             matches.append((table_entity, best_match_in_x, "fuzzy", score / 100.0))
    #         else:
    #             matches.append((table_entity, None, "unmatched", 0.0))
        
    #     for table_entity, x_match, match_type, confidence in matches:
    #         if x_match is not None:
    #             self.con.execute(f"""
    #                 UPDATE
    #                     {self.matches_table_label}
    #                 SET
    #                     {table.label} = ?, {table.label}_match_type = ?, {table.label}_confidence = ?
    #                 WHERE
    #                     data_x = ?
    #                 """,
    #                 (table_entity, match_type, confidence, x_match)
    #             )

    #         else:
    #             self.con.execute(f"""
    #                 INSERT INTO {self.matches_table_label} (
    #                     data_x,
    #                     {table.label},
    #                     {table.label}_match_type,
    #                     {table.label}_confidence
    #                 )
    #                 VALUES (?, ?, ?, ?)
    #                 """,
    #                 (
    #                     None,
    #                     table_entity,
    #                     "unmatched",
    #                     0.0,
    #                 ),
    #             )
            
    # def build_matches_table(self) -> None:
    #     """TODO: log these prints"""
    #     if os.path.exists(self.matches_table_path):
    #         print("Matches file provided; using it as is.")
    #         return
    #     print("No matches file provided.")
    #     print("Automatic matches table generation in progress...")
        
    #     self.fill_overlap_columns_sql_DataFileInfo_field()

    #     _create_empty_matches_table(
    #         con=self.con,
    #         matches_table_label=self.matches_table_label,
    #     )
    #     _insert_data_x_entities(
    #         con=self.con,
    #         data_x_table_label=self.tables["data_x"].label,
    #         matches_table_label=self.matches_table_label,
    #         entity_column_label=self.entity_column_label,
    #     )
    #     self.x_entities = _get_entities_from_table(
    #         con=self.con,
    #         table_label=self.tables["data_x"].label,
    #         entity_column_label=self.entity_column_label,
    #     )
    #     self.merge_entities_into_matches_table()
    #     _export_matches_excel(
    #         con=self.con,
    #         matches_table_label=self.matches_table_label,
    #         output_path=self.matches_table_path,
    #     )

    def print_tables_info(self) -> None:
        for table in self.tables:
            print(table, self.tables[table], self.tables[table].suffixes)
