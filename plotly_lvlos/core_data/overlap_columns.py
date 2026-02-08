from plotly_lvlos.core_data.DataFileInfo import DataFileInfo
from plotly_lvlos.errors.errors_build_core_data import (
    OverlapColumnsFailure,
)


def _overlap_columns_present_in_table(
    table: DataFileInfo | None = None,
    columns: list = [],
    overlap_start: str = "",
    overlap_end: str = "",
) -> None:

    if table.mandatory:
        if overlap_start not in columns:
            raise OverlapColumnsFailure(
                f"Overlap start '{overlap_start}' not found in table '{table.label}'."
            )
        if overlap_end not in columns:
            raise OverlapColumnsFailure(
                f"Overlap end '{overlap_end}' not found in table '{table.label}'."
            )
    else:
        for column in columns:
            try:
                int_column = int(column)
                if int_column in [
                    col for col in range(
                        int(overlap_start), int(overlap_end) + 1)]:
                    return
            except ValueError:
                continue
        raise OverlapColumnsFailure(
            f"No overlap column found in {table.label}."
            "At least one column must be in the range [overlap_start, overlap_end]."
        )


def _overlap_columns_indices_order(
    table_label: str = "",
    start_index: int = -1,
    end_index: int = -1,
) -> None:

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


def _validate_overlap_columns(
    table: DataFileInfo | None = None,
    overlap_start: str | None = "",
    overlap_end: str | None = "",
) -> None:
        columns = table.df.columns
        _overlap_columns_present_in_table(
            table=table,
            columns=columns,
            overlap_start=overlap_start,
            overlap_end=overlap_end,
        )
        if table.mandatory:
            start_index=columns.index(overlap_start)
            end_index=columns.index(overlap_end)
            _overlap_columns_indices_order(
                table_label=table.label,
                start_index=start_index,
                end_index=end_index,
            )
            _overlap_columns_contiguous_int(
                table_label=table.label,
                columns=columns,
                start_index=start_index,
                end_index=end_index,
            )


def _fill_overlap_columns_DataFileInfo_field(
    table: DataFileInfo | None = None,
    overlap_start: int = -1,
    overlap_end: int = -1,
) -> None:
    overlap_columns: list[str] = []

    for name in table.df.columns:
        try:
            value = int(name)
        except ValueError:
            continue

        if overlap_start <= value <= overlap_end:
            overlap_columns.append(name)

    if not overlap_columns:
        raise ValueError(
            f"No overlap columns found in table '{table.label}' "
            f"for interval [{overlap_start} ; {overlap_end}]"
        )

    table.overlap_columns = overlap_columns


def _fill_overlap_columns_sql_DataFileInfo_field(
    table: DataFileInfo,
) -> None:

    table.overlap_columns_sql = ", ".join(
        f'"{col}"' for col in table.overlap_columns
    )