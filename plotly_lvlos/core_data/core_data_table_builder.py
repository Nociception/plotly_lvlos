import polars as pl
import pyarrow as pa
import duckdb
from pathlib import Path
from plotly_lvlos.core_data.DataFileInfo import DataFileInfo
from plotly_lvlos.errors.errors_build_core_data import FileReadFailure


EXPECTED_COLUMNS = [
    "data_x",
    "data_y",
    "data_y_match_type",
    "data_y_confidence",
    "extra_data_point",
    "extra_data_point_match_type",
    "extra_data_point_confidence",
    "extra_data_x",
    "extra_data_x_match_type",
    "extra_data_x_confidence",
]

def _load_matches_file(
    con: duckdb.DuckDBPyConnection | None = None,
    matches_file_path: str = "config/matches.xlsx",
    matches_table_label: str = "matches",
) -> None:

    matches_file = Path(matches_file_path)

    try:
        df: pl.DataFrame = pl.read_excel(
            str(matches_file),
            sheet_id=0,
        )["matched"]

        actual_columns = df.columns
        if actual_columns != EXPECTED_COLUMNS:
            raise FileReadFailure(
                table=DataFileInfo(
                    label=matches_table_label,
                    file=str(matches_file_path),
                    mandatory=True,
                    file_profile="clean",
                ),
                original_exception=ValueError(
                    f"Expected columns: {EXPECTED_COLUMNS}\n"
                    f"Found columns   : {actual_columns}"
                ),
            )

        table_arrow: pa.Table = df.to_arrow()
        con.register(matches_table_label, table_arrow)

    except Exception as e:
        raise FileReadFailure(
            table=DataFileInfo(
                label=matches_table_label,
                file=str(matches_file_path),
                mandatory=True,
                file_profile="clean",
            ),
            original_exception=e,
        ) from e


def _get_overlap_columns(
    con: duckdb.DuckDBPyConnection | None = None,
    table_name: str = "",
    overlap_start: int = -1,
    overlap_end: int = -1,
) -> list[str]:
    info = con.execute(
        f"PRAGMA table_info('{table_name}')"
    ).fetchall()

    overlap_columns: list[str] = []

    for _, name, *_ in info:
        try:
            value = int(name)
        except ValueError:
            continue

        if (
            overlap_start
            <= value
            <= overlap_end
        ):
            overlap_columns.append(name)

    if not overlap_columns:
        raise ValueError(
            f"No overlap columns found in table '{table_name}' "
            f"for interval "
            f"[{overlap_start} ; {overlap_end}]"
        )

    return overlap_columns
