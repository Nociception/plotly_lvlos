from functools import wraps

import polars as pl

from plotly_lvlos.errors.errors_build_core_data import (
    FileReadFailure,
    EntityColumnFailure,
    EntityUniquenessFailure,
    OverlapColumnsFailure,
    Data_xValuePositivenessFailure,
)


def all_tables_decorator(func):
    @wraps(func)
    def wrapper(self):
        for table_name in self.tables:
            table = self.tables[table_name]

            if not table.status:
                continue

            try:
                func(self, table)

            except (
                FileReadFailure,
                EntityColumnFailure,
                EntityUniquenessFailure,
                OverlapColumnsFailure,
                Data_xValuePositivenessFailure,
            ) as e:
                table.status = False
                if table.mandatory:
                    raise
                else:
                    e.warn()

            except pl.exceptions.PolarsError as e:
                failure = FileReadFailure(table=table, original_exception=e)
                table.status = False
                if table.mandatory:
                    raise failure
                else:
                    failure.warn()

    return wrapper
