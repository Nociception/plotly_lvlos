from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)
from plotly_lvlos.errors.errors_config import ConfigValueOutOfBounds


def validate_config_values(config_dict):
    for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items():

        section_dict = config_dict[section]
        for key, rules in keys.items():
            value = section_dict[key]

            if "min" in rules and value < rules["min"]:
                raise ConfigValueOutOfBounds(
                    f"Value of '{section}.{key}' is {value}, "
                    f"below minimum allowed {rules['min']}"
                )

            if "max" in rules and value > rules["max"]:
                raise ConfigValueOutOfBounds(
                    f"Value of '{section}.{key}' is {value}, "
                    f"above maximum allowed {rules['max']}"
                )

    return True
