# mappers/langchain_ms.py

from .schema import create_standard_msg


def map_langchain(msg, session_id=None):
    """
    Maps a LangChain Message object to the TraceForge Standard.
    """
    # # 1. Try to find session_id if not provided
    # # LangChain sometimes hides it in response_metadata or additional_kwargs
    # print("00000000000000000000000")
    # if not session_id:
    #     if hasattr(msg, "response_metadata"):
    #         session_id = msg.response_metadata.get("session_id")
    #     if not session_id and hasattr(msg, "additional_kwargs"):
    #         session_id = msg.additional_kwargs.get("session_id")

    # # 2. Extract Token Usage
    # prompt_tokens = None
    # completion_tokens = None
    # if hasattr(msg, "response_metadata"):
    #     usage = msg.response_metadata.get("token_usage", {})
    #     prompt_tokens = usage.get("prompt_tokens")
    #     completion_tokens = usage.get("completion_tokens")

    # 1. Session ID extraction (as before)
    if not session_id:
        meta = getattr(msg, "response_metadata", {})
        session_id = meta.get("session_id") or msg.additional_kwargs.get("session_id")

    # 2. THE FIX: Robust Token Extraction
    prompt_tokens = None
    completion_tokens = None

    # A. Check New LangChain Standard (usage_metadata attribute)
    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
        prompt_tokens = msg.usage_metadata.get("input_tokens")
        completion_tokens = msg.usage_metadata.get("output_tokens")

    # B. Fallback: Check response_metadata (OpenAI/Anthropic style)
    if prompt_tokens is None:
        res_meta = getattr(msg, "response_metadata", {})

        # Try 'token_usage' (OpenAI)
        token_usage = res_meta.get("token_usage", {})
        # Try 'usage' (Anthropic/Ollama)
        usage = res_meta.get("usage", token_usage)

        prompt_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
        completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens")

    # 3. Extract Reasoning/Thought
    thought = None
    if hasattr(msg, "additional_kwargs"):
        thought = msg.additional_kwargs.get("reasoning_content")

    # 4. Extract Tool Calls
    tool_calls = []
    if hasattr(msg, "tool_calls"):
        for tc in msg.tool_calls:
            tool_calls.append(
                {
                    "call_id": tc.get("id"),
                    "name": tc.get("name"),
                    "arguments": tc.get("args"),
                }
            )

    # Return using our Master Schema
    return create_standard_msg(
        role=msg.type,  # 'human', 'ai', etc.
        content=msg.content,
        session_id=session_id,
        thought=thought,
        tool_calls=tool_calls,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        model_name=getattr(msg, "response_metadata", {}).get(
            "model_name"
        ),  # Example of 'Addition'
    )
