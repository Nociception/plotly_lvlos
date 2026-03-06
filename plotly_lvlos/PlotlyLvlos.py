from pathlib import Path

import duckdb
import plotly.graph_objects as go
import polars as pl
import numpy as np

from plotly_lvlos.core_data.CoreDataBuilder import CoreDataBuilder


class PlotlyLvlos:
    def __init__(self, config_dict: dict) -> None:
        self.config_dict = config_dict
        self.con = duckdb.connect("core_data.duckdb")
        self.frames: list[go.Frame]
        self.html_path: str | None = None
        self.core_data_table_label = "core_data"

    def build_core_data_table(self) -> None:
        # if not Path("core_data.csv").resolve().exists():
            core_data_builder = CoreDataBuilder(
                con=self.con,
                config_dict=self.config_dict,
                core_data_table_label=self.core_data_table_label,
            )
            core_data_builder.build()




    # def build_analytical_table(self)




    def build_plotly_frames(self) -> None:

        df: pl.DataFrame = pl.from_arrow(
            self.con.execute("SELECT * FROM core_data").fetch_arrow_table()
        )  # type: ignore
        years = df.select("year").unique().sort("year")["year"].to_list()
        frames: list[go.Frame] = []
        max_val = df["extra_data_point"].max()
        sizeref = 2 * np.sqrt(max_val) / (60 ** 2)  # type: ignore

        for year in years:
            frame_df = df.filter(pl.col("year") == year)
            sizes = np.maximum(np.sqrt(frame_df["extra_data_point"].to_numpy()), 3)
            frame = go.Frame(
                data=[
                    go.Scatter(
                        x=frame_df["data_x_log"],
                        y=frame_df["data_y"],
                        mode="markers",
                        marker=dict(
                            size=sizes,
                            sizeref=sizeref,
                            sizemode="area",
                        ),
                        text=frame_df["country"],
                        ids=frame_df["country"],
                    )
                ],
                name=str(year),
            )
            frames.append(frame)

        self.frames = frames




    def build_html(self) -> None:
        first_frame = self.frames[0]

        fig = go.Figure(
            data=first_frame.data,
            frames=self.frames,
        )

        fig.update_layout(
            xaxis_title="data_x_log",
            yaxis_title="data_y",
            sliders=[
                {
                    "steps": [
                        {
                            "method": "animate",
                            "args": [
                                [frame.name],
                                {"mode": "immediate"},
                            ],
                            "label": frame.name,
                        }
                        for frame in self.frames
                    ]
                }
            ]
        )
        self.html_path = "plotly_lvlos.html"
        fig.write_html(self.html_path)


    def close_connection(self) -> None:
        self.con.close()
