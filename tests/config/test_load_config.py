import pytest
from pathlib import Path

from plotly_lvlos.config import load_config
from plotly_lvlos.errors.errors_config import (
    ConfigError,
    ConfigFileNotFound,
    ConfigFileInvalid,
    ConfigConstraintError,
)
from tests.config.conftest import write_valid_config


def test_load_config_raises_for_empty_file(tmp_path: Path) -> None:
    """Verify that load_config raises ConfigError when the file is empty."""
    config_file: Path = tmp_path / "config.toml"
    config_file.write_text("")

    with pytest.raises(ConfigError):
        load_config(config_file)


def test_load_config_raises_for_nonexistent_file(tmp_path: Path) -> None:
    """
    Verify that load_config raises ConfigFileNotFound
    when the file does not exist.
    """
    config_file: Path = tmp_path / "missing.toml"

    with pytest.raises(ConfigFileNotFound):
        load_config(config_file)


def test_load_config_raises_for_invalid_toml(tmp_path: Path) -> None:
    """
    Verify that load_config raises
    ConfigFileInvalid for invalid TOML content.
    """
    config_file: Path = tmp_path / "invalid.toml"
    config_file.write_text("This is not valid TOML content")

    with pytest.raises(ConfigFileInvalid):
        load_config(config_file)


def test_load_config_valid_file(tmp_path: Path) -> None:
    config_file = write_valid_config(tmp_path)

    (tmp_path / "x.csv").touch()
    (tmp_path / "y.csv").touch()

    config = load_config(config_file)
    assert isinstance(config, dict)
    assert "data" in config


def test_load_config_missing_file_raises() -> None:
    with pytest.raises(ConfigFileNotFound):
        load_config(Path("does_not_exist.toml"))


def test_load_config_invalid_toml_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text("this = = not valid toml")

    with pytest.raises(ConfigFileInvalid):
        load_config(config_file)


def test_load_config_invalid_values(tmp_path: Path) -> None:
    config_file = write_valid_config(
        tmp_path, overrides={"analysis": {"min_points_per_year": 1}}
    )

    (tmp_path / "x.csv").touch()
    (tmp_path / "y.csv").touch()

    with pytest.raises(ConfigConstraintError):
        load_config(config_file)
