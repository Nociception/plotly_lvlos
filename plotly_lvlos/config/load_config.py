from pathlib import Path
import tomllib

from plotly_lvlos.config.parse_config_toml_dict import parse_config_toml_dict
from plotly_lvlos.config.validate_config_values import validate_config_values
from plotly_lvlos.config.validate_files_exist import validate_files_exist
from plotly_lvlos.config.sanitize_config_sql_identifiers import (
    sanitize_config_sql_identifiers,
)
from plotly_lvlos.config.suffixes import load_suffixes_toml
from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFound,
    ConfigFileInvalid,
)


def load_config(config_path: Path | None = None) -> dict:
    
    if not config_path.exists():
        raise ConfigFileNotFound(f"Config file not found: {config_path}")
    
    try:
        with config_path.open("rb") as f:
            toml_dict = tomllib.load(f)
            parse_config_toml_dict(toml_dict)
            validate_config_values(toml_dict)
            validate_files_exist(toml_dict)
            sanitize_config_sql_identifiers(toml_dict)

            load_suffixes_toml(toml_dict)

            return toml_dict
    except tomllib.TOMLDecodeError as exc:
        raise ConfigFileInvalid(f"Invalid config TOML: {config_path}") from exc
