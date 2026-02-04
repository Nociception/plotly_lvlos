from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataFileInfo:
    label: str
    file: Path
    mandatory: bool
    file_profile: str
    overlap_columns_sql: str
    status: bool = True
