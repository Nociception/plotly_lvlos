from pathlib import Path
import tomllib

from plotly_lvlos.utils.errors import ConfigError


def load_config(path="config.toml"):
    path_obj = Path(path)

    if not path_obj.is_file():
        raise ConfigError(f"Config file not found: {path}")

    try:
        with path_obj.open("rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Invalid TOML config: {path}") from exc
