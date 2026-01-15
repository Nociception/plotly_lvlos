from pathlib import Path
import tomllib

from typeguard import typechecked

from plotly_lvlos.config.parse_config_toml_dict import parse_config_toml_dict
from plotly_lvlos.config.validate_config_values import (
    validate_config_values,
    validate_files_exist,
)

from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFound,
    ConfigFileInvalid,
)


@typechecked
def load_config(path: Path):

    if not path.exists():
        raise ConfigFileNotFound(f"Config file not found: {path}")

    try:
        with path.open("rb") as f:
            return_dict = tomllib.load(f)
            parse_config_toml_dict(return_dict)
            validate_config_values(return_dict)
            validate_files_exist(return_dict)
            return return_dict
    except tomllib.TOMLDecodeError as exc:
        raise ConfigFileInvalid(f"Invalid TOML config: {path}") from exc
