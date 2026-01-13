from pathlib import Path

from plotly_lvlos.utils.errors import ConfigFileNotFound


def load_config(path):
    path = Path(path)

    if not path.exists():
        raise ConfigFileNotFound(f"Config file not found: {path}")

    return {}
