import functools
import inspect

# from traceforge.core.context import get_trace
from traceforge.core.manager import get_trace
from traceforge.core.models import universal_serializer

from .span import execute_span_async, execute_span_sync


def trace_span(name=None):
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            trace = get_trace()
            span_name = name or func.__name__
            if not trace:
                return await func(*args, **kwargs)

            # Start span inside the library logic
            span = trace.start_span(
                name=span_name, inputs={"args": args, "kwargs": kwargs}
            )
            try:
                result = await func(*args, **kwargs)
                span.outputs = {"result": universal_serializer(result)}
                return result
            except Exception as e:
                span.error = str(e)
                raise e
            finally:
                span.end()

        return async_wrapper

    return decorator


# def trace_step(name: str = None, span_type: str = "tool"):
#     """
#     The primary TraceForge decorator for tracking workflow steps.
#     Works for both sync and async functions.
#     """

#     def decorator(func):
#         # Auto-detect name if not provided
#         step_name = name or func.__name__

#         @functools.wraps(func)
#         async def async_wrapper(*args, **kwargs):
#             return await execute_span_async(func, step_name, span_type, args, kwargs)

#         @functools.wraps(func)
#         def sync_wrapper(*args, **kwargs):
#             return execute_span_sync(func, step_name, span_type, args, kwargs)

#         # Return the correct wrapper based on the function type
#         return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

#     return decorator


def trace_step(name: str = None, span_type: str = "tool"):
    """
    Primary TraceForge decorator.
    Handles both sync and async functions and delegates to centralized span logic.
    """

    def decorator(func):
        # Fallback to function name if no string is provided
        step_name = name or func.__name__

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # execute_span_async handles the mapping and universal_serializer
            return await execute_span_async(func, step_name, span_type, args, kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # execute_span_sync handles the mapping and universal_serializer
            return execute_span_sync(func, step_name, span_type, args, kwargs)

        # Smart detection of function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
