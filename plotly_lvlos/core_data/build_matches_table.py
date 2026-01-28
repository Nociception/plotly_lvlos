import os.path

from duckdb import DuckDBPyRelation, DuckDBPyConnection
from rapidfuzz import fuzz, process

from plotly_lvlos.core_data.DataInfo import DataInfo
from plotly_lvlos.errors.errors_build_core_data import (
    MatchesTableBuildingFailure,
)

def _create_empty_matches_table(
    con: DuckDBPyConnection | None = None,
    matches_table_label: str = ""
) -> None:

    con.execute(
        f"""
        CREATE TABLE {matches_table_label} (
            data_x VARCHAR,
            data_y VARCHAR,
            data_y_match_type VARCHAR,
            data_y_confidence DOUBLE,
            extra_data_point VARCHAR,
            extra_data_point_match_type VARCHAR,
            extra_data_point_confidence DOUBLE,
            extra_data_x VARCHAR,
            extra_data_x_match_type VARCHAR,
            extra_data_x_confidence DOUBLE
        )
        """
    )


def _insert_data_x_entities(
    con: DuckDBPyConnection | None = None,
    data_x_table_label: str = "",
    matches_table_label: str = "",
    entity_column_label: str = "",
) -> None:
    
    con.execute(
        f"""
        INSERT INTO
            {matches_table_label} (data_x)
        SELECT
            {entity_column_label}
        FROM
            {data_x_table_label}
        """
    )


def _get_entities_from_table(
    con: DuckDBPyConnection | None = None,
    table_label: str = "",
    entity_column_label: str = "",
) -> list:
    return [
        entity[0] for entity in con.execute(f"""
            SELECT
                {entity_column_label}
            FROM
                {table_label}
        """).fetchall()
    ]


