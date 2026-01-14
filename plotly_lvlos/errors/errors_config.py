class ConfigError(Exception):
    """Base exception for configuration file issues."""

class ConfigFileNotFound(ConfigError):
    """Raised when the configuration file is missing."""

class ConfigFileInvalid(ConfigError):
    """Raised when the configuration file is invalid (syntax error, etc.)."""


class ConfigMissingSection(ConfigError):
    """Raised when a required section is missing from the configuration."""

class ConfigUnexpectedSection(ConfigError):
    """Raised when an unexpected section is found in the configuration."""

class ConfigMissingKey(ConfigError):
    """Raised when a required key is missing from a configuration section."""

class ConfigUnexpectedKey(ConfigError):
    """Raised when an unexpected key is found in a configuration section."""

class ConfigInvalidSectionType(ConfigError):
    """Raised when a section has an invalid type."""
