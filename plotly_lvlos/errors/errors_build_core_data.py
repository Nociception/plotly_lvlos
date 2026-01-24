# Base exception/waring
class ErrorBuildCoreData(Exception):
    """Base exception for core data building issues."""


class WarningBuildCoreData(Warning):
    """Base warning for core data building issues."""


# load_core_raw_tables exceptions
class ExtraDataFileReadError(ErrorBuildCoreData):
    """Raised when a mandatory data file cannot be read."""
    def __init__(self, label: str, file: str, original_exception: Exception):
        self.label = label
        self.file = file
        self.original_exception = original_exception
        super().__init__(
            f"Failed to read a mandatory file '{label}' at '{file}': "
            f"{type(original_exception).__name__}: {original_exception}"
        )

class ExtraDataFileReadWarning(WarningBuildCoreData):
    """Raised when an extra data file cannot be read and is skipped."""
    def __init__(self, label: str, file: str, original_exception: Exception):
        self.label = label
        self.file = file
        self.original_exception = original_exception
        super().__init__(
            f"Failed to read an optional extra file '{label}' at '{file}': "
            f"{type(original_exception).__name__}: {original_exception}"
        )


# validate_entity_first_column.py exceptions
class EntityColumnError(ErrorBuildCoreData):
    """Raised when the entity_column is not the first column in either data table."""


class EntityUniquenessError(ErrorBuildCoreData):
    """Raised when entities are not unique."""
