from duckdb import DuckDBPyConnection


def get_x_entities_from_matches(con: DuckDBPyConnection | None = None) -> list:
    return [
        entity[0] for entity in con.execute("""
            SELECT
                data_x
            FROM
                matches_table
        """).fetchall()
    ]
