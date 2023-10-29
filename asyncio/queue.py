from . import event


class QueueEmpty(Exception):
    pass


class QueueFull(Exception):
    pass


class Queue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._queue = list()

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
        while self.empty():
            await self._put_event.wait()
        return self._get()

    def get_nowait(self):
        if self.empty():
            raise QueueEmpty()
        return self._get()

    async def put(self, val):
        while self.full():
            await self._get_event.wait()
        self._put(val)

    def put_nowait(self, val):
        if self.full():
            raise QueueFull()
        self._put(val)

    def qsize(self):
        return len(self._queue)

    def empty(self):
        return len(self._queue) == 0

    def full(self):
        return 0 < self.maxsize <= self.qsize()

    def task_done(self):
        self._join_counter -= 1

        if self._join_counter <= 0:
            # Can't have less than 0
            self._join_counter = 0
            self._join_event.set()

    async def join(self):
        await self._join_event.wait()
