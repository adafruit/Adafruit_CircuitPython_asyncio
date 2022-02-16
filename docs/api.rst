:py:mod:`~asyncio`

.. If you created a package, create one automodule per module in the package.

.. If your library file(s) are nested in a directory (e.g. /adafruit_foo/foo.py)
.. use this format as the module name: "adafruit_foo.foo"

.. automodule:: asyncio
    :members:

.. automodule:: asyncio.core
    :members:
    :exclude-members: SingletonGenerator, IOQueue

.. automodule:: asyncio.event
    :members:
    :exclude-members: ThreadSafeFlag

.. automodule:: asyncio.funcs
    :members:

.. automodule:: asyncio.lock
    :members:

.. automodule:: asyncio.stream
    :members:
    :exclude-members: stream_awrite

.. automodule:: asyncio.task
    :members:
    :exclude-members: ph_meld, ph_pairing, ph_delete, TaskQueue
