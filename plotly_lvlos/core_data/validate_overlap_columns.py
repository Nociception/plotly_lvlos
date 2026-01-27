from plotly_lvlos.core_data.DataInfo import DataInfo
from plotly_lvlos.errors.errors_build_core_data import (
    OverlapColumnsFailure,
)


def _overlap_columns_present_in_table(
    table: DataInfo | None = None,
    columns: list = [],
    overlap_start: str = "",
    overlap_end: str = "",
) -> None:

    if (
        table is None
        or len(columns) == 0
        or len(overlap_start) == 0
        or len(overlap_start) == 0
    ):
        raise OverlapColumnsFailure(
            "Argument in helper function is missing!"
        )

    if overlap_start not in columns:
        raise OverlapColumnsFailure(
            f"Overlap start '{overlap_start}' not found in table '{table.label}'."
        )
    if overlap_end not in columns:
        raise OverlapColumnsFailure(
            f"Overlap end '{overlap_end}' not found in table '{table.label}'."
        )


def _overlap_columns_indices_order(
    table_label: str = "",
    columns: list = [],
    start_index: int = -1,
    end_index: int = -1,
) -> None:

    if (
        len(table_label) == 0
        or len(columns) == 0
        or start_index == 0
        or end_index == 0
    ):
        raise OverlapColumnsFailure(
            "Argument in helper function is missing or non-existent!"
        )

    if start_index > end_index:
        raise OverlapColumnsFailure(
            f"In table '{table_label}', overlap_start occurs after overlap_end."
        )


def _overlap_columns_contiguous_int(
    table_label: str = "",
    columns: list = [],
    start_index: int = -1,
    end_index: int = -1,
) -> None:
    
    overlap_columns = columns[start_index : end_index + 1]
    try:
        overlap_values = [int(col) for col in overlap_columns]
    except ValueError as exc:
        raise OverlapColumnsFailure(
            f"Non-integer column name found in overlap range of table '{table_label}'. "
            f"Columns: {overlap_columns}"
        ) from exc

    expected_values = list(
        range(overlap_values[0], overlap_values[-1] + 1)
    )

    if overlap_values != expected_values:
        raise OverlapColumnsFailure(
            f"Overlap columns in table '{table_label}' are not contiguous. "
            f"Expected {expected_values}, found {overlap_values}."
        )
