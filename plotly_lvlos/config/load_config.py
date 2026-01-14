from pathlib import Path
import tomllib

from plotly_lvlos.errors.errors_config import ConfigFileNotFound, ConfigFileInvalid


def load_config(path):
    path = Path(path)

    if not path.exists():
        raise ConfigFileNotFound(f"Config file not found: {path}")

    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigFileInvalid(f"Invalid TOML config: {path}") from exc
