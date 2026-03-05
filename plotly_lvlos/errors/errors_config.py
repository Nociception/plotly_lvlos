# Base exception/waring
class ErrorConfig(Exception):
    """Base exception for configuration file issues."""


class ConfigWarning(Warning):
    """Base warning for configuration file issues."""


# load_config.py exceptions
class ConfigFileNotFound(ErrorConfig):
    """Raised when the configuration file is missing."""


class ConfigFileInvalid(ErrorConfig):
    """Raised when the configuration file is invalid (syntax error, etc.)."""


# parse_config_toml_dict.py exceptions
class ConfigMissingSection(ErrorConfig):
    """Raised when a required section is missing from the configuration."""


class ConfigUnexpectedSection(ErrorConfig):
    """Raised when an unexpected section is found in the configuration."""


class ConfigMissingKey(ErrorConfig):
    """Raised when a required key is missing from a configuration section."""


class ConfigUnexpectedKey(ErrorConfig):
    """Raised when an unexpected key is found in a configuration section."""


# validate_config_values.py exceptions
class ConfigFileNotFoundFatalError(ErrorConfig):
    """
    Raised when a required data file specified in the configuration is missing.
    This is considered a fatal error.
    """


class ConfigFileNotFoundWarning(ConfigWarning):
    """
    Warns when an optional data file specified in the configuration is missing.
    """


class ConfigValueOutOfBounds(ErrorConfig):
    """
    Raised when a configuration value is invalid (out of range, etc.).
    Please read the confi_toml_dict_schema.py file
    for the expected structure and values.
    """


class ConfigOverlapError(ErrorConfig):
    """
    Raised when overlap_start is not less than overlap_end.
    """


class ConfigConstraintError(ErrorConfig):
    """
    Raised when a configuration value violates declared constraints.
    """

    def __init__(
        self,
        section: str,
        key: str,
        value,
        constraints: dict,
    ):
        self.section = section
        self.key = key
        self.value = value
        self.constraints = constraints

        constraint_lines = "\n".join(
            f"- {name}: {repr(val)}" for name, val in constraints.items()
        )

        message = (
            f"Invalid value for config field "
            f"[{section}.{key}]\n"
            f"Value: {repr(value)}\n"
            f"Constraints:\n{constraint_lines}"
        )

        super().__init__(message)


# suffixes.py
class SuffixesInvalidSchema(ErrorConfig):
    """
    Raised when a suffixes value violates declared constraints.
    """
