import re


def _safe_sql_identifier(config_field: str) -> str:
    safe = re.sub(r"[^0-9a-zA-Z]", "_", config_field)
    safe = re.sub(r"_+", "_", safe)
    safe = safe.strip("_")
    if re.match(r"^\d", safe):
        safe = "_" + safe
    return safe


def sanitize_config_sql_identifiers(config_dict: dict) -> str:
    for config_field in ["entity_column", "overlap_column"]:
        config_dict["data"][config_field] = _safe_sql_identifier(
            config_dict["data"][config_field]
        )
