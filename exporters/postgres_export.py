import asyncio
import json
from typing import Optional

import asyncpg

from traceforge.exporters.base import BaseExporter

# pip install asyncpg


class PostgresAsyncExporter(BaseExporter):
    def __init__(self, db_url: str):
        """
        db_url example:
        postgresql://user:password@localhost:5432/traceforge
        """
        self.db_url = db_url
        self._pool: Optional[asyncpg.Pool] = None

    async def _init_pool(self):
        if not self._pool:
            self._pool = await asyncpg.create_pool(self.db_url)
            await self._init_schema()

    async def _init_schema(self):
        async with self._pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    project TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    metadata JSONB
                );
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS spans (
                    span_id TEXT PRIMARY KEY,
                    trace_id TEXT REFERENCES traces(trace_id) ON DELETE CASCADE,
                    parent_id TEXT,
                    name TEXT,
                    span_type TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    metadata JSONB,
                    inputs JSONB,
                    outputs JSONB
                );
            """)

    async def _export_async(self, trace_dict: dict):
        await self._init_pool()

        async with self._pool.acquire() as conn:
            async with conn.transaction():
                # Insert trace
                await conn.execute(
                    """
                    INSERT INTO traces (trace_id, project, start_time, end_time, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (trace_id) DO NOTHING;
                """,
                    trace_dict["trace_id"],
                    trace_dict.get("project"),
                    trace_dict.get("start_time"),
                    trace_dict.get("end_time"),
                    json.dumps(trace_dict.get("metadata", {})),
                )

                # Insert spans
                for span in trace_dict.get("spans", []):
                    await self._insert_span(conn, trace_dict["trace_id"], span)

    async def _insert_span(self, conn, trace_id, span, parent_id=None):
        await conn.execute(
            """
            INSERT INTO spans (
                span_id, trace_id, parent_id, name,
                span_type, start_time, end_time,
                metadata, inputs, outputs
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10)
            ON CONFLICT (span_id) DO NOTHING;
        """,
            span["span_id"],
            trace_id,
            parent_id,
            span.get("name"),
            span.get("span_type"),
            span.get("start_time"),
            span.get("end_time"),
            json.dumps(span.get("metadata", {})),
            json.dumps(span.get("inputs", {})),
            json.dumps(span.get("outputs", {})),
        )

        for child in span.get("children", []):
            await self._insert_span(conn, trace_id, child, span["span_id"])

    def export(self, trace_dict: dict):
        """
        Safe universal export:
        - Works in script mode
        - Works in FastAPI
        """

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self._export_async(trace_dict))
            return

        asyncio.create_task(self._export_async(trace_dict))
