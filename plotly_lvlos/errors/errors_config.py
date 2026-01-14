# Base exception
class ConfigError(Exception):
    """Base exception for configuration file issues."""


# load_config.py exceptions
class ConfigFileNotFound(ConfigError):
    """Raised when the configuration file is missing."""


class ConfigFileInvalid(ConfigError):
    """Raised when the configuration file is invalid (syntax error, etc.)."""


# parse_config_toml_dict.py exceptions
class ConfigMissingSection(ConfigError):
    """Raised when a required section is missing from the configuration."""


class ConfigUnexpectedSection(ConfigError):
    """Raised when an unexpected section is found in the configuration."""


class ConfigMissingKey(ConfigError):
    """Raised when a required key is missing from a configuration section."""


class ConfigUnexpectedKey(ConfigError):
    """Raised when an unexpected key is found in a configuration section."""


class ConfigInvalidValueType(ConfigError):
    """Raised when a section has an invalid type."""


# validate_config_values.py exceptions
class ConfigValueOutOfBounds(ConfigError):
    """
    Raised when a configuration value is invalid (out of range, etc.).
    Please read the confi_toml_dict_schema.py file
    for the expected structure and values.
    """
