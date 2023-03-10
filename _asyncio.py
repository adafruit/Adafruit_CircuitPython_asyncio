import collections
import inspect
import types


class BaseLoop:
    def poll_isr(self):
        pass

_running_loop = None

def set_running_loop(loop):
    assert loop is None or isinstance(loop, BaseLoop)
    global _running_loop
    _running_loop = loop

def get_running_loop():
    return _running_loop

def iscoroutinefunction(func):
    """Return True if func is a decorated coroutine function."""
    return inspect.iscoroutinefunction(func)

# Prioritize native coroutine check to speed-up
# asyncio.iscoroutine.
_COROUTINE_TYPES = (types.CoroutineType, types.GeneratorType,
                    collections.abc.Coroutine)

def iscoroutine(obj):
    """Return True if obj is a coroutine object."""
    return isinstance(obj, _COROUTINE_TYPES)
