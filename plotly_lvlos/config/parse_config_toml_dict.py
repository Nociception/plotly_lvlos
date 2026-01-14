from plotly_lvlos.errors.errors_config import (
    ConfigMissingSection,
    ConfigUnexpectedSection,
)
from plotly_lvlos.config.config_toml_dict_schema import CONFIG_TOML_DICT_SCHEMA


def parse_config_toml_dict(toml_dict):
    """"""
    for section in CONFIG_TOML_DICT_SCHEMA.keys():
        if section not in toml_dict:
            raise ConfigMissingSection

    for section in toml_dict.keys():
        if section not in CONFIG_TOML_DICT_SCHEMA:
            raise ConfigUnexpectedSection
    return True
