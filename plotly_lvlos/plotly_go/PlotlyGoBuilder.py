import duckdb
import plotly.graph_objects as go
import numpy as np
import polars as pl
from plotly.subplots import make_subplots


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
                data_x,
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
                ) AS size,
                extra_data_x
            FROM
                core_data
            ORDER BY
                overlap_value,
                {self.entity_column_label}
        """).fetch_arrow_table())  # type: ignore

        sizeref: float = (
            2 * df["size"].max()  # type: ignore
            / (self.config_dict["visualization"]["max_marker_size"] ** 2)
        )

        x_lin: np.ndarray = df["data_x"].to_numpy()
        x_log: np.ndarray = df["data_x_log"].to_numpy()
        y: np.ndarray = df["data_y_plot"].to_numpy()
        size: np.ndarray = df["size"].to_numpy()
        opacity: np.ndarray = df["opacity"].to_numpy()
        entity: list[str] = df["entity"].to_list()
        year: np.ndarray = df["overlap_value"].to_numpy()

        start: int = 0
        for frame_df in df.partition_by("overlap_value", maintain_order=True):
            n: int = frame_df.height
            end: int = start + n
            frame: go.Frame = go.Frame(
                data=[
                    go.Scatter(
                        x=x_lin[start:end],
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
                    ),
                    go.Scatter(
                        x=x_log[start:end],
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
                    ),
                ],
                name=str(year[start]),
            )
            self.frames.append(frame)
            start = end


    def build_html(self) -> None:

        fig = make_subplots(
            rows=6,
            cols=4,
            specs=[

                [{"rowspan": 3, "colspan": 3}, None, None, {"rowspan": 2}],
                [None, None, None, None],
                [None, None, None, {"rowspan": 2}],
                [{"rowspan": 3, "colspan": 3}, None, None, None],
                [None, None, None, {"rowspan": 2}],
                [None, None, None, None],
            ],
            column_widths=[0.25, 0.25, 0.25, 0.25],
            horizontal_spacing=0.06,
            vertical_spacing=0.08,
        )

        first_frame = self.frames[0]

        fig.add_trace(first_frame.data[0], row=1, col=1)  # type: ignore
        fig.add_trace(first_frame.data[1], row=4, col=1)  # type: ignore
        fig.add_trace(go.Scatter(mode="lines", name="corr_log"), row=1, col=4)
        fig.add_trace(go.Scatter(mode="lines", name="corr_diff"), row=3, col=4)
        fig.add_trace(go.Scatter(mode="lines", name="corr_lin"), row=5, col=4)

        fig.frames = self.frames

        slider_steps = [
            dict(
                method="animate",
                label=frame.name,
                args=[
                    [frame.name],
                    dict(
                        mode="immediate",
                        frame=dict(duration=80, redraw=True),
                        transition=dict(duration=0),
                    ),
                ],
            )
            for frame in self.frames
        ]

        fig.update_layout(
            sliders=[dict(active=0, steps=slider_steps)],
        )

        fig.write_html("plotly_lvlos.html", auto_play=True)
