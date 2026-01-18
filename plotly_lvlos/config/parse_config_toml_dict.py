from plotly_lvlos.errors.errors_config import (
    ConfigMissingSection,
    ConfigUnexpectedSection,
    ConfigMissingKey,
    ConfigUnexpectedKey,
)
from plotly_lvlos.config import CONFIG_TOML_DICT_SCHEMA


def parse_config_toml_dict(toml_dict) -> None:
    """
    Validate the structure of a parsed TOML configuration dictionary.

    This function enforces strict conformity with CONFIG_TOML_DICT_SCHEMA:
    - all required sections must be present
    - no unexpected sections are allowed
    - all required keys must be present in each section
    - no unexpected keys are allowed

    Parameters
    ----------
    toml_dict : dict
        Parsed TOML configuration dictionary.

    Raises
    ------
    ConfigMissingSection
        If a required section is missing.
    ConfigUnexpectedSection
        If an unknown section is present.
    ConfigMissingKey
        If a required key is missing from a section.
    ConfigUnexpectedKey
        If an unexpected key is present in a section.
    """
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
