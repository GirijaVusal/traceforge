# traceforge/exporters/json_file.py

import json
from pathlib import Path

from .base import BaseExporter


class JSONExporter(BaseExporter):
    def __init__(self, file_path="traces.jsonl"):
        self.file_path = Path(file_path)

    def export(self, trace_dict):
        with self.file_path.open("a") as f:
            f.write(json.dumps(trace_dict) + "\n")
