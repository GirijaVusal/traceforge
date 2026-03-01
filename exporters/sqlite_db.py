# traceforge/exporters/sqlite_db.py

import asyncio
from typing import List

import aiosqlite
from traceforge.core.models import Span, Trace


class SQLiteExporter:
    def __init__(self, db_path: str = "traceforge.db"):
        self.db_path = db_path
        self._initialized = False

    async def _initialize(self):
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    project TEXT,
                    metadata TEXT,
                    start_time REAL,
                    end_time REAL
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS spans (
                    span_id TEXT PRIMARY KEY,
                    trace_id TEXT,
                    parent_id TEXT,
                    name TEXT,
                    span_type TEXT,
                    start_time REAL,
                    end_time REAL,
                    duration_ms REAL,
                    inputs TEXT,
                    outputs TEXT,
                    error TEXT,
                    metadata TEXT
                )
            """)

            await conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_spans_trace_id ON spans(trace_id)"
            )

            await conn.commit()

        self._initialized = True

    def export_trace(self, trace: Trace):
        asyncio.run(self._export_trace_async(trace))

    async def _export_trace_async(self, trace: Trace):
        if not self._initialized:
            await self._initialize()

        async with aiosqlite.connect(self.db_path) as conn:
            # Insert trace
            await conn.execute(
                """
                INSERT OR REPLACE INTO traces
                (trace_id, project, metadata, start_time, end_time)
                VALUES (?, ?, ?, ?, ?)
                """,
                trace.to_db_tuple(),
            )

            # Flatten spans
            spans: List[Span] = []

            def collect(span: Span):
                spans.append(span)
                for child in span.children:
                    collect(child)

            for root_span in trace.spans:
                collect(root_span)

            if spans:
                await conn.executemany(
                    """
                    INSERT OR REPLACE INTO spans
                    (span_id, trace_id, parent_id, name, span_type,
                     start_time, end_time, duration_ms,
                     inputs, outputs, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [s.to_db_tuple() for s in spans],
                )

            await conn.commit()
