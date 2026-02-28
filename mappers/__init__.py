# traceforge/mappers/__init__.py
# from .pydanticai_ms import map_pydanticai
from ..core.constants import AILibrary
from .langchain_ms import map_langchain


# def standardize_output(obj, library=AILibrary.Auto, session_id=None):
#     """
#     Standardizes output based on a specific library choice or auto-detection.
#     """
#     # 1. Handle Lists
#     if isinstance(obj, list):
#         return [standardize_output(item, session_id, library) for item in obj]

#     # 2. Force specific library if requested
#     if library == AILibrary.LANGCHAIN:
#         return map_langchain(obj, session_id=session_id)

#     # if library == AILibrary.PYDANTIC_AI:
#     #     return map_pydanticai(obj, session_id=session_id)

#     # 3. Fallback to 'Auto-Sniffing' logic if library is AUTO
#     obj_module = getattr(obj, "__module__", "")
#     if "langchain" in obj_module:
#         return map_langchain(obj, session_id=session_id)
#     # if "pydantic_ai" in obj_module:
#     #     return map_pydanticai(obj, session_id=session_id)

#     return obj



# traceforge/mappers/__init__.py
from ..core.constants import AILibrary
from .langchain_ms import map_langchain
from .schema import create_standard_msg

# def standardize_output(obj, library=AILibrary.AUTO, session_id=None):
#     """
#     Standardizes output for Agents, Tools, and intermediate Workflow steps.
#     """
#     # 1. Handle the 7-step Workflow Tuples (e.g., from detect_and_translate)
#     # This specifically catches: return TranslationResult, token_usage
#     if isinstance(obj, tuple) and len(obj) == 2:
#         data_obj, usage = obj
        
#         # Extract tokens from your service's usage dict
#         p_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
#         c_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
        
#         # Extract content from TranslationResult object or fallback to string
#         content = str(data_obj)
#         thought = None
        
#         if hasattr(data_obj, "translation"):
#             content = f"[{data_obj.queried_lang} -> EN]: {data_obj.translation}"
#             # You can even pass the confidence to the thought/reasoning block
#             thought = f"Detected {data_obj.queried_lang} with {data_obj.confidence*100:.1f}% confidence."

#         return [create_standard_msg(
#             role="tool", # UI shows wrench icon
#             content=content,
#             session_id=session_id,
#             thought=thought,
#             prompt_tokens=p_tokens,
#             completion_tokens=c_tokens,
#             raw_metadata=str(data_obj) 
#         )]

#     # 2. Handle Lists (Recursive)
#     if isinstance(obj, list):
#         return [standardize_output(item, library, session_id) for item in obj]

#     # 3. Standard AI Library Detection
#     obj_module = getattr(obj, "__module__", "")
#     if library == AILibrary.LANGCHAIN or "langchain" in obj_module:
#         return map_langchain(obj, session_id=session_id)

#     # 4. Fallback for simple strings/dicts (Detection, Intent, etc.)
#     if isinstance(obj, (str, dict)):
#         return [create_standard_msg(
#             role="tool",
#             content=str(obj),
#             session_id=session_id
#         )]

#     return obj



def standardize_output(obj, library="auto", session_id=None):
    """
    Consolidated Standardizer. 
    Ensures outputs are always a flat list of UI-ready messages.
    """
    # 1. If it's already a list, process each item but FLATTEN the result
    if isinstance(obj, list):
        items = []
        for item in obj:
            res = standardize_output(item, library, session_id)
            if isinstance(res, list):
                items.extend(res)
            else:
                items.append(res)
        return items

    # 2. If it's a LangChain message object
    obj_module = getattr(obj, "__module__", "")
    if library == "langchain" or "langchain" in obj_module:
        return map_langchain(obj, session_id=session_id)

    # 3. Handle the 7-step Workflow Tuples (Result, TokenUsage)
    if isinstance(obj, tuple) and len(obj) == 2:
        data_obj, usage = obj
        p_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
        c_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
        
        return [create_standard_msg(
            role="tool",
            content=str(data_obj),
            session_id=session_id,
            prompt_tokens=p_tokens,
            completion_tokens=c_tokens
        )]

    # 4. Fallback for raw strings/dicts (The "Tool" look)
    # This catches "English", "Add 2 and 3...", etc.
    return [create_standard_msg(
        role="tool",
        content=str(obj),
        session_id=session_id
    )]
