"""
Build entry point for plotly-lvlos.

This module orchestrates the full build pipeline:
- load configuration (through
    load_config, and the following tests :
    parse_config_toml_dict,
    validate_config_values,
    validate_files_exist
)
- (future) load data
- (future) generate Plotly HTML output
"""

from plotly_lvlos.config.load_config import load_config
from pathlib import Path

from typeguard import typechecked


@typechecked
def build(config_path: str) -> None:
    """
    """
    config_dict = load_config(Path(config_path))

    # build_core_data_table()
    # optionnal_data_enrichment()
    # build_analytical_table
    # build_plotly_frames()
    # build_html()


    if config_dict:
        for key, value in config_dict.items():
            print(f"{key}: {value}")
    else:
        print("No configuration loaded.")


if __name__ == "__main__":
    build("config.toml")
