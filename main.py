import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from traceforge.apis.routers import router

app = FastAPI(title="TraceForge")

app.include_router(router, prefix="/api")
current_dir = os.path.dirname(os.path.realpath(__file__))
ui_path = os.path.join(current_dir, "tfg_ui.html")


@app.get("/")
async def serve_ui():
    return FileResponse(ui_path)


app.mount("/", StaticFiles(directory="."), name="static")
