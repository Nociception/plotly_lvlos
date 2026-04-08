from pathlib import Path


def _label_from_path(filepath: str) -> str:
    return Path(filepath).stem.replace("_", " ").capitalize()


def _extract_labels(config_dict: dict) -> dict[str, str]:
    data = config_dict["data"]
    return {
        "entity": data["entity_column"],
        "overlap": data["overlap_column"],
        "data_x": _label_from_path(data["x_file"]),
        "data_y": _label_from_path(data["y_file"]),
        "extra_data_point": _label_from_path(data["extra_data_point_file"]),
        "extra_data_x": _label_from_path(data["extra_data_x_file"]),
    }
