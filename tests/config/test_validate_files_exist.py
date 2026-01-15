import pytest
import copy

from plotly_lvlos.config.validate_files_exist import _validate_file_exists
from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFoundFatalError,
    ConfigFileNotFoundWarning,
)


@pytest.mark.parametrize("file_key", ["x_file", "y_file"])
def test_mandatory_data_file_missing_raises(
    valid_config_dict: dict, file_key: str
) -> None:
    """Check that missing mandatory data files raise a fatal error."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

    test_dict["data"][file_key] = "nonexistent_file.csv"

    with pytest.raises(ConfigFileNotFoundFatalError):
        _validate_file_exists(test_dict["data"][file_key], mandatory=True)


@pytest.mark.parametrize("file_key", ["extra_data_point_file", "extra_data_x_file"])
def test_optional_data_file_missing_warns(
    valid_config_dict: dict, file_key: str
) -> None:
    """Check that missing optional data files trigger a warning."""
    test_dict: dict = copy.deepcopy(valid_config_dict)

    test_dict["data"][file_key] = "nonexistent_file.csv"

    with pytest.warns(ConfigFileNotFoundWarning):
        _validate_file_exists(test_dict["data"][file_key], mandatory=False)
