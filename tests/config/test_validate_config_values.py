import pytest
import copy

from plotly_lvlos.config.validate_config_values import (
    validate_config_values,
)
from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)
from plotly_lvlos.errors.errors_config import (
    ConfigConstraintError,
    ConfigOverlapError,
)


@pytest.mark.parametrize(
    "section,key,constraints",
    [
        (section, key, constraints)
        for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items()
        for key, constraints in keys.items()
        if constraints.get("type") is str and "len_min" in constraints
    ],
)
def test_string_len_min_constraint(
    section: str, key: str, constraints: dict, valid_config_dict: dict
) -> None:
    """Check that strings shorter than len_min raise a ConfigConstraintError."""
    test_dict = copy.deepcopy(valid_config_dict)

    invalid_value: str = ""
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
def test_string_len_max_constraint(
    section: str, key: str, constraints: dict, valid_config_dict: dict
) -> None:
    """Check that strings longer than len_max raise a ConfigConstraintError."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

    invalid_value: str = "a" * (constraints["len_max"] + 1)
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
def test_string_strip_constraint(
    section: str, key: str, constraints: dict, valid_config_dict: dict
) -> None:
    """Check that strings containing only whitespace raise a ConfigConstraintError."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

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
def test_int_min_constraint(
    section: str, key: str, constraints: dict, valid_config_dict: dict
) -> None:
    """Check that integers below the min value raise a ConfigConstraintError."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

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
def test_int_max_constraint(
    section: str, key: str, constraints: dict, valid_config_dict: dict
) -> None:
    """Check that integers above the max value raise a ConfigConstraintError."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

    test_dict[section][key] = constraints["max"] + 1

    with pytest.raises(ConfigConstraintError):
        validate_config_values(test_dict)


@pytest.mark.parametrize(
    "ol_start,ol_end",
    [
        (2050, 1800),
        (2000, 1800),
        (1800, 1800),
        (2001, 2000),
    ],
)
def test_overlap_start_end_constraints(
    valid_config_dict: dict, ol_start: int, ol_end: int
) -> None:
    """Check that overlap_start is less than overlap_end."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

    test_dict["data"]["overlap_start"] = ol_start
    test_dict["data"]["overlap_end"] = ol_end

    with pytest.raises(ConfigOverlapError) as exc:
        validate_config_values(test_dict)

    assert "data.overlap_start" in str(exc.value)
    assert "data.overlap_end" in str(exc.value)
