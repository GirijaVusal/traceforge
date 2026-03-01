# traceforge/cli.py

import webbrowser

import typer
import uvicorn

app = typer.Typer()


@app.command()
def start(
    host: str = "127.0.0.1",
    port: int = 8001,
    open_browser: bool = True,
):
    print("🚀 Starting TraceForge server...")

    if open_browser:
        webbrowser.open(f"http://{host}:{port}")

    uvicorn.run(
        "traceforge.apis.app:app",
        host=host,
        port=port,
        reload=False,
    )


def main():
    app()
