import polars as pl

from plotly_lvlos.core_data.DataFileInfo import DataFileInfo
from plotly_lvlos.core_data.csv_profiles import CSV_PROFILES
from plotly_lvlos.errors.errors_build_core_data import (
    EntityColumnFailure,
    EntityUniquenessFailure,
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






















def _build_suffix_multiplier_expr(
    col: pl.Expr,
    suffixes: dict[str, float],
) -> pl.Expr:
    """
    Given a string column expression, extract suffix and apply multiplier.
    """
    # extract numeric part
    number = col.str.extract(r"^([+-]?\d*\.?\d+)", 1).cast(pl.Float64)

    # extract suffix (letters or µ)
    suffix = col.str.extract(r"([a-zA-Zµ]+)$", 1)

    # default multiplier = 1
    multiplier = pl.lit(1.0)

    for suf, factor in suffixes.items():
        multiplier = pl.when(suffix == suf).then(factor).otherwise(multiplier)

    return number * multiplier




def _convert_according_to_suffixes(
    table: DataFileInfo,
    default_suffixes: dict[str, float],
) -> None:

    df = table.df
    options = table.suffixes.get("options", {}) if table.suffixes else {}

    case_sensitive = options.get("case_sensitive", False)
    allow_unicode_micro = options.get("allow_unicode_micro", True)

    suffixes = default_suffixes.copy()

    # normalize suffix keys
    if not case_sensitive:
        suffixes = {k.lower(): v for k, v in suffixes.items()}

    if allow_unicode_micro and "u" in suffixes:
        suffixes["µ"] = suffixes["u"]

    # columns to convert = all except entity column
    entity_col = df.columns[0]
    value_columns = df.columns[1:]

    new_columns = []

    for col_name in value_columns:
        col = pl.col(col_name)

        expr = col

        if not case_sensitive:
            expr = expr.str.to_lowercase()

        expr = _build_suffix_multiplier_expr(
            col=expr,
            suffixes=suffixes,
        )

        new_columns.append(expr.alias(col_name))

    table.df = df.with_columns(new_columns)
