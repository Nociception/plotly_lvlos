from plotly_lvlos.config import CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS
from plotly_lvlos.errors.errors_config import (
    ConfigConstraintError,
    ConfigOverlapError,
)


def _check_olstart_lt_olend(overlap_start: int, overlap_end: int) -> None:
    """
    Check that overlap_start is less than overlap_end.

    Raises
    ------
    ConfigOverlapError
        If overlap_start is not less than overlap_end.
    """

    if overlap_start >= overlap_end:
        raise ConfigOverlapError()


def validate_config_values(config_dict: dict) -> None:
    """
    Validate configuration values against declared constraints.

    Constraints are defined in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS and include:
    - type checking
    - string length bounds
    - numeric min/max bounds
    - optional string stripping before validation

    Parameters
    ----------
    config_dict : dict
        Fully parsed configuration dictionary.

    Raises
    ------
    ConfigConstraintError
        If any configuration value violates its declared constraints.
    """

    for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items():
        section_dict = config_dict[section]

        for key, constraints in keys.items():
            value = section_dict[key]
            expected_type = constraints["type"]

            if expected_type is str:
                if constraints.get("strip"):
                    value = value.strip()

                length = len(value)
                len_min = constraints.get("len_min", 0)
                len_max = constraints.get("len_max", float("inf"))

                if "len_min" in constraints and length < len_min:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

                if "len_max" in constraints and length > len_max:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

            elif expected_type is int:
                if "min" in constraints and value < constraints["min"]:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

                if "max" in constraints and value > constraints["max"]:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

    _check_olstart_lt_olend(
        config_dict["data"]["overlap_start"],
        config_dict["data"]["overlap_end"],
    )
