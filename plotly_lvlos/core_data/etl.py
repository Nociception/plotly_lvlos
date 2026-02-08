import polars as pl


def _convert_suffixes_to_numeric(
    df: pl.DataFrame | None = None,
    suffixes: dict | None = None,
    overlap_start: int | None = None,
    overlap_end: int | None = None,
) -> pl.DataFrame :
    suffix_map = suffixes["suffixes"]
    options = suffixes["options"]
    
    # Normalisation de la casse si nécessaire
    case_sensitive = options.get("case_sensitive", False)
    allow_unicode_micro = options.get("allow_unicode_micro", True)
    
    # Déterminer les colonnes à transformer
    overlap_cols = [
        col for col in df.columns
        if df[col].dtype in [pl.Utf8, pl.Int64, pl.Float64]  # varchar ou numérique
        and df[col].min() >= overlap_start
        and df[col].max() <= overlap_end
    ]
    
    for col in overlap_cols:
        col_expr = pl.col(col).cast(pl.Utf8)

        if allow_unicode_micro:
            col_expr = col_expr.str.replace("µ", "u")

        if not case_sensitive:
            col_expr = col_expr.str.to_uppercase()
            suffix_map = {k.upper(): v for k, v in suffix_map.items()}

        # Extraction nombre + suffixe
        parsed = col_expr.str.extract(r"^([-+]?[0-9]*\.?[0-9]+)([a-zA-Z]*)$")

        num = parsed.arr.get(0).cast(pl.Float64)
        suf = parsed.arr.get(1)

        # Transformation vectorisée via mapping Python
        df = df.with_column(
            (num * suf.map_dict(suffix_map, default=1.0)).alias(col)
        )

    return df