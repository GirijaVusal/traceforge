import datetime


def create_standard_msg(
    role: str,
    content: str,
    session_id: str = None,
    thought: str = None,
    tool_calls: list = None,
    prompt_tokens: int = None,
    completion_tokens: int = None,
    **extra_metadata,
):
    """
    TraceForge Master Schema.
    Standardizes messages across all AI libraries.
    """
    print("----------create_standard_msg -----------")
    # Calculate total if components exist
    total_tokens = None
    if prompt_tokens is not None or completion_tokens is not None:
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

    # 1. Internal Standard Object
    standard = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "thought": thought,
        "tool_calls": tool_calls or [],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
        "metadata": {
            "timestamp": datetime.datetime.now().isoformat(),
            **extra_metadata,
        },
    }

    return {
        "type": "ai" if role == "assistant" else role,
        "session_id": session_id,
        "data": {
            "content": standard["content"],
            "additional_kwargs": {
                "reasoning_content": standard["thought"],
                "session_id": session_id,
                "usage": standard["usage"],  # Standardized token part
                **standard["metadata"],
            },
            "tool_calls": [
                {
                    "name": t.get("name"),
                    "args": t.get("arguments"),
                    "id": t.get("call_id"),
                }
                for t in standard["tool_calls"]
            ],
        },
    }
