import contextvars
from contextlib import contextmanager

from ..exporters.base import get_exporter
from .models import Trace

_active_trace_cv = contextvars.ContextVar("active_trace", default=None)
_active_span_cv = contextvars.ContextVar("active_span", default=None)


class BaseExporter:
    def export(self, trace_dict: dict):
        """Must be implemented by child classes."""
        raise NotImplementedError

    async def flush(self):
        """
        Optional: Wait for background tasks to finish.
        Default implementation does nothing.
        """
        pass


class TraceManager:
    def __init__(self, project):
        self.project = project

    async def flush(self):
        """
        Public method to ensure all background exports
        are finished before the script exits.
        """
        exporter = get_exporter()
        if exporter and hasattr(exporter, "flush"):
            await exporter.flush()

    @contextmanager
    def start(self, library: str = "auto", metadata: dict = None):
        """
        Starts a trace.
        'library' can be 'langchain', 'pydantic_ai', or 'auto'.
        """
        metadata = metadata or {}
        # Ensure the library name is saved in the trace metadata
        metadata["library"] = library

        trace = Trace(project=self.project, metadata=metadata)

        token = _active_trace_cv.set(trace)
        try:
            yield trace
        finally:
            trace.end()
            exporter = get_exporter()
            if exporter:
                exporter.export(trace.to_dict())
            _active_trace_cv.reset(token)


# Helper functions to be used by span.py
def get_trace():
    return _active_trace_cv.get()


def get_current_span():
    return _active_span_cv.get()


def set_current_span(span):
    _active_span_cv.set(span)
