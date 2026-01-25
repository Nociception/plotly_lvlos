from dataclasses import dataclass
from pathlib import Path


@dataclass
class DataInfo:
    label: str
    file: Path
    mandatory: bool
    status: bool = True
