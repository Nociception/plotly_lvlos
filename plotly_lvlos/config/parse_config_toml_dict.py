from plotly_lvlos.errors.errors_config import (
    ConfigMissingSection,
    ConfigUnexpectedSection,
    ConfigMissingKey,
    ConfigUnexpectedKey,
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

    for section_name, section_schema in CONFIG_TOML_DICT_SCHEMA.items():
        section_dict = toml_dict[section_name]

        schema_keys = set(section_schema.keys())
        dict_keys = set(section_dict.keys())

        if not schema_keys.issubset(dict_keys):
            raise ConfigMissingKey

        if not dict_keys.issubset(schema_keys):
            raise ConfigUnexpectedKey
