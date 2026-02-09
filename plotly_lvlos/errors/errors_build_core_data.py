import warnings

from plotly_lvlos.core_data.DataFileInfo import DataFileInfo

# base classes
class TableValidationFailure(Exception):
    """Base class for all table-related validation failures."""

    def warn(self):
        warnings.warn(str(self))

class MatchesTableBuildingFailure(Exception):
    def warn(self):
        warnings.warn(str(self))


# specific failure classes
class FileReadFailure(TableValidationFailure):
    def __init__(self, table: DataFileInfo, original_exception: Exception | None = None):
        self.label = table.label
        self.file = table.file
        self.original_exception = original_exception
        super().__init__(
            f"Failed to read file '{self.file}' for table '{self.label}': {original_exception}"
        )

class EntityColumnFailure(TableValidationFailure):
    def __init__(self, failure_text: str):
        super().__init__(failure_text)


class EntityUniquenessFailure(TableValidationFailure):
    def __init__(self, failure_text: str):
        super().__init__(failure_text)


class OverlapColumnsFailure(TableValidationFailure):
    def __init__(self, failure_text: str):
        super().__init__(failure_text)


class Data_xValuePositivenessFailure(TableValidationFailure):
    def __init__(self, failure_text: str):
        super().__init__(failure_text)
