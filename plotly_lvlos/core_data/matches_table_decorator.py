from functools import wraps

from plotly_lvlos.errors.errors_build_core_data import (
    FileReadFailure,
    EntityColumnFailure,
    EntityUniquenessFailure,
    OverlapColumnsFailure,
)


def matches_table_decorator(func):
    @wraps(func)
    def wrapper(self):
        for table in self.tables:
            table = self.tables[table]
            if not table.status:
                continue
            try:
                func(self, table)
            except (
                FileReadFailure,
                EntityColumnFailure,
                EntityUniquenessFailure,
                OverlapColumnsFailure,
            ) as e:
                table.status = False
                if table.mandatory:
                    raise e
                else:
                    e.warn()

    return wrapper
