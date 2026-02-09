import polars as pl
import duckdb

from plotly_lvlos.core_data.DataFileInfo import DataFileInfo
from plotly_lvlos.core_data.csv_profiles import CSV_PROFILES
from plotly_lvlos.errors.errors_build_core_data import (
    EntityColumnFailure,
    EntityUniquenessFailure,
    Data_xValuePositivenessFailure,
)


def _extract_as_all_varchar(table: DataFileInfo) -> pl.DataFrame:
    df = pl.read_csv(
        source=table.file,
        infer_schema_length=0,
        quote_char='"',
        **CSV_PROFILES[table.file_profile]
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
    

def _validate_first_column_entities_uniqueness(
    table: DataFileInfo,
    entity_column_label: str
) -> None:

    with pl.SQLContext() as ctx:
        ctx.register("tmp_table", table.df)
        query = f"""
            SELECT 
                "{entity_column_label}",
                COUNT(*) AS occurences
            FROM
                tmp_table
            GROUP BY
                "{entity_column_label}"
            HAVING
                COUNT(*) > 1 OR "{entity_column_label}" IS NULL
        """
        result_df = ctx.execute(query).collect()

    if result_df.height > 0:
        messages = []
        for row in result_df.iter_rows():
            val, count = row
            if val is None:
                messages.append(f"{count} null value(s)")
            else:
                messages.append(f"'{val}' appears {count} times")
        dup_msg_str = "; ".join(messages)
        raise EntityUniquenessFailure(
            f"In table '{table.label}', entity column '{entity_column_label}' "
            f"contains duplicated or null values: {dup_msg_str}."
        )


def _convert_according_to_suffixes(table: DataFileInfo, default_suffixes: dict[str, float]) -> None:
    suffixes_dict = table.suffixes if table.suffixes else default_suffixes
    suffixes_dict = suffixes_dict["suffixes"]
    num_cols = table.overlap_columns
    table.df = table.df.with_columns([
        (
            pl.col(col).cast(pl.Utf8)
            .str.extract(r"(-?[0-9]+(?:\.[0-9]+)?)", 1)
            .cast(pl.Float64)
            *
            pl.col(col).str.extract(r"([A-Za-zµ]+)$", 1)
            .replace(suffixes_dict)
            .cast(pl.Float64)
            .fill_null(1.0)
        ).alias(col)
        for col in num_cols
    ])


def _load_into_duckdb(
    duckdb_conn: duckdb.DuckDBPyConnection | None = None,
    table: DataFileInfo | None = None,
) -> None:
    duckdb_conn.execute(f"DROP TABLE IF EXISTS {table.label}")
    duckdb_conn.register("arrow_tmp", table.df.to_arrow())
    duckdb_conn.execute(f"""
        CREATE TABLE
            {table.label} AS
                SELECT
                    *
                FROM
                    arrow_tmp
    """)
    duckdb_conn.unregister("arrow_tmp")
