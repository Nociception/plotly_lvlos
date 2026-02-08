import polars as pl

from plotly_lvlos.core_data.DataFileInfo import DataFileInfo
from plotly_lvlos.errors.errors_build_core_data import (
     EntityColumnFailure,
)


def _extract_as_all_varchar(table: DataFileInfo) -> pl.DataFrame:
    df = pl.read_csv(
        table.file,
        quote_char=None,
        try_parse_dates=False,
        infer_schema_length=0,
        truncate_ragged_lines=True,
    )
    table.df = df.with_columns(pl.all().cast(pl.Utf8))


def _validate_entity_first_column_label(
    table: DataFileInfo | None = None,
    entity_column_label: str = "",
) -> None:

    first_col = table.df.columns[0]
    if first_col != entity_column_label:
        raise EntityColumnFailure(
            f"In table '{table.label}', the first column must be "
            f"`{entity_column_label}`, found `{first_col}` instead."
        )