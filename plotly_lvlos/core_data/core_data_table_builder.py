import duckdb

from plotly_lvlos.core_data.DataFileInfo import DataFileInfo

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

def _build_core_data_table(
    con: duckdb.DuckDBPyConnection | None = None,
    entity_column_label: str = "",
    overlap_column_label: str = "",
    tables: list[DataFileInfo] = [],
) -> None:

    con.execute(f"""
        CREATE TABLE core_data AS
            WITH
                data_x_long AS (
                    SELECT
                        {entity_column_label},
                        CAST(col AS INTEGER) AS {overlap_column_label},
                        val AS data_x
                    FROM
                        data_x
                    UNPIVOT (
                        val FOR col IN ({tables['data_x'].overlap_columns_sql})
                    )
                ),

                data_y_long AS (
                    SELECT
                        {entity_column_label},
                        CAST(col AS INTEGER) AS {overlap_column_label},
                        val AS data_y
                    FROM
                        data_y
                    UNPIVOT (
                        val FOR col IN ({tables['data_y'].overlap_columns_sql})
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
                        val FOR col IN ({tables['extra_data_point'].overlap_columns_sql})
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
                        val FOR col IN ({tables['extra_data_x'].overlap_columns_sql})
                    )
                )

            SELECT
                dx.{entity_column_label} AS {entity_column_label},
                dx.{overlap_column_label} AS {overlap_column_label},
                dx.data_x AS data_x,
                NULL AS data_x_log,
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
