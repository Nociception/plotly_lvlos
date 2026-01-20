from duckdb import DuckDBPyRelation


def validate_overlap_columns(
    data_x_table: DuckDBPyRelation | None = None,
    data_y_table: DuckDBPyRelation | None = None,
    overlap_start: int | str | None = None,
    overlap_end: int | str | None = None,
) -> None:
    """
    Validates that overlap_start and overlap_end are column names
    and that all integer column names between them are present.
    """

    if (
        data_x_table is None
        or data_y_table is None
        or overlap_start is None
        or overlap_end is None
    ):
        raise ValueError("Missing required arguments for overlap validation.")

    x_columns = data_x_table.columns
    y_columns = data_y_table.columns

    overlap_start = str(overlap_start)
    overlap_end = str(overlap_end)

    for table_name, columns in {
        "data_x_table": x_columns,
        "data_y_table": y_columns,
    }.items():
        if overlap_start not in columns:
            raise ValueError(
                f"Overlap start '{overlap_start}' not found in {table_name}."
            )

        if overlap_end not in columns:
            raise ValueError(
                f"Overlap end '{overlap_end}' not found in {table_name}."
            )

        start_index = columns.index(overlap_start)
        end_index = columns.index(overlap_end)

        if start_index > end_index:
            raise ValueError(
                f"In {table_name}, overlap_start occurs after overlap_end."
            )

        overlap_columns = columns[start_index : end_index + 1]

        try:
            overlap_values = [int(col) for col in overlap_columns]
        except ValueError as exc:
            raise ValueError(
                f"Non-integer column name found in overlap range of {table_name}."
            ) from exc

        expected_values = list(
            range(overlap_values[0], overlap_values[-1] + 1)
        )

        if overlap_values != expected_values:
            raise ValueError(
                f"Overlap columns in {table_name} are not continuous. "
                f"Expected {expected_values}, found {overlap_values}."
            )
