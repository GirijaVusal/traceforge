from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routers import router

app = FastAPI(title="TraceForge")

# Include API router
app.include_router(router)

# Mount static folder
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
