import duckdb


def load_raw_tables(con: duckdb.DuckDBPyConnection = None, config: dict = None) -> tuple[duckdb.DuckDBPyRelation, duckdb.DuckDBPyRelation]:

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
