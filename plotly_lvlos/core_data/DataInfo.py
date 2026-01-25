from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataInfo:
    label: str
    file: Path
    mandatory: bool
    file_profile: str
    status: bool = True
