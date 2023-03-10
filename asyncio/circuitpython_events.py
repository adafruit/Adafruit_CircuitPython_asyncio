from . import base_events

__all__ = "CircuitPythonEventLoop",


class CircuitPythonEventLoop(base_events.BaseEventLoop):
    def _process_events(self, event_list):
        pass
