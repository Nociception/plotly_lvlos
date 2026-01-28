import duckdb
from pathlib import Path
import os.path

from plotly_lvlos.core_data.matches_table_decorator import (
    matches_table_decorator
)
from plotly_lvlos.core_data.DataInfo import DataInfo
from plotly_lvlos.core_data.csv_profiles import CSV_PROFILES
from plotly_lvlos.core_data.validate_overlap_columns import (
    _overlap_columns_present_in_table,
    _overlap_columns_indices_order,
    _overlap_columns_contiguous_int,
)
from plotly_lvlos.core_data.build_matches_table import (
    _create_empty_matches_table,
    _insert_data_x_entities,
    _get_entities_from_table,
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
    ):
        if con is None:
            raise ValueError("con (connection) is missing !")
        if config_dict is None:
            raise ValueError("config_dict is missing !")

        self.con: duckdb.DuckDBPyConnection = con
        self.config_dict: dict = config_dict
        self.config_data: dict = self.config_dict["data"]
        self.entity_column_label: str = self.config_data["entity_column"]

        self.matches_table_path = "config/matches.csv"
        self.matches_table_label = "matches"
        self.x_entities: list[str] | None = None

        self.tables = [
            DataInfo(
                label="data_x",
                file=Path(self.config_data["x_file"]),
                mandatory=True,
                file_profile=self.config_data["x_file_profile"]
            ),
            DataInfo(
                label="data_y",
                file=Path(self.config_data["y_file"]),
                mandatory=True,
                file_profile=self.config_data["y_file_profile"]
            ),
            DataInfo(
                label="extra_data_point",
                file=Path(self.config_data["extra_data_point_file"]),
                mandatory=False,
                file_profile=self.config_data["extra_data_point_file_profile"]
            ),
            DataInfo(
                label="extra_data_x",
                file=Path(self.config_data["extra_data_x_file"]),
                mandatory=False,
                file_profile=self.config_data["extra_data_x_file_profile"]
            ),
        ]


    def build(self) -> tuple[
        duckdb.DuckDBPyRelation,
        duckdb.DuckDBPyRelation,
    ]:
        self.load_core_raw_tables()
        self.validate_entity_first_column_label()
        self.validate_first_column_entities_uniqueness()
        self.validate_overlap_columns()

        self.build_matches_table()

        # self.build_core_table()

        print(self.con.execute("SHOW TABLES").fetchall())

        print("#####")
        df = self.con.execute(
            f"SELECT * FROM {self.matches_table_label} LIMIT 1000"
        ).df()

        df.to_html("table.html", index=False)
        print("#####")

        self.print_tables_info()



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
    def validate_first_column_entities_uniqueness(
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

    @matches_table_decorator
    def validate_overlap_columns(
        self,
        table: DataInfo
    ) -> None:
        """
        Validate overlap columns for a single table.

        Ensures that overlap_start and overlap_end columns exist,
        are ordered correctly, and define a continuous integer range.
        """

        columns = self.con.table(table.label).columns

        overlap_start = str(self.config_data["overlap_start"])
        overlap_end = str(self.config_data["overlap_end"])
        _overlap_columns_present_in_table(
            table=table,
            columns=columns,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
        )

        if table.mandatory:
            start_index=columns.index(overlap_start)
            end_index=columns.index(overlap_end)

            _overlap_columns_indices_order(
                table_label=table.label,
                start_index=start_index,
                end_index=end_index,
            )

            _overlap_columns_contiguous_int(
                table_label=table.label,
                columns=columns,
                start_index=start_index,
                end_index=end_index,
            )

    @matches_table_decorator
    def merge_entities_into_matches_table(
        self,
        table: DataInfo
    ) -> None:
        if table.label == "data_x":
            return
     
        from rapidfuzz import fuzz, process

        match_threshold: int = 90
        table_entities = _get_entities_from_table(
            con=self.con,
            table_label=table.label,
            entity_column_label=self.entity_column_label
        )
        matches = []
        for table_entity in table_entities:
            best_match_in_x, score, _ = process.extractOne(
                table_entity,
                self.x_entities,
                scorer=fuzz.WRatio
            )
            if score >= 100:
                matches.append((table_entity, best_match_in_x, "exact", 1.0))
            elif score >= match_threshold:
                matches.append((table_entity, best_match_in_x, "fuzzy", score / 100.0))
            else:
                matches.append((table_entity, None, "unmatched", 0.0))
        
        for table_entity, x_match, match_type, confidence in matches:
            if x_match is not None:
                self.con.execute(f"""
                    UPDATE
                        {self.matches_table_label}
                    SET
                        {table.label} = ?, {table.label}_match_type = ?, {table.label}_confidence = ?
                    WHERE
                        data_x = ?
                    """,
                    (table_entity, match_type, confidence, x_match)
                )

            # else:
            #     con.execute(f"""
            #         INSERT INTO
            #             {matches_table_label} (data_x, data_y, data_y_match_type, data_y_confidence)
            #         VALUES
            #             (?, ?, ?, ?)
            #         """,
            #         (None, y_entity, match_type, confidence)
            #     )
            

    def build_matches_table(self) -> None:
        """TODO: log these prints"""
        if os.path.exists(self.matches_table_path):
            print("Matches table provided; using it as is.")
            return
        print("No matches table provided.")
        print("Automatic matches table generation in progress...")
            
        _create_empty_matches_table(
            con=self.con,
            matches_table_label=self.matches_table_label,
        )
        _insert_data_x_entities(
            con=self.con,
            data_x_table_label=self.tables[0].label,
            matches_table_label=self.matches_table_label,
            entity_column_label=self.entity_column_label,
        )
        self.x_entities = _get_entities_from_table(
            con=self.con,
            table_label=self.tables[0].label,
            entity_column_label=self.entity_column_label,
        )
        self.merge_entities_into_matches_table()

        # must generate the so called matches.csv into the config directory


    # def build_core_table(self) -> None:  # uses matches_table


    def print_tables_info(self) -> None:
        for table in self.tables:
            print(table)