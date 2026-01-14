import pytest
import copy

from plotly_lvlos.config.validate_config_values import validate_config_values
from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA,
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)
from plotly_lvlos.errors.errors_config import ConfigValueOutOfBounds


@pytest.fixture
def valid_config_dict():
    return CONFIG_TOML_DICT_SCHEMA.copy()


@pytest.mark.parametrize(
    "section,key",
    [
        (section, key)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key in keys.keys()
    ],
)
def test_constraints_min_max(valid_config_dict, section, key):
    test_dict = copy.deepcopy(valid_config_dict)
    rules = CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS[section][key]

    if "min" in rules:
        test_dict[section][key] = rules["min"] - 1
        with pytest.raises(ConfigValueOutOfBounds):
            validate_config_values(test_dict)

    if "max" in rules:
        test_dict[section][key] = rules["max"] + 1
        with pytest.raises(ConfigValueOutOfBounds):
            validate_config_values(test_dict)
