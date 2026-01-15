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


def _validate_file_exists(file_path, mandatory: bool = True):
    path = Path(file_path)
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


def validate_files_exist(config_dict):
    data_section = config_dict.get("data", {})
    if data_section:
        x_file = data_section.get("x_file")
        y_file = data_section.get("y_file")
        extra_data_point_file = data_section.get("extra_data_point_file")
        extra_data_x_file = data_section.get("extra_data_x_file")

        _validate_file_exists(x_file, mandatory=True)
        _validate_file_exists(y_file, mandatory=True)

        if extra_data_point_file:
            _validate_file_exists(extra_data_point_file, mandatory=False)

        if extra_data_x_file:
            _validate_file_exists(extra_data_x_file, mandatory=False)


def validate_config_values(config_dict):
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
