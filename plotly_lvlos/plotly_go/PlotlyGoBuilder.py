import duckdb
import plotly.graph_objects as go
import numpy as np

from .analytics import build_analytics
from .frames import build_plotly_frames
from .html.html_builder import build_html


class PlotlyGoBuilder:
    def __init__(self, con: duckdb.DuckDBPyConnection, config_dict: dict) -> None:
        self.con = con
        self.config_dict = config_dict
        self.overlap_column_label = self.config_dict["data"]["overlap_column"]
        self.entity_column_label = self.config_dict["data"]["entity_column"]
        self.frames: list[go.Frame] = []
        self.analytics_years: np.ndarray = np.array([])
        self.analytics: dict[str, dict[str, np.ndarray]] = {}

    def build(self) -> None:
        build_analytics(self)
        build_plotly_frames(self)
        build_html(self)