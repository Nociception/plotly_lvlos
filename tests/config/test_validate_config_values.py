from pathlib import Path
import pytest
import copy

from plotly_lvlos.config.validate_config_values import (
    validate_config_values,
    validate_file_exists,
)
from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA,
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)
from plotly_lvlos.errors.errors_config import (
    ConfigValueOutOfBounds,
    ConfigFileNotFoundFatalError,
    ConfigFileNotFoundWarning,
)


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


@pytest.mark.parametrize("file_key", ["x_file", "y_file"])
def test_mandatory_data_file_missing_raises(valid_config_dict, file_key):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict["data"][file_key] = "nonexistent_file.csv"

    with pytest.raises(ConfigFileNotFoundFatalError):
        validate_file_exists(test_dict["data"][file_key], mandatory=True)


@pytest.mark.parametrize("file_key", ["extra_data_point_file", "extra_data_x_file"])
def test_optional_data_file_missing_warns(valid_config_dict, file_key):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict["data"][file_key] = "nonexistent_file.csv"

    with pytest.warns(ConfigFileNotFoundWarning):
        validate_file_exists(test_dict["data"][file_key], mandatory=False)
