from pathlib import Path
import warnings

# from plotly_lvlos.config.config_toml_dict_schema import (
#     CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS,
# )
from plotly_lvlos.errors.errors_config import (
    ConfigFileNotFoundFatalError,
    ConfigFileNotFoundWarning,
)


def validate_file_exists(file_path, mandatory: bool = True):
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
    return True


def validate_config_values(dico):
    pass
