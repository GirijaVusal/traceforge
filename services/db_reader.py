import json
import sqlite3
from pathlib import Path

import aiosqlite


class SQLiteTraceReader:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)

    async def get_all_traces(self):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            try:
                traces_rows = await db.execute_fetchall("SELECT * FROM traces")
                spans_rows = await db.execute_fetchall("SELECT * FROM spans")
            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    return {}
                raise

        # Group spans by trace_id
        spans_by_trace = {}
        for row in spans_rows:
            span = dict(row)
            span["metadata"] = json.loads(span["metadata"] or "{}")
            span["inputs"] = json.loads(span["inputs"] or "{}")
            span["outputs"] = json.loads(span["outputs"] or "{}")
            span["children"] = []

            spans_by_trace.setdefault(span["trace_id"], []).append(span)

        final_traces = []

        for trace_row in traces_rows:
            trace = dict(trace_row)
            trace["metadata"] = json.loads(trace["metadata"] or "{}")

            trace_spans = spans_by_trace.get(trace["trace_id"], [])

            # Build tree structure
            span_map = {s["span_id"]: s for s in trace_spans}
            root_spans = []

            for span in trace_spans:
                parent_id = span["parent_id"]
                if parent_id and parent_id in span_map:
                    span_map[parent_id]["children"].append(span)
                else:
                    root_spans.append(span)

            trace["spans"] = root_spans
            final_traces.append(trace)

        return final_traces
