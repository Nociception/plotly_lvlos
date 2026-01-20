from plotly_lvlos.errors.errors_build_core_data import EntityColumnError


def validate_entity_first_column(
    data_x_table=None,
    data_y_table=None,
    entity_column="",
) -> None:
    """
    Validates that the entity_column is the first column in both data_x_table and data_y_table.
    """

    if data_x_table is None or data_y_table is None or entity_column == "":
        raise ValueError("Data tables or entity_column must not be None/empty.")

    x_columns = data_x_table.columns
    y_columns = data_y_table.columns

    if x_columns[0] != entity_column:
        raise EntityColumnError(
            f"Entity column '{entity_column}' is not the first column in data_x_table. Found '{x_columns[0]}' instead."
        )

    if y_columns[0] != entity_column:
        raise EntityColumnError(
            f"Entity column '{entity_column}' is not the first column in data_y_table. Found '{y_columns[0]}' instead."
        )

    # print(f"Entity column '{entity_column}' is correctly positioned as the first column in both tables.")