import pytest

from plotly_lvlos.config.parse_config_toml_dict import parse_config_toml_dict
from plotly_lvlos.config.config_toml_dict_schema import CONFIG_TOML_DICT_SCHEMA

from plotly_lvlos.errors.errors_config import (
    ConfigMissingSection,
    ConfigUnexpectedSection,
    ConfigMissingKey,
    ConfigUnexpectedKey,
)


def test_parse_toml_dict_passes_for_valid_dict(valid_config_dict: dict) -> None:
    """The valid config should pass validation"""
    assert parse_config_toml_dict(valid_config_dict) is None


@pytest.mark.parametrize("missing_section", CONFIG_TOML_DICT_SCHEMA.keys())
def test_parse_toml_dict_fails_when_section_missing(
    valid_config_dict: dict, missing_section: str
) -> None:
    """Removing any section must raise an error."""

    test_dict: dict = valid_config_dict.copy()

    test_dict.pop(missing_section)

    with pytest.raises(ConfigMissingSection):
        parse_config_toml_dict(test_dict)


@pytest.mark.parametrize("extra_section", ["extra1", "extra2", "extra3"])
def test_parse_toml_dict_fails_when_extra_section_present(
    valid_config_dict: dict, extra_section: str
) -> None:
    """Adding any extra section must raise an error."""

    test_dict = valid_config_dict.copy()

    test_dict[extra_section] = {}

    with pytest.raises(ConfigUnexpectedSection):
        parse_config_toml_dict(test_dict)


@pytest.mark.parametrize(
    "section_name,key_name",
    [
        (section, key)
        for section, keys in CONFIG_TOML_DICT_SCHEMA.items()
        for key in keys.keys()
    ],
)
def test_parse_toml_dict_fails_when_key_missing(
    valid_config_dict: dict, section_name: str, key_name: str
) -> None:
    """Removing any required key must raise ConfigMissingKey."""

    test_dict: dict = valid_config_dict.copy()

    section_dict: dict = test_dict[section_name].copy()
    section_dict.pop(key_name)

    test_dict[section_name] = section_dict

    with pytest.raises(ConfigMissingKey):
        parse_config_toml_dict(test_dict)


@pytest.mark.parametrize(
    "section_name, unexpected_key",
    [(section, "unexpected_key") for section in CONFIG_TOML_DICT_SCHEMA.keys()],
)
def test_parse_toml_dict_fails_when_unexpected_key_present(
    valid_config_dict: dict, section_name: str, unexpected_key: str
) -> None:
    """Adding any unexpected key inside a section must raise an error."""

    test_dict: dict = valid_config_dict.copy()
    test_dict[section_name] = test_dict[section_name].copy()

    test_dict[section_name][unexpected_key] = "whatever"

    with pytest.raises(ConfigUnexpectedKey):
        parse_config_toml_dict(test_dict)
