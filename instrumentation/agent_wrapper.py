# # traceforge/instrumentation/agent_wrapper.py

import inspect

from traceforge.core.models import universal_serializer
from traceforge.core.span import execute_span_async, execute_span_sync


def wrap_agent(agent, method_name="run", name="Agent"):
    original = getattr(agent, method_name)

    if inspect.iscoroutinefunction(original):

        async def async_wrapper(*args, **kwargs):
            raw_result = await execute_span_async(
                original, name=name, span_type="agent", args=args, kwargs=kwargs
            )
            # FORCE serialization before it leaves the library
            return universal_serializer(raw_result)

        setattr(agent, method_name, async_wrapper)
    else:

        def sync_wrapper(*args, **kwargs):
            raw_result = execute_span_sync(
                original, name=name, span_type="agent", args=args, kwargs=kwargs
            )
            # FORCE serialization before it leaves the library
            return universal_serializer(raw_result)

        setattr(agent, method_name, sync_wrapper)

    return agent
