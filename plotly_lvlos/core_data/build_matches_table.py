import os.path

from duckdb import DuckDBPyRelation, DuckDBPyConnection
from rapidfuzz import fuzz, process


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


def get_x_entities_from_matches(con: DuckDBPyConnection | None = None) -> list:
    return [
        entity[0] for entity in con.execute("""
            SELECT
                data_x
            FROM
                matches_table
        """).fetchall()
    ]


def _merge_data_y_entities(
    con: DuckDBPyConnection,
    data_y_table_label: str,
    entity_column: str,
    threshold: float = 90.0,
) -> None:
    """
    Merge data_y entities into matches_table using fuzzy matching.

    Rules:
    - Each data_y entity is matched to the best data_x entity.
    - If multiple candidates, take the one with the highest score.
    - If score < threshold, consider as unmatched (orphan).

    Updates matches_table columns:
    - data_y
    - data_y_match_type: 'exact', 'fuzzy', or 'unmatched'
    - data_y_confidence: 1.0 for exact, normalized score for fuzzy, 0.0 for unmatched
    """

    data_x_entities = get_x_entities_from_matches(con=con)

    data_y_entities = [
        entity[0] for entity in con.execute(f"""
            SELECT
                {entity_column}
            FROM
                {data_y_table_label}
        """).fetchall()
    ]

    matches = []
    for y_entity in data_y_entities:
        best_match_in_x, score, _ = process.extractOne(
            y_entity,
            data_x_entities,
            scorer=fuzz.WRatio
        )
        if score >= 100:
            matches.append((y_entity, best_match_in_x, "exact", 1.0))
        elif score >= threshold:
            matches.append((y_entity, best_match_in_x, "fuzzy", score / 100.0))
        else:
            matches.append((y_entity, None, "unmatched", 0.0))
    

    for y_entity, x_match, match_type, confidence in matches:
        if x_match is not None:
            con.execute(
                """
                UPDATE
                    matches_table
                SET
                    data_y = ?, data_y_match_type = ?, data_y_confidence = ?
                WHERE
                    data_x = ?
                """,
                (y_entity, match_type, confidence, x_match)
            )

        else:
            con.execute(
                """
                INSERT INTO
                    matches_table (data_x, data_y, data_y_match_type, data_y_confidence)
                VALUES
                    (?, ?, ?, ?)
                """,
                (None, y_entity, match_type, confidence)
            )


def build_matches_table(
    con: DuckDBPyConnection | None = None,
    data_x_table_label: str | None = None,
    data_y_table_label: str | None = None,
    entity_column: str | None = "",
    matches_table_path: str | None = "",
) -> DuckDBPyRelation:

    # if matches_table_path and os.path.exists(matches_table_path):
    #     print("Matches table provided; using it as-is.")
    #     return con.read_csv(matches_table_path)

    # print("No matches table provided.")
    # print("Automatic matches table generation in progress...")

    # _create_empty_matches_table(con)

    # _insert_data_x_entities(
    #     con=con,
    #     data_x_table_label=data_x_table_label,
    #     entity_column=entity_column,
    # )

    _merge_data_y_entities(
        con=con,
        data_y_table_label=data_y_table_label,
        entity_column=entity_column
    )
    con.execute("""
        SELECT
            *
        FROM
            matches_table
    """).fetchdf().to_csv("matches.csv", index=False)

    return con.table("matches_table")
