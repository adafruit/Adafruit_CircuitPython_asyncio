"""The asyncio package, tracking PEP 3156."""

# This relies on each of the submodules having an __all__ variable.
from .base_events import *
from .coroutines import *
from .events import *
from .exceptions import *
from .futures import *
from .locks import *
# from .protocols import *
from .runners import *
from .queues import *
from .circuitpython_streams import *
# from .subprocess import *
from .tasks import *
from .taskgroups import *
from .timeouts import *
# from .threads import *
# from .transports import *

__all__ = (
    base_events.__all__ +
    coroutines.__all__ +
    events.__all__ +
    exceptions.__all__ +
    futures.__all__ +
    locks.__all__ +
    # protocols.__all__ +
    runners.__all__ +
    queues.__all__ +
    circuitpython_streams.__all__ +
    # subprocess.__all__ +
    tasks.__all__ +
    # threads.__all__ +
    timeouts.__all__ +
    # transports.__all__ +
    ()
)

from .circuitpython_events import *
__all__ += circuitpython_events.__all__
