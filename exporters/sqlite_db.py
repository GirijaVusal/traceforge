# import asyncio
# import json
# from pathlib import Path

# import aiosqlite

# from .base import BaseExporter


# class SQLiteExporter(BaseExporter):
#     def __init__(self, db_path="traceforge.db"):
#         self.db_path = str(Path(db_path).resolve())
#         # Automatically initialize DB tables upon startup
#         try:
#             loop = asyncio.get_running_loop()
#             loop.create_task(self._init_db())
#         except RuntimeError:
#             # Fallback if initialized outside of an async event loop
#             asyncio.run(self._init_db())

#     async def _init_db(self):
#         """Creates the necessary tables if they don't exist."""
#         async with aiosqlite.connect(self.db_path) as db:
#             await db.execute("""
#                 CREATE TABLE IF NOT EXISTS traces (
#                     trace_id TEXT PRIMARY KEY,
#                     project TEXT,
#                     session_id TEXT,
#                     start_time TEXT,
#                     end_time TEXT,
#                     metadata TEXT,
#                     spans TEXT
#                 )
#             """)
#             await db.commit()

#     def export(self, trace_dict: dict):
#         """
#         Sync interface bridging to async.
#         Fires off the DB insert into the background without blocking the main thread.
#         """
#         try:
#             loop = asyncio.get_running_loop()
#             loop.create_task(self._async_export(trace_dict))
#         except RuntimeError:
#             asyncio.run(self._async_export(trace_dict))

#     async def _async_export(self, trace_dict: dict):
#         """Handles the actual async database insertion."""
#         # Stringify nested JSON objects for SQLite storage
#         metadata_json = json.dumps(trace_dict.get("metadata", {}))
#         spans_json = json.dumps(trace_dict.get("spans", []))
#         session_id = trace_dict.get("metadata", {}).get("session_id", "unknown")

#         async with aiosqlite.connect(self.db_path) as db:
#             await db.execute(
#                 """
#                 INSERT INTO traces (trace_id, project, session_id, start_time, end_time, metadata, spans)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """,
#                 (
#                     trace_dict["trace_id"],
#                     trace_dict["project"],
#                     session_id,
#                     trace_dict["start_time"],
#                     trace_dict["end_time"],
#                     metadata_json,
#                     spans_json,
#                 ),
#             )
#             await db.commit()

import json
from pathlib import Path

import aiosqlite

from .base import BaseExporter


class AsyncSQLiteExporter(BaseExporter):
    def __init__(self, db_path="traceforge.db"):
        self.db_path = Path(db_path)

    async def _init_db(self, db):
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

    async def export(self, trace_dict: dict):
        async with aiosqlite.connect(self.db_path) as db:
            await self._init_db(db)

            await db.execute(
                """
                INSERT OR REPLACE INTO traces VALUES (?, ?, ?, ?, ?)
            """,
                (
                    trace_dict["trace_id"],
                    trace_dict["project"],
                    json.dumps(trace_dict["metadata"]),
                    trace_dict["start_time"],
                    trace_dict["end_time"],
                ),
            )

            async def insert_span(span):
                await db.execute(
                    """
                    INSERT OR REPLACE INTO spans VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                        json.dumps(span["inputs"]),
                        json.dumps(span["outputs"]),
                        span["error"],
                        json.dumps(span["metadata"]),
                    ),
                )

                for child in span.get("children", []):
                    await insert_span(child)

            for span in trace_dict["spans"]:
                await insert_span(span)

            await db.commit()
