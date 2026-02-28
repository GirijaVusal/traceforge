import inspect

from traceforge.core.span import execute_span_async, execute_span_sync


def wrap_tool(tool, name=None):
    """
    Wrap any callable tool (sync or async).
    Returns a wrapped version of the tool that automatically creates spans.
    """
    tool_name = name or getattr(tool, "__name__", "tool")

    # If the tool is 'async def'
    if inspect.iscoroutinefunction(tool):

        async def async_wrapper(*args, **kwargs):
            return await execute_span_async(
                tool,
                name=tool_name,
                span_type="tool",
                args=args,
                kwargs=kwargs,
            )

        return async_wrapper

    # If the tool is a standard 'def'
    else:

        def sync_wrapper(*args, **kwargs):
            return execute_span_sync(
                tool,
                name=tool_name,
                span_type="tool",
                args=args,
                kwargs=kwargs,
            )

        return sync_wrapper
