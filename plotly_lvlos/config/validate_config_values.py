from pathlib import Path
import warnings

from plotly_lvlos.config.config_toml_dict_schema import (
    CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
)
from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFoundFatalError,
    ConfigFileNotFoundWarning,
    ConfigConstraintError,
)


def _validate_file_exists(file_path: str, mandatory: bool = True) -> None:
    """
    Check whether a file exists and raise or warn accordingly.

    Parameters
    ----------
    file_path : str or Path
        Path to the file to check.
    mandatory : bool, default=True
        Whether the file is mandatory. If True, absence raises an error.
        If False, absence emits a warning.

    Raises
    ------
    ConfigFileNotFoundFatalError
        If the file is mandatory and does not exist.

    Warns
    -----
    ConfigFileNotFoundWarning
        If the file is optional and does not exist.
    """
    path: Path = Path(file_path)
    if not path.exists():
        if mandatory:
            raise ConfigFileNotFoundFatalError(
                f"Mandatory config file not found: {file_path}"
            )
        else:
            warnings.warn(
                f"Optional config file not found: {file_path}",
                ConfigFileNotFoundWarning,
            )


def validate_files_exist(config_dict: dict) -> None:
    """
    Validate the existence of data files referenced in the configuration.

    Mandatory files are checked strictly and raise errors if missing.
    Optional files emit warnings if missing.

    Parameters
    ----------
    config_dict : dict
        Fully parsed configuration dictionary.

    Raises
    ------
    ConfigFileNotFoundFatalError
        If a mandatory data file does not exist.
    """
    data_section = config_dict.get("data", {})
    if data_section:
        x_file: str = data_section.get("x_file")
        y_file: str = data_section.get("y_file")
        extra_data_point_file: str = data_section.get("extra_data_point_file")
        extra_data_x_file: str = data_section.get("extra_data_x_file")

        _validate_file_exists(x_file, mandatory=True)
        _validate_file_exists(y_file, mandatory=True)

        if extra_data_point_file:
            _validate_file_exists(extra_data_point_file, mandatory=False)

        if extra_data_x_file:
            _validate_file_exists(extra_data_x_file, mandatory=False)


def validate_config_values(config_dict: dict) -> None:
    """
    Validate configuration values against declared constraints.

    Constraints are defined in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS and include:
    - type checking
    - string length bounds
    - numeric min/max bounds
    - optional string stripping before validation

    Parameters
    ----------
    config_dict : dict
        Fully parsed configuration dictionary.

    Raises
    ------
    ConfigConstraintError
        If any configuration value violates its declared constraints.
    """
    for section, keys in CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS.items():
        section_dict = config_dict[section]

        for key, constraints in keys.items():
            value = section_dict[key]
            expected_type = constraints["type"]

            if expected_type is str:
                if constraints.get("strip"):
                    value = value.strip()

                length = len(value)
                len_min = constraints.get("len_min", 0)
                len_max = constraints.get("len_max", float("inf"))

                if "len_min" in constraints and length < len_min:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

                if "len_max" in constraints and length > len_max:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

            elif expected_type is int:
                if "min" in constraints and value < constraints["min"]:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )

                if "max" in constraints and value > constraints["max"]:
                    raise ConfigConstraintError(
                        section=section,
                        key=key,
                        value=value,
                        constraints=constraints,
                    )
