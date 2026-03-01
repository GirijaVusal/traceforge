# # # traceforge/core/models.py
# from __future__ import annotations

# import uuid
# from dataclasses import asdict, dataclass, field, is_dataclass
# from datetime import datetime
# from typing import Any, Dict, List, Optional


# def utcnow():
#     return datetime.utcnow()


# def universal_serializer(obj: Any) -> Any:
#     """
#     Recursively converts non-serializable objects into JSON-friendly formats.
#     Works for LangChain, Pydantic, Dataclasses, and more.
#     """
#     if obj is None or isinstance(obj, (str, int, float, bool)):
#         return obj

#     # 1. Handle LangChain/Pydantic (Objects with to_dict or dict methods)
#     if hasattr(obj, "to_dict") and callable(obj.to_dict):
#         return universal_serializer(obj.to_dict())
#     if hasattr(obj, "dict") and callable(obj.dict):
#         return universal_serializer(obj.dict())

#     # 2. Handle Dataclasses
#     if is_dataclass(obj):
#         return universal_serializer(asdict(obj))

#     # 3. Handle Iterables
#     if isinstance(obj, (list, tuple, set)):
#         return [universal_serializer(item) for item in obj]

#     # 4. Handle Dictionaries
#     if isinstance(obj, dict):
#         return {str(k): universal_serializer(v) for k, v in obj.items()}

#     # 5. Handle Datetime
#     if isinstance(obj, datetime):
#         return obj.isoformat()

#     # Fallback: Stringify the object if we don't know what it is
#     return str(obj)


# @dataclass
# class Span:
#     name: str
#     span_type: str
#     trace_id: str
#     parent_id: Optional[str] = None

#     span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
#     start_time: datetime = field(default_factory=utcnow)
#     end_time: Optional[datetime] = None
#     duration_ms: Optional[float] = None

#     inputs: Dict[str, Any] = field(default_factory=dict)
#     outputs: Dict[str, Any] = field(default_factory=dict)
#     error: Optional[str] = None
#     metadata: Dict[str, Any] = field(default_factory=dict)
#     children: List["Span"] = field(default_factory=list)

#     def end(self):
#         self.end_time = utcnow()
#         self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000

#     def to_dict(self):
#         return {
#             "span_id": self.span_id,
#             "trace_id": self.trace_id,
#             "parent_id": self.parent_id,
#             "name": self.name,
#             "type": self.span_type,
#             "start_time": self.start_time.isoformat(),
#             "end_time": self.end_time.isoformat() if self.end_time else None,
#             "duration_ms": self.duration_ms,
#             # Use universal_serializer on inputs and outputs
#             "inputs": universal_serializer(self.inputs),
#             "outputs": universal_serializer(self.outputs),
#             "error": self.error,
#             "metadata": self.metadata,
#             "children": [c.to_dict() for c in self.children],
#         }


# @dataclass
# class Trace:
#     project: str
#     metadata: Dict[str, Any] = field(default_factory=dict)
#     trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
#     start_time: datetime = field(default_factory=utcnow)
#     end_time: Optional[datetime] = None
#     spans: List[Span] = field(default_factory=list)

#     def end(self):
#         self.end_time = utcnow()

#     def to_dict(self):
#         return {
#             "trace_id": self.trace_id,
#             "project": self.project,
#             "metadata": self.metadata,
#             "start_time": self.start_time.isoformat(),
#             "end_time": self.end_time.isoformat() if self.end_time else None,
#             "spans": [s.to_dict() for s in self.spans],
#         }


# ================ NEW =========


# traceforge/core/models.py

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


def utcnow():
    return datetime.utcnow()


def universal_serializer(obj: Any) -> Any:
    if obj is None or isinstance(obj, (str, int, float, bool)):
        return obj

    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return universal_serializer(obj.to_dict())

    if hasattr(obj, "dict") and callable(obj.dict):
        return universal_serializer(obj.dict())

    if is_dataclass(obj):
        return universal_serializer(asdict(obj))

    if isinstance(obj, (list, tuple, set)):
        return [universal_serializer(item) for item in obj]

    if isinstance(obj, dict):
        return {str(k): universal_serializer(v) for k, v in obj.items()}

    if isinstance(obj, datetime):
        return obj.isoformat()

    return str(obj)


@dataclass
class Span:
    name: str
    span_type: str
    trace_id: str
    parent_id: Optional[str] = None

    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=utcnow)
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None

    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    children: List["Span"] = field(default_factory=list)

    def end(self):
        self.end_time = utcnow()
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000

    def to_db_tuple(self):
        return (
            self.span_id,
            self.trace_id,
            self.parent_id,
            self.name,
            self.span_type,
            self.start_time.timestamp(),
            self.end_time.timestamp() if self.end_time else None,
            self.duration_ms,
            str(universal_serializer(self.inputs)),
            str(universal_serializer(self.outputs)),
            self.error,
            str(universal_serializer(self.metadata)),
        )


@dataclass
class Trace:
    project: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    start_time: datetime = field(default_factory=utcnow)
    end_time: Optional[datetime] = None
    spans: List[Span] = field(default_factory=list)

    def end(self):
        self.end_time = utcnow()

    def to_db_tuple(self):
        return (
            self.trace_id,
            self.project,
            str(universal_serializer(self.metadata)),
            self.start_time.timestamp(),
            self.end_time.timestamp() if self.end_time else None,
        )
