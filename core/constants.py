# traceforge/core/constants.py

from enum import Enum


class AILibrary(Enum):
    LANGCHAIN = "langchain"
    PYDANTIC_AI = "pydantic_ai"
    AUTO = "auto"
