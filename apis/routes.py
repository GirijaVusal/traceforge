# traceforge/apis/routes.py

import aiosqlite
from fastapi import APIRouter

router = APIRouter()

DB_PATH = "traceforge.db"


@router.get("/traces")
async def get_traces(limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT trace_id, project, metadata, start_time, end_time
            FROM traces
            ORDER BY start_time DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = await cursor.fetchall()

        return [
            {
                "trace_id": r[0],
                "project": r[1],
                "metadata": r[2],
                "start_time": r[3],
                "end_time": r[4],
            }
            for r in rows
        ]


@router.get("/spans/{trace_id}")
async def get_spans(trace_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """
            SELECT span_id, parent_id, name, span_type,
                   start_time, end_time, duration_ms,
                   inputs, outputs, error, metadata
            FROM spans
            WHERE trace_id = ?
            ORDER BY start_time ASC
            """,
            (trace_id,),
        )

        rows = await cursor.fetchall()

        return [
            {
                "span_id": r[0],
                "parent_id": r[1],
                "name": r[2],
                "span_type": r[3],
                "start_time": r[4],
                "end_time": r[5],
                "duration_ms": r[6],
                "inputs": r[7],
                "outputs": r[8],
                "error": r[9],
                "metadata": r[10],
            }
            for r in rows
        ]
