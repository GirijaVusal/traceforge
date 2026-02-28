# traceforge/core/context.py

import contextvars
from typing import Optional

from .models import Span, Trace

_current_trace = contextvars.ContextVar("current_trace", default=None)
_current_span = contextvars.ContextVar("current_span", default=None)


def set_trace(trace: Trace):
    _current_trace.set(trace)


def get_trace() -> Optional[Trace]:
    return _current_trace.get()


def set_current_span(span: Span):
    _current_span.set(span)


def get_current_span() -> Optional[Span]:
    return _current_span.get()
