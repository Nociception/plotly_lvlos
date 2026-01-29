import polars as pl
import pyarrow as pa
import duckdb
from pathlib import Path
from plotly_lvlos.core_data.DataInfo import DataInfo
from plotly_lvlos.errors.errors_build_core_data import FileReadFailure


def _load_matches_file(
    con: duckdb.DuckDBPyConnection | None = None,
    matches_file_path: str = "config/matches.xlsx",
    matches_table_label: str = "matches",
) -> None:

    matches_file = Path(matches_file_path)

    try:
        df: pl.DataFrame = pl.read_excel(str(matches_file))

        table_arrow: pa.Table = df.to_arrow()

        con.register(matches_table_label, table_arrow)

    except Exception as e:
        raise FileReadFailure(
            table=DataInfo(
                label=matches_table_label,
                file=str(matches_file_path),
                mandatory=True,
                file_profile="clean",
            ),
            original_exception=e,
        ) from e
