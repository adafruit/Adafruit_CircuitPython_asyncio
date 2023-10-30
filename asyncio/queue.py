"""
Exceptions and classes related to asyncio Queue implementations.
"""

from . import event


class QueueEmpty(Exception):
    """Raised when Queue.get_nowait() is called on an empty Queue."""


class QueueFull(Exception):
    """Raised when the Queue.put_nowait() method is called on a full Queue."""


class Queue:
    """
    A queue, useful for coordinating producer and consumer coroutines.

    If maxsize is less than or equal to zero, the queue size is infinite. If it
    is an integer greater than 0, then "await put()" will block when the
    queue reaches maxsize, until an item is removed by get().

    Unlike CPython's asyncio.Queue, this implementation is backed by a list rather
    than `collections.deque` because smaller boards may not have the library
    implemented.
    """

    def __init__(self, maxsize=0):
        self.maxsize = maxsize

        self._queue = []

        self._join_counter = 0
        self._join_event = event.Event()
        self._join_event.set()

        self._put_event = event.Event()
        self._get_event = event.Event()

    def _get(self):
        value = self._queue.pop(0)
        self._get_event.set()
        self._get_event.clear()
        return value

    def _put(self, val):
        self._join_counter += 1
        self._join_event.clear()

        self._queue.append(val)

        self._put_event.set()
        self._put_event.clear()

    async def get(self):
        """
        Remove and return an item from the queue.

        If queue is empty, wait until an item is available.
        """
        while self.empty():
            await self._put_event.wait()
        return self._get()

    def get_nowait(self):
        """
        Remove and return an item from the queue.

        If queue is empty, raise QueueEmpty.
        """
        if self.empty():
            raise QueueEmpty()
        return self._get()

    async def put(self, val):
        """
        Put an item into the queue.

        If the queue is full, waits until a free
        slot is available before adding item.
        """
        while self.full():
            await self._get_event.wait()
        self._put(val)

    def put_nowait(self, val):
        """
        Put an item into the queue.

        If the queue is full, raises QueueFull.
        """
        if self.full():
            raise QueueFull()
        self._put(val)

    def qsize(self):
        """
        Number of items in this queue.
        """
        return len(self._queue)

    def empty(self):
        """
        Return True if the queue is empty.
        """
        return len(self._queue) == 0

    def full(self):
        """
        Return True if there are maxsize items in the queue.
        """
        return 0 < self.maxsize <= self.qsize()

    def task_done(self):
        """
        Indicate that a formerly enqueued task is complete.

        If a join() is currently blocking, it will resume when all items have
        been processed (meaning that a task_done() call was received for every
        item that had been put() into the queue).

        Raises ValueError if called more times than there were items placed in
        the queue.
        """
        if self._join_counter == 0:
            # Can't have less than 0
            raise ValueError("task_done() called too many times")

        self._join_counter -= 1

        if self._join_counter == 0:
            self._join_event.set()

    async def join(self):
        """
        Block until all items in the queue have been gotten and processed.
        """
        await self._join_event.wait()
