class ConfigError(Exception):
    """Base exception for configuration file issues."""

class ConfigFileNotFound(ConfigError):
    """Raised when the configuration file is missing."""

class ConfigFileInvalid(ConfigError):
    """Raised when the configuration file is invalid (syntax error, etc.)."""
