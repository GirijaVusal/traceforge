# from traceforge.exporters.postgres_export import PostgresAsyncExporter
from traceforge.config import resolve_db_url
from traceforge.exporters.sqlite_export import SQLiteAsyncExporter


def trace_exporter():
    db_url = resolve_db_url()

    # if db_url.startswith("postgres"):
    #     return PostgresAsyncExporter(db_url)

    if db_url.startswith("sqlite"):
        path = db_url.replace("sqlite:///", "")
        return SQLiteAsyncExporter(path)

    raise ValueError("Unsupported DB URL")
