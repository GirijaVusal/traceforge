# # traceforge/exporters/base.py

# _exporter = None


# class BaseExporter:
#     def export(self, trace_dict: dict):
#         raise NotImplementedError


# def set_exporter(exporter):
#     global _exporter
#     _exporter = exporter


# def get_exporter():
#     return _exporter


# traceforge/exporters/base.py

_exporter_instance = None


def set_exporter(exporter):
    global _exporter_instance
    _exporter_instance = exporter


def get_exporter():
    return _exporter_instance
