_exporter = None


class BaseExporter:
    def export(self, trace_dict: dict):
        raise NotImplementedError

    async def flush(self):
        """
        Optional: Wait for background tasks to finish.
        Default implementation does nothing.
        """
        pass


def set_exporter(exporter):
    global _exporter
    _exporter = exporter


def get_exporter():
    return _exporter
