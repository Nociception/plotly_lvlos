from typing import Any, Dict, Optional
import pytest
from pathlib import Path
import tomli_w

from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA,
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)


@pytest.fixture
def valid_config_dict() -> dict:
    """Provide a valid configuration dictionary fixture for tests."""
    return CONFIG_TOML_DICT_SCHEMA.copy()


def write_valid_config(
    tmp_path: Path, overrides: Optional[Dict[str, Dict[str, Any]]] = None
) -> Path:
    """
    Create a fully valid TOML configuration file according to the schema
    and constraints, and write it to tmp_path/config.toml.
    Mandatory files are created automatically.

    Parameters
    ----------
    tmp_path : Path
        Directory where to write the TOML file.
    overrides : dict of dict, optional
        Optional dictionary to override specific values.
        Example: {"analysis": {"min_points_per_year": 10}}

    Returns
    -------
    Path
        Path to the written TOML file.
    """
    config: Dict[str, Dict[str, Any]] = {}

    for section, keys in CONFIG_TOML_DICT_SCHEMA.items():
        config[section] = {}
        for key, default in keys.items():
            constraints = CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.get(section, {}).get(
                key, {}
            )

            if constraints.get("type") is str:
                if section == "data" and key in ("x_file", "y_file"):
                    file_path = tmp_path / f"{key}.csv"
                    file_path.touch()
                    value = str(file_path)
                else:
                    len_min = constraints.get("len_min", 1)
                    value = "a" * max(1, len_min)
            elif constraints.get("type") is int:
                if section == "data" and key == "overlap_start":
                    value = 1800
                elif section == "data" and key == "overlap_end":
                    value = 2050
                else:
                    min_val = constraints.get("min", 0)
                    value = max(min_val, 1)
            else:
                value = default

            config[section][key] = value

    if overrides:
        for section, keys in overrides.items():
            if section not in config:
                config[section] = {}
            for key, value in keys.items():
                config[section][key] = value

    config_file = tmp_path / "config.toml"

    with config_file.open("wb") as f:
        tomli_w.dump(config, f)

    return config_file
