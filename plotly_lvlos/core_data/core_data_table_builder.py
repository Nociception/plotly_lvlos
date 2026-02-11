import duckdb

from plotly_lvlos.core_data.DataFileInfo import DataFileInfo
from plotly_lvlos.errors.errors_build_core_data import (
    Data_xValuePositivenessFailure,
)


def _build_data_x_long(
    con: duckdb.DuckDBPyConnection | None = None,
    entity_column_label: str = "",
    overlap_column_label: str = "",
    data_x_overlap_columns_sql: str = "",
) -> None:
    con.execute(f"""
        CREATE TABLE data_x_long AS
            SELECT
                {entity_column_label},
                CAST(col AS INTEGER) AS {overlap_column_label},
                val AS data_x
            FROM
                data_x
            UNPIVOT (
                val FOR col IN ({data_x_overlap_columns_sql})
            )
    """)


def _check_strictly_positive_data_x_values(
    con: duckdb.DuckDBPyConnection | None = None,
) -> None:
    invalid = con.execute("""
        SELECT
            COUNT(*)
        FROM
            data_x_long
        WHERE
            data_x <= 0
    """).fetchone()[0]
    if invalid > 0:
        raise Data_xValuePositivenessFailure(
            f"Invalid data_x values: {invalid} values <= 0. "
            "Logarithmic scale requires strictly positive data."
        )


def _build_core_data_table(
    con: duckdb.DuckDBPyConnection | None = None,
    entity_column_label: str = "",
    overlap_column_label: str = "",
    tables: dict[str, DataFileInfo] = [],
) -> None:
    _build_data_x_long(
        con=con,
        entity_column_label=entity_column_label,
        overlap_column_label=overlap_column_label,
        data_x_overlap_columns_sql=tables["data_x"].overlap_columns_sql,
    )
    _check_strictly_positive_data_x_values(con=con)

    con.execute(f"""
        CREATE TABLE core_data AS
            WITH
                data_y_long AS (
                    SELECT
                        {entity_column_label},
                        CAST(col AS INTEGER) AS {overlap_column_label},
                        val AS data_y
                    FROM
                        data_y
                    UNPIVOT (
                        val FOR col IN ({tables["data_y"].overlap_columns_sql})
                    )
                ),

                extra_data_point_long AS (
                    SELECT
                        {entity_column_label},
                        CAST(col AS INTEGER) AS {overlap_column_label},
                        val AS extra_data_point
                    FROM
                        extra_data_point
                    UNPIVOT (
                        val FOR col IN ({tables["extra_data_point"].overlap_columns_sql})
                    )
                ),

                extra_data_x_long AS (
                    SELECT
                        {entity_column_label},
                        CAST(col AS INTEGER) AS {overlap_column_label},
                        val AS extra_data_x
                    FROM
                        extra_data_x
                    UNPIVOT (
                        val FOR col IN ({tables["extra_data_x"].overlap_columns_sql})
                    )
                )

            SELECT
                dx.{entity_column_label} AS {entity_column_label},
                dx.{overlap_column_label} AS {overlap_column_label},
                dx.data_x AS data_x,
                LOG10(dx.data_x) AS data_x_log,
                dy.data_y AS data_y,
                edp.extra_data_point AS extra_data_point,
                edx.extra_data_x AS extra_data_x

            FROM
                data_x_long AS dx

            LEFT JOIN
                matches AS m
                    ON m.data_x = dx.{entity_column_label}

            LEFT JOIN
                data_y_long AS dy
                    ON dy.{entity_column_label} = m.data_y
                    AND dy.{overlap_column_label} = dx.{overlap_column_label}

            LEFT JOIN
                extra_data_point_long AS edp
                    ON edp.{entity_column_label} = m.extra_data_point
                    AND edp.{overlap_column_label} = dx.{overlap_column_label}

            LEFT JOIN
                extra_data_x_long AS edx
                    ON edx.{entity_column_label} = m.extra_data_x
                    AND edx.{overlap_column_label} = dx.{overlap_column_label}
            
            ORDER BY
                {entity_column_label},
                {overlap_column_label}
    """)
