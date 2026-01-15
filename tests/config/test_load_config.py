import pytest

from plotly_lvlos.config.load_config import load_config
from plotly_lvlos.errors.errors_config import (
    ConfigError,
    ConfigFileNotFound,
    ConfigFileInvalid,
)


def test_load_config_raises_for_empty_file(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("")

    with pytest.raises(ConfigError):
        load_config(config_file)


def test_load_config_raises_for_nonexistent_file(tmp_path):
    config_file = tmp_path / "missing.toml"

    with pytest.raises(ConfigFileNotFound):
        load_config(config_file)


def test_load_config_raises_for_invalid_toml(tmp_path):
    config_file = tmp_path / "invalid.toml"
    config_file.write_text("This is not valid TOML content")

    with pytest.raises(ConfigFileInvalid):
        load_config(config_file)
