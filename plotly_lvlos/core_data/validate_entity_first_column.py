# from duckdb import (
#     DuckDBPyConnection,
# )

# from plotly_lvlos.errors.errors_build_core_data import (
#     EntityColumnError,
#     EntityUniquenessError,
# )


# def _validate_entity_column(
#     con: DuckDBPyConnection,
#     table_label: str,
#     entity_column: str,
# ) -> None:
#     """
#     Validates entity column position and uniqueness for a single table.
#     """

#     first_col = con.execute(
#         f"""
#         SELECT
#             name
#         FROM
#             pragma_table_info('{table_label}')
#         ORDER BY
#             cid
#         LIMIT
#             1
#         """
#     ).fetchone()[0]

#     if first_col != entity_column:
#         raise EntityColumnError(
#             f"In table '{table_label}', the first column must be '{entity_column}', "
#             f"found '{first_col}' instead."
#         )


#     total_rows, distinct_entities = con.execute(
#         f"""
#         SELECT
#             COUNT(*) AS total_rows,
#             COUNT(DISTINCT {entity_column}) AS distinct_entities
#         FROM
#             {table_label}
#         """
#     ).fetchone()

#     if total_rows != distinct_entities:
#         raise EntityUniquenessError(
#             f"In {table_label}, entity column '{entity_column}' contains duplicated values "
#             f"({total_rows - distinct_entities} duplicate rows detected)."
#         )


# def validate_entity_first_column(
#     con: DuckDBPyConnection | None = None,
#     data_x_table_label: str | None = None,
#     data_y_table_label: str | None = None,
#     entity_column: str = "",
# ) -> None:
#     """
#     Validates the entity column contract for data_x and data_y tables.

#     Checks:
#     - entity_column is the first column
#     - entity_column values are unique (no duplicated entities)

#     Raises:
#         EntityColumnError: if the entity column is not the first column
#         EntityUniquenessError: if duplicated entity values are found
#     """

#     if (con is None
#         or data_x_table_label is None
#         or data_y_table_label is None
#         or entity_column == ""
#     ):
#         raise ValueError("Data tables and entity_column must not be None or empty.")

#     _validate_entity_column(
#         con=con,
#         table_label=data_x_table_label,
#         entity_column=entity_column,
#     )

#     _validate_entity_column(
#         con=con,
#         table_label=data_y_table_label,
#         entity_column=entity_column,
#     )
