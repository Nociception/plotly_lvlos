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

        df: pl.DataFrame = pl.from_arrow(self.con.execute(f"""
            SELECT
                {self.entity_column_label} AS entity,
                {self.overlap_column_label} AS overlap_value,
                data_x_log,
                COALESCE(
                    LAST_VALUE(data_y IGNORE NULLS)
                        OVER (
                            PARTITION BY
                                {self.entity_column_label}
                            ORDER BY
                                {self.overlap_column_label}
                            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                    ),
                    FIRST_VALUE(data_y IGNORE NULLS)
                        OVER (
                            PARTITION BY
                                {self.entity_column_label}
                            ORDER BY
                                {self.overlap_column_label}
                            ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING
                    )
                ) AS data_y_plot,
                CAST(
                    CASE
                        WHEN data_y IS NULL THEN 0
                        ELSE 1
                    END
                AS DOUBLE) AS opacity,
                extra_data_point,
                GREATEST(
                    SQRT(extra_data_point),
                    {self.config_dict["visualization"]["min_marker_size"]}
                ) AS size
            FROM
                core_data
            ORDER BY
                overlap_value,
                {self.entity_column_label}
        """).fetch_arrow_table())  # type: ignore

        sizeref: float = (
            2 * df["size"].max()
            / (self.config_dict["visualization"]["max_marker_size"] ** 2)
        )

        x: np.ndarray = df["data_x_log"].to_numpy()
        y: np.ndarray = df["data_y_plot"].to_numpy()
        size: np.ndarray = df["size"].to_numpy()
        opacity: np.ndarray = df["opacity"].to_numpy()
        entity: list[str] = df["entity"].to_list()
        year: np.ndarray = df["overlap_value"].to_numpy()

        frames: list[pl.DataFrame] = df.partition_by("overlap_value", maintain_order=True)
        start: int = 0
        for frame_df in frames:
            n: int = frame_df.height
            end: int = start + n
            frame: go.Frame = go.Frame(
                data=[
                    go.Scatter(
                        x=x[start:end],
                        y=y[start:end],
                        mode="markers",
                        marker=dict(
                            size=size[start:end],
                            opacity=opacity[start:end] * 0.8,
                            sizeref=sizeref,
                            sizemode="area",
                        ),
                        text=entity[start:end],
                        ids=entity[start:end],
                    )
                ],
                name=str(year[start]),
            )
            self.frames.append(frame)
            start = end


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
