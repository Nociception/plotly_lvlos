# Base exception/waring
class ErrorBuildCoreData(Exception):
    """Base exception for core data building issues."""


class WarningBuildCoreData(Warning):
    """Base warning for core data building issues."""


# validate_entity_first_column.py exceptions
class EntityColumnError(ErrorBuildCoreData):
    """Raised when the entity_column is not the first column in either data table."""


class EntityUniquenessError(ErrorBuildCoreData):
    """Raised when entities are not unique."""
