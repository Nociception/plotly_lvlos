from duckdb import DuckDBPyConnection, DuckDBPyRelation


def load_raw_tables(
    con: DuckDBPyConnection = None,
    config: dict = None
) -> tuple[DuckDBPyRelation, DuckDBPyRelation]:
    return (
        con.read_csv(
            config["data"]["x_file"],
            header=True,
        ),
        con.read_csv(
            config["data"]["y_file"],
            header=True,
        ),
    )
