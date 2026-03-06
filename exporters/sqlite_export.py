import asyncio
import json
from pathlib import Path

import aiosqlite

from .base import BaseExporter


class SQLiteAsyncExporter(BaseExporter):
    def __init__(self, db_path: str = "traceforge.db"):
        self.db_path = Path(db_path)
        self._initialized = False
        self._lock = asyncio.Lock()
        self.pending_tasks = set()

    async def _init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    project TEXT,
                    metadata TEXT,
                    start_time TEXT,
                    end_time TEXT
                )
            """)

            await db.execute("""
                CREATE TABLE IF NOT EXISTS spans (
                    span_id TEXT PRIMARY KEY,
                    trace_id TEXT,
                    parent_id TEXT,
                    name TEXT,
                    type TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_ms REAL,
                    inputs TEXT,
                    outputs TEXT,
                    error TEXT,
                    metadata TEXT
                )
            """)

            await db.commit()

        self._initialized = True

    async def _export_async(self, trace_dict: dict):
        if not self._initialized:
            await self._init_db()

        async with self._lock:
            async with aiosqlite.connect(self.db_path) as db:
                # Insert trace
                await db.execute(
                    """
                    INSERT INTO traces (
                        trace_id, project, metadata, start_time, end_time
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        trace_dict["trace_id"],
                        trace_dict["project"],
                        json.dumps(trace_dict.get("metadata", {})),
                        trace_dict["start_time"],
                        trace_dict["end_time"],
                    ),
                )

                # Insert spans
                for span in trace_dict.get("spans", []):
                    await self._insert_span(db, span)

                await db.commit()

    async def _insert_span(self, db, span: dict):
        await db.execute(
            """
            INSERT INTO spans (
                span_id, trace_id, parent_id, name, type,
                start_time, end_time, duration_ms,
                inputs, outputs, error, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                span["span_id"],
                span["trace_id"],
                span["parent_id"],
                span["name"],
                span["type"],
                span["start_time"],
                span["end_time"],
                span["duration_ms"],
                json.dumps(span.get("inputs", {})),
                json.dumps(
                    span.get("outputs", {})
                ),  # ← your standardized format stored here
                span.get("error"),
                json.dumps(span.get("metadata", {})),
            ),
        )

        # Recursively store children flattened
        for child in span.get("children", []):
            await self._insert_span(db, child)

    def export(self, trace_dict: dict):
        """
        Sync-compatible wrapper.
        Works inside FastAPI OR normal script.
        """
        # try:
        #     loop = asyncio.get_running_loop()
        #     loop.create_task(self._export_async(trace_dict))
        # except RuntimeError:
        #     asyncio.run(self._export_async(trace_dict))

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No loop running → script mode
            asyncio.run(self._export_async(trace_dict))
            return

        # If we're here, a loop is running (FastAPI case)
        # We MUST schedule and NOT close loop
        task = asyncio.create_task(self._export_async(trace_dict))
        # Add to tracking set so flush() can find it
        self.pending_tasks.add(task)
        # Remove from set automatically when done to prevent memory leaks
        task.add_done_callback(self.pending_tasks.discard)

    async def flush(self):
        """Wait for all currently backgrounded tasks to finish."""
        if self.pending_tasks:
            await asyncio.gather(*self.pending_tasks, return_exceptions=True)
