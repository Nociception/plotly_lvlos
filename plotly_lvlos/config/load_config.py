from pathlib import Path

from plotly_lvlos.utils.errors import ConfigError


def load_config(path):
    path = Path(path)

    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    return {}
