from pathlib import Path
from plotly_lvlos.utils.errors import ConfigError


def load_config(path="config.toml"):
    path_obj = Path(path)
    if not path_obj.is_file():
        raise ConfigError(f"Config file not found: {path}")
    return None
