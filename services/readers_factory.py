from urllib.parse import urlparse

from traceforge.config import resolve_db_url

from .db_reader import SQLiteTraceReader


# TODO need to implement for postrgsql
def get_trace_reader():
    db_url = resolve_db_url()

    if db_url.startswith("sqlite"):
        path = urlparse(db_url).path
        return SQLiteTraceReader(path)

    raise ValueError(f"Unsupported DB URL: {db_url}")
