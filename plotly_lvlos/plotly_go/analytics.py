from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .PlotlyGoBuilder import PlotlyGoBuilder


def build_analytics(builder: PlotlyGoBuilder) -> None:
    builder.con.execute("DROP TABLE IF EXISTS analytics")
    builder.con.execute(f"""
        CREATE TABLE analytics AS

            WITH
                cleaned AS (
                    SELECT
                        {builder.entity_column_label},
                        {builder.overlap_column_label},
                        data_x,
                        data_x_log,
                        data_y
                    FROM core_data
                    WHERE
                        data_x IS NOT NULL
                        AND data_y IS NOT NULL
                ),

                oc_agg AS (
                    SELECT
                        {builder.overlap_column_label},
                        avg(data_y)                         AS avg_y,
                        avg(data_x)                         AS avg_x_lin,
                        avg(data_x_log)                     AS avg_x_log,
                        covar_pop(data_x, data_y)           AS covar_lin,
                        covar_pop(data_x_log, data_y)       AS covar_log,
                        var_pop(data_x)                     AS var_x_lin,
                        var_pop(data_x_log)                 AS var_x_log
                    FROM cleaned
                    GROUP BY {builder.overlap_column_label}
                ),

                ranked AS (
                    SELECT
                        c.{builder.overlap_column_label},
                        c.data_x,
                        c.data_x_log,
                        c.data_y,

                        RANK() OVER (
                            PARTITION BY c.{builder.overlap_column_label}
                            ORDER BY c.data_x
                        ) AS rank_x,
                        RANK() OVER (
                            PARTITION BY c.{builder.overlap_column_label}
                            ORDER BY c.data_y
                        ) AS rank_y,

                        oca.covar_lin / NULLIF(oca.var_x_lin, 0)                               AS slope_lin,
                        oca.avg_y - (oca.covar_lin / NULLIF(oca.var_x_lin, 0)) * oca.avg_x_lin AS intercept_lin,

                        oca.covar_log / NULLIF(oca.var_x_log, 0)                               AS slope_log,
                        oca.avg_y - (oca.covar_log / NULLIF(oca.var_x_log, 0)) * oca.avg_x_log AS intercept_log

                    FROM
                        cleaned AS c
                        JOIN oc_agg AS oca
                            ON oca.{builder.overlap_column_label} = c.{builder.overlap_column_label}
                ),

                lin_scale AS (
                    SELECT
                        {builder.overlap_column_label},
                        'lin'                                                               AS scale,
                        corr(data_x, data_y)                                                AS pearson_r,
                        corr(rank_x, rank_y)                                                AS spearman_rho,
                        avg(slope_lin)                                                      AS ols_slope,
                        avg(intercept_lin)                                                  AS ols_intercept,
                        POWER(corr(data_x, data_y), 2)                                      AS r_squared,
                        SQRT(avg(POWER(data_y - (slope_lin * data_x + intercept_lin), 2)))  AS ols_rmse,
                        COUNT(*)                                                            AS n_entities
                    FROM ranked
                    GROUP BY {builder.overlap_column_label}
                ),

                log_scale AS (
                    SELECT
                        {builder.overlap_column_label},
                        'log'                                                                       AS scale,
                        corr(data_x_log, data_y)                                                    AS pearson_r,
                        corr(rank_x, rank_y)                                                        AS spearman_rho,
                        avg(slope_log)                                                              AS ols_slope,
                        avg(intercept_log)                                                          AS ols_intercept,
                        POWER(corr(data_x_log, data_y), 2)                                          AS r_squared,
                        SQRT(avg(POWER(data_y - (slope_log * data_x_log + intercept_log), 2)))      AS ols_rmse,
                        COUNT(*)                                                                    AS n_entities
                    FROM ranked
                    GROUP BY {builder.overlap_column_label}
                )

            SELECT * FROM lin_scale
            UNION ALL
            SELECT * FROM log_scale
            ORDER BY
                {builder.overlap_column_label},
                scale
    """)