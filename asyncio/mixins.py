"""Event loop mixins."""

from . import events


class _LoopBoundMixin:
    _loop = None

    def _get_loop(self):
        loop = events._get_running_loop()

        if self._loop is None:
            self._loop = loop
        if loop is not self._loop:
            raise RuntimeError(f'{repr(self)} is bound to a different event loop')
        return loop
