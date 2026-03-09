import duckdb
import plotly.graph_objects as go
import numpy as np
import polars as pl


class PlotlyGoBuilder:
    def __init__(self, con: duckdb.DuckDBPyConnection, config_dict: dict) -> None:
        self.con = con
        self.config_dict = config_dict
        self.overlap_column_label = self.config_dict["data"]["overlap_column"]
        self.entity_column_label = self.config_dict["data"]["entity_column"]
        self.frames: list[go.Frame] = []

    def build(self) -> None:
        self.build_plotly_frames()
        self.build_html()

    def build_plotly_frames(self) -> None:

        arrow_table: pl.DataFrame = self.con.execute(f"""
            SELECT
                {self.entity_column_label},
                {self.overlap_column_label} AS overlap_value,
                data_x_log,
                data_y,
                extra_data_point
            FROM
                core_data
            ORDER BY
                overlap_value,
                {self.entity_column_label}
        """).fetch_arrow_table()
        df: pl.DataFrame = pl.from_arrow(arrow_table)  # type: ignore

        sizeref: float = (
            2 * np.sqrt(df["extra_data_point"].max())  # type: ignore
            / (self.config_dict["visualization"]["max_marker_size"] ** 2)
        )

        df: pl.DataFrame = df.with_columns(
            pl.col("extra_data_point")
            .sqrt()
            .clip(self.config_dict["visualization"]["min_marker_size"])
            .alias("size")
        )
        for frame_df in df.partition_by("overlap_value", maintain_order=True):
            overlap_value = frame_df["overlap_value"][0]
            frame = go.Frame(
                data=[
                    go.Scatter(
                        x=frame_df["data_x_log"].to_numpy(),
                        y=frame_df["data_y"].to_numpy(),
                        mode="markers",
                        marker=dict(
                            size=frame_df["size"].to_numpy(),
                            sizeref=sizeref,
                            sizemode="area",
                        ),
                        text=frame_df["country"].to_list(),
                        ids=frame_df["country"].to_list(),
                    )
                ],
                name=str(overlap_value),
            )
            self.frames.append(frame)


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
            ],
        )
        html_path = "plotly_lvlos.html"
        fig.write_html(html_path)
