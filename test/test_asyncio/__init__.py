import os
from test import support
from test.support import load_package_tests
from test.support import import_helper

support.requires_working_socket(module=True)

# Skip tests if we don't have concurrent.futures.
import_helper.import_module('concurrent.futures')

def load_tests(*args):
    return load_package_tests(os.path.dirname(__file__), *args)

# CPython unittest library requires these function
from asyncio.circuitpython_events import CircuitPythonEventLoop
async def dummy(*args, **kwargs):
    pass
CircuitPythonEventLoop.shutdown_default_executor = dummy