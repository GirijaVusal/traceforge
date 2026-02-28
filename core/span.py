# # traceforge/core/span.py
# from .context import get_current_span, get_trace, set_current_span
from traceforge.mappers import standardize_output

from .manager import get_current_span, get_trace, set_current_span
from .models import Span, universal_serializer


def _prepare_span(func, name, span_type, args, kwargs):
    trace = get_trace()
    if not trace:
        # If this prints, the "pocket" is still empty
        # print("DEBUG: Wrapper called but no active trace found")
        return None, None

    parent = get_current_span()
    span = Span(
        name=name,
        span_type=span_type,
        trace_id=trace.trace_id,
        parent_id=parent.span_id if parent else None,
    )

    span.inputs = {
        "args": universal_serializer(args),
        "kwargs": universal_serializer(kwargs),
    }

    # IMPORTANT: Attach the span to the trace immediately
    if parent:
        parent.children.append(span)
    else:
        trace.spans.append(span)

    return span, parent


# async def execute_span_async(func, name, span_type, args, kwargs):
#     """Handles async function tracing and auto-serializes output."""
#     span, parent = _prepare_span(func, name, span_type, args, kwargs)
#     if not span:
#         return await func(*args, **kwargs)

#     set_current_span(span)
#     try:
#         raw_result = await func(*args, **kwargs)
#         # Transform raw LangChain/Pydantic objects into clean dicts
#         result = universal_serializer(raw_result)
#         print(result)
#         span.outputs = {"result": result}
#         return result
#     except Exception as e:
#         span.error = str(e)
#         raise
#     finally:
#         span.end()
#         set_current_span(parent)

# def execute_span_sync(func, name, span_type, args, kwargs):
#     """Handles standard sync function tracing and auto-serializes output."""
#     span, parent = _prepare_span(func, name, span_type, args, kwargs)
#     if not span:
#         return func(*args, **kwargs)

#     set_current_span(span)
#     try:
#         raw_result = func(*args, **kwargs)
#         # FIX: Added serialization here so sync calls return clean JSON-safe data
#         result = universal_serializer(raw_result)
#         print(result)
#         span.outputs = {"result": result}
#         return result
#     except Exception as e:
#         span.error = str(e)
#         raise
#     finally:
#         span.end()
#         set_current_span(parent)


async def execute_span_async(func, name, span_type, args, kwargs):
    """Traces the function and maps output to TraceForge Standard without forcing string serialization."""
    span, parent = _prepare_span(func, name, span_type, args, kwargs)
    if not span:
        return await func(*args, **kwargs)

    set_current_span(span)
    try:
        # 1. Run the actual function
        raw_result = await func(*args, **kwargs)
        # session_id = kwargs.get("session_id")
        trace = get_trace()
        session_id = kwargs.get("session_id") or (trace.metadata.get("session_id") if trace else "auto")
        # If not provided it will be fall to auto
        library = kwargs.get("library", "auto")

        # 3. Standardize for the Logs
        # We transform the data into our Standard JSON format here
        if isinstance(raw_result, dict) and "messages" in raw_result:
            # Create a copy so we don't mutate the original agent's result
            log_result = raw_result.copy()
            log_result["messages"] = standardize_output(
                raw_result["messages"], session_id=session_id, library=library
            )
        else:
            log_result = standardize_output(
                raw_result, session_id=session_id, library=library
            )

        # 4. Save the Standardized version to the span
        # Note: We still use universal_serializer here ONLY for the log file
        # to ensure it can be written to disk, but we don't affect the 'return'
        span.outputs = {"result": universal_serializer(log_result)}

        # 5. Return the RAW result so the agent doesn't break
        return raw_result

    except Exception as e:
        span.error = str(e)
        raise
    finally:
        span.end()
        set_current_span(parent)


def execute_span_sync(func, name, span_type, args, kwargs):
    """Handles standard sync function tracing and auto-serializes output."""
    span, parent = _prepare_span(func, name, span_type, args, kwargs)
    if not span:
        return func(*args, **kwargs)

    set_current_span(span)
    try:
        # 1. Run the actual function
        raw_result = func(*args, **kwargs)

        # 2. Extract configuration from kwargs
        # session_id = kwargs.get("session_id")
        trace = get_trace()
        session_id = kwargs.get("session_id") or (trace.metadata.get("session_id") if trace else "auto")
        # Mention the library explicitly or use "auto"
        library = kwargs.get("library", "auto")

        # 3. Standardize for the Logs
        # We transform the data into our Standard JSON format here
        if isinstance(raw_result, dict) and "messages" in raw_result:
            # Create a copy so we don't mutate the original agent's result
            log_result = raw_result.copy()
            log_result["messages"] = standardize_output(
                raw_result["messages"], session_id=session_id, library=library
            )
        else:
            log_result = standardize_output(
                raw_result, session_id=session_id, library=library
            )

        # 4. Save the Standardized version to the span
        # Note: We still use universal_serializer here ONLY for the log file
        # to ensure it can be written to disk, but we don't affect the 'return'
        span.outputs = {"result": universal_serializer(log_result)}

        # 5. Return the RAW result so the agent doesn't break
        return raw_result

    except Exception as e:
        span.error = str(e)
        raise
    finally:
        span.end()
        set_current_span(parent)
