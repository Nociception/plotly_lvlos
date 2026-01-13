from pathlib import Path


def load_config(path):
    path = Path(path)

    if path.exists():
        return {}

    raise FileNotFoundError
