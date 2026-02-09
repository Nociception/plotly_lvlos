from dataclasses import dataclass
from pathlib import Path

import polars as pl


@dataclass
class DataFileInfo:
    label: str
    file: Path
    mandatory: bool
    file_profile: str
    overlap_columns_sql: str
    suffixes: dict | None
    df: pl.DataFrame | None = None
    overlap_columns: list[str] | None = None
    status: bool = True


def _create_DataFileInfo_objects(config_dict: dict) -> dict[str, DataFileInfo]:

    config_data = config_dict["data"]
    suffixes_dict = config_dict["suffixes"]

    return {
        "data_x": DataFileInfo(
            label="data_x",
            file=Path(config_data["x_file"]),
            mandatory=True,
            file_profile=config_data["x_file_profile"],
            overlap_columns_sql="",
            suffixes=suffixes_dict.get("data_x"),
        ),
        "data_y": DataFileInfo(
            label="data_y",
            file=Path(config_data["y_file"]),
            mandatory=True,
            file_profile=config_data["y_file_profile"],
            overlap_columns_sql="",
            suffixes=suffixes_dict.get("data_y"),
        ),
        "extra_data_point": DataFileInfo(
            label="extra_data_point",
            file=Path(config_data["extra_data_point_file"]),
            mandatory=False,
            file_profile=config_data["extra_data_point_file_profile"],
            overlap_columns_sql="",
            suffixes=suffixes_dict.get("extra_data_point"),
        ),
        "extra_data_x": DataFileInfo(
            label="extra_data_x",
            file=Path(config_data["extra_data_x_file"]),
            mandatory=False,
            file_profile=config_data["extra_data_x_file_profile"],
            overlap_columns_sql="",
            suffixes=suffixes_dict.get("extra_data_x"),
        ),
    }
