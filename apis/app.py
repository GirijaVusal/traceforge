# traceforge/apis/app.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes import router

app = FastAPI(title="TraceForge")

app.include_router(router, prefix="/api")

# Serve UI
static_path = Path(__file__).parent / "static"
app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
