from fastapi import APIRouter

from traceforge.services.readers_factory import get_trace_reader

# from traceforge.services.db_reader import SQLiteTraceReader
# reader = SQLiteTraceReader()

router = APIRouter()

reader = get_trace_reader()


@router.get("/traces")
async def get_all_traces():
    return await reader.get_all_traces()
