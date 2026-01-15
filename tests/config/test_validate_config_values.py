from pathlib import Path
import pytest
import copy

from plotly_lvlos.config.validate_config_values import (
    validate_config_values,
    _validate_file_exists,
)
from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA,
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)
from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFoundFatalError,
    ConfigFileNotFoundWarning,
    ConfigConstraintError,
)


@pytest.fixture
def valid_config_dict():
    return CONFIG_TOML_DICT_SCHEMA.copy()


@pytest.mark.parametrize("file_key", ["x_file", "y_file"])
def test_mandatory_data_file_missing_raises(valid_config_dict, file_key):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict["data"][file_key] = "nonexistent_file.csv"

    with pytest.raises(ConfigFileNotFoundFatalError):
        _validate_file_exists(test_dict["data"][file_key], mandatory=True)


@pytest.mark.parametrize("file_key", ["extra_data_point_file", "extra_data_x_file"])
def test_optional_data_file_missing_warns(valid_config_dict, file_key):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict["data"][file_key] = "nonexistent_file.csv"

    with pytest.warns(ConfigFileNotFoundWarning):
        _validate_file_exists(test_dict["data"][file_key], mandatory=False)


@pytest.mark.parametrize(
    "section,key,constraints",
    [
        (section, key, constraints)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key, constraints in keys.items()
        if constraints.get("type") is str and "len_min" in constraints
    ],
)
def test_string_len_min_constraint(section, key, constraints, valid_config_dict):
    test_dict = copy.deepcopy(valid_config_dict)

    invalid_value = ""
    test_dict[section][key] = invalid_value

    if constraints["len_min"] == 0:
        pytest.skip("len_min=0 allows empty string")

    with pytest.raises(ConfigConstraintError) as exc:
        validate_config_values(test_dict)

    assert f"{section}.{key}" in str(exc.value)


@pytest.mark.parametrize(
    "section,key,constraints",
    [
        (section, key, constraints)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key, constraints in keys.items()
        if constraints.get("type") is str and "len_max" in constraints
    ],
)
def test_string_len_max_constraint(section, key, constraints, valid_config_dict):
    test_dict = copy.deepcopy(valid_config_dict)

    invalid_value = "a" * (constraints["len_max"] + 1)
    test_dict[section][key] = invalid_value

    with pytest.raises(ConfigConstraintError):
        validate_config_values(test_dict)


@pytest.mark.parametrize(
    "section,key,constraints",
    [
        (section, key, constraints)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key, constraints in keys.items()
        if constraints.get("type") is str
        and constraints.get("strip") is True
        and constraints.get("len_min", 0) > 0
    ],
)
def test_string_strip_constraint(section, key, constraints, valid_config_dict):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict[section][key] = "   \n\t  "

    with pytest.raises(ConfigConstraintError):
        validate_config_values(test_dict)


@pytest.mark.parametrize(
    "section,key,constraints",
    [
        (section, key, constraints)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key, constraints in keys.items()
        if constraints.get("type") is int and "min" in constraints
    ],
)
def test_int_min_constraint(section, key, constraints, valid_config_dict):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict[section][key] = constraints["min"] - 1

    with pytest.raises(ConfigConstraintError):
        validate_config_values(test_dict)


@pytest.mark.parametrize(
    "section,key,constraints",
    [
        (section, key, constraints)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key, constraints in keys.items()
        if constraints.get("type") is int and "max" in constraints
    ],
)
def test_int_max_constraint(section, key, constraints, valid_config_dict):
    test_dict = copy.deepcopy(valid_config_dict)

    test_dict[section][key] = constraints["max"] + 1

    with pytest.raises(ConfigConstraintError):
        validate_config_values(test_dict)
