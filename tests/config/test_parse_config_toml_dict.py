import pytest

from plotly_lvlos.config.parse_config_toml_dict import parse_config_toml_dict
from plotly_lvlos.config.config_toml_dict_schema import CONFIG_TOML_DICT_SCHEMA

from plotly_lvlos.errors.errors_config import ConfigMissingSection

@pytest.fixture
def valid_config_dict():
    return CONFIG_TOML_DICT_SCHEMA.copy()


def test_parse_toml_dict_passes_for_valid_dict(valid_config_dict):
    """The valid config should pass validation"""
    assert parse_config_toml_dict(valid_config_dict) is True


@pytest.mark.parametrize("missing_section", CONFIG_TOML_DICT_SCHEMA.keys())
def test_parse_toml_dict_fails_when_section_missing(valid_config_dict, missing_section):
    """Removing any section must raise an error."""

    test_dict = valid_config_dict.copy()

    test_dict.pop(missing_section)

    with pytest.raises(ConfigMissingSection):
        parse_config_toml_dict(test_dict)
