import warnings

from plotly_lvlos.core_data.DataInfo import DataInfo


# Base exception/waring
class TableValidationFailure(Exception):
    """Base class for all table-related validation failures."""

    def warn(self):
        warnings.warn(str(self))


# load_core_raw_tables exceptions
class FileReadFailure(TableValidationFailure):
    def __init__(self, table: DataInfo, original_exception: Exception):
        self.label = table.label
        self.file = table.file
        self.original_exception = original_exception
        super().__init__(
            f"Failed to read file '{self.file}' for table '{self.label}': {original_exception}"
        )


# # validate_entity_first_column.py exceptions
# class EntityColumnError(ErrorBuildCoreData):
#     """Raised when the entity_column is not the first column in either mandatory data table."""
#     def __init__(self, fail_text: str):
#         self.fail_text = fail_text
#         super().__init__(fail_text)

# class EntityColumnWarning(WarningBuildCoreData):
#     """Launched when the entity_column is not the first column in either optionnal data table."""
#     def __init__(self, fail_text: str):
#         self.fail_text = fail_text
#         super().__init__(fail_text)

# class EntityUniquenessError(ErrorBuildCoreData):
#     """Raised when entities are not unique in a mandatory table."""

# class EntityUniquenessWarning(WarningBuildCoreData):
#     """Launched when entities are not unique in an optionnal table ."""
