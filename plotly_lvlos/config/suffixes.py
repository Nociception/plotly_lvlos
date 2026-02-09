from pathlib import Path
import tomllib

from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFound,
    ConfigFileInvalid,
    SuffixesInvalidSchema,
)


def _parse_suffixes_toml(suffixes_dict: dict, file_path: Path) -> None:

    if "suffixes" not in suffixes_dict:
        raise SuffixesInvalidSchema(
            f"Missing required [suffixes] section in {file_path.resolve()}"
        )

    suffixes = suffixes_dict["suffixes"]

    if not isinstance(suffixes, dict) or not suffixes:
        raise SuffixesInvalidSchema(
            f"[suffixes] section must be a non-empty table in {file_path.resolve()}"
        )

    non_numeric = [
        key for key, value in suffixes.items()
        if not isinstance(value, (int, float))
    ]

    if non_numeric:
        raise SuffixesInvalidSchema(
            f"Suffixes {non_numeric} have non-numeric values in {file_path.resolve()}"
        )


def load_suffixes_toml(toml_dict: dict) -> None:

    default_suffixes_path = Path("config/default_suffixes.toml")
    if not default_suffixes_path.exists():
        raise ConfigFileNotFound(
            f"Default suffixes TOML file not found: {default_suffixes_path.resolve()}"
        )

    def _load_one_suffixes_file(path: Path) -> dict[str, dict[str, float]]:
        try:
            with path.open("rb") as f:
                return {"suffixes": {k: float(v) for k, v in tomllib.load(f)["suffixes"].items()}}
        except tomllib.TOMLDecodeError as exc:
            raise ConfigFileInvalid(f"Invalid suffixes TOML file: {path.resolve()}") from exc


    default_loaded = _load_one_suffixes_file(default_suffixes_path)
    _parse_suffixes_toml(default_loaded, default_suffixes_path)
    suffixes_dict = {"default": default_loaded}

    for data in ("data_x", "data_y", "extra_data_point", "extra_data_x"):
        override_path = Path(f"config/{data}_suffixes.toml")
        if override_path.exists():
            loaded_suffixes_file = _load_one_suffixes_file(override_path)
            _parse_suffixes_toml(loaded_suffixes_file, override_path)
            suffixes_dict[data] = loaded_suffixes_file

    toml_dict["suffixes"] = suffixes_dict
