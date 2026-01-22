from duckdb import DuckDBPyConnection, DuckDBPyRelation


def load_core_raw_tables(
    con: DuckDBPyConnection,
    config: dict,
    data_x_table_label: str,
    data_y_table_label: str,
) -> tuple[DuckDBPyRelation, DuckDBPyRelation]:
    """
    Loads raw data_x and data_y files and registers them
    as DuckDB tables named 'data_x' and 'data_y'.

    Contract:
    - data_x and data_y are available for SQL queries
    - returned relations correspond exactly to the registered tables
    """

    data_x = con.read_csv(
        config["data"]["x_file"],
        header=True,
    )

    data_y = con.read_csv(
        config["data"]["y_file"],
        header=True,
    )

    con.register(data_x_table_label, data_x)
    con.register(data_y_table_label, data_y)

    return data_x, data_y
