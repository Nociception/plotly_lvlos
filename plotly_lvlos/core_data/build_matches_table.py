from pathlib import Path

import pandas as pd
import duckdb
import polars as pl
import pyarrow as pa

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

def _create_empty_matches_table(
    con: duckdb.DuckDBPyConnection | None = None,
    matches_table_label: str = ""
) -> None:

    con.execute(
        f"""
        CREATE TABLE {matches_table_label} (
            data_x VARCHAR,
            data_y VARCHAR,
            data_y_match_type VARCHAR,
            data_y_confidence DOUBLE,
            extra_data_point VARCHAR,
            extra_data_point_match_type VARCHAR,
            extra_data_point_confidence DOUBLE,
            extra_data_x VARCHAR,
            extra_data_x_match_type VARCHAR,
            extra_data_x_confidence DOUBLE
        )
        """
    )


def _insert_data_x_entities(
    con: duckdb.DuckDBPyConnection | None = None,
    data_x_table_label: str = "",
    matches_table_label: str = "",
    entity_column_label: str = "",
) -> None:
    
    con.execute(
        f"""
        INSERT INTO
            {matches_table_label} (data_x)
        SELECT
            {entity_column_label}
        FROM
            {data_x_table_label}
        """
    )


def _get_entities_from_table(
    con: duckdb.DuckDBPyConnection | None = None,
    table_label: str = "",
    entity_column_label: str = "",
) -> list:
    return [
        entity[0] for entity in con.execute(f"""
            SELECT
                {entity_column_label}
            FROM
                {table_label}
        """).fetchall()
    ]


def _write_matches_excel(
    df_matched: pd.DataFrame | None,
    df_unmatched: pd.DataFrame | None,
    output_path: str = "",
) -> None:
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        df_matched.to_excel(
            writer,
            sheet_name="matched",
            index=False,
        )
        df_unmatched.to_excel(
            writer,
            sheet_name="unmatched",
            index=False,
        )

        workbook = writer.book
        unmatched_ws = writer.sheets["unmatched"]

        unmatched_ws.freeze_panes(1, 0)

        confidence_cols = [
            i for i, col in enumerate(df_unmatched.columns)
            if col.endswith("_confidence")
        ]

        if confidence_cols:
            unmatched_ws.autofilter(
                0, 0,
                len(df_unmatched),
                len(df_unmatched.columns) - 1,
            )

        red_fmt = workbook.add_format(
            {"bg_color": "#FFC7CE"}
        )

        for col_idx in confidence_cols:
            unmatched_ws.conditional_format(
                1, col_idx,
                len(df_unmatched),
                col_idx,
                {
                    "type": "cell",
                    "criteria": "==",
                    "value": 0,
                    "format": red_fmt,
                },
            )


def _export_matches_excel(
    con: duckdb.DuckDBPyConnection | None,
    matches_table_label: str = "",
    output_path: str = "matches.xlsx",
) -> None:
    df_matched = con.execute(
        f"""
        SELECT *
        FROM {matches_table_label}
        WHERE data_x IS NOT NULL
        """
    ).df()

    df_unmatched = con.execute(
        f"""
        SELECT *
        FROM {matches_table_label}
        WHERE data_x IS NULL
        """
    ).df()

    _write_matches_excel(
        df_matched=df_matched,
        df_unmatched=df_unmatched,
        output_path=output_path,
    )


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
