import pytest

from plotly_lvlos.config.parse_config_toml_dict import parse_config_toml_dict
from plotly_lvlos.config.config_toml_dict_schema import CONFIG_TOML_DICT_SCHEMA

from plotly_lvlos.errors.errors_config import (
    ConfigMissingSection,
    ConfigUnexpectedSection,
    ConfigMissingKey,
    ConfigUnexpectedKey,
    ConfigInvalidValueType,
)


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


@pytest.mark.parametrize("extra_section", ["extra1", "extra2", "extra3"])
def test_parse_toml_dict_fails_when_extra_section_present(
    valid_config_dict, extra_section
):
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
    valid_config_dict, section_name, key_name
):
    """Removing any required key must raise ConfigMissingKey."""

    test_dict = valid_config_dict.copy()

    section_dict = test_dict[section_name].copy()
    section_dict.pop(key_name)

    test_dict[section_name] = section_dict

    with pytest.raises(ConfigMissingKey):
        parse_config_toml_dict(test_dict)


@pytest.mark.parametrize(
    "section_name, unexpected_key",
    [(section, "unexpected_key") for section in CONFIG_TOML_DICT_SCHEMA.keys()],
)
def test_parse_toml_dict_fails_when_unexpected_key_present(
    valid_config_dict, section_name, unexpected_key
):
    """Adding any unexpected key inside a section must raise an error."""

    test_dict = valid_config_dict.copy()
    test_dict[section_name] = test_dict[section_name].copy()

    test_dict[section_name][unexpected_key] = "whatever"

    with pytest.raises(ConfigUnexpectedKey):
        parse_config_toml_dict(test_dict)


@pytest.mark.parametrize(
    "section_name,key_name",
    [
        (section, key)
        for section, keys in CONFIG_TOML_DICT_SCHEMA.items()
        for key in keys.keys()
    ],
)
def test_parse_toml_dict_fails_when_value_has_invalid_type(
    valid_config_dict, section_name, key_name
):
    """
    Any key with a value of an invalid type must raise ConfigInvalidValueType.
    """

    test_dict = valid_config_dict.copy()
    test_dict[section_name] = test_dict[section_name].copy()

    reference_value = CONFIG_TOML_DICT_SCHEMA[section_name][key_name]
    expected_type = type(reference_value)

    if expected_type is int:
        test_dict[section_name][key_name] = "not an int"
    else:
        test_dict[section_name][key_name] = 123

    with pytest.raises(ConfigInvalidValueType):
        parse_config_toml_dict(test_dict)
