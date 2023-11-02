# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019-2020 Damien P. George

# The rest of the library assumes that `_never` and `_task_queue` should be imported from
# core, which angers pylint.
# pylint: disable=protected-access

"""
Exceptions and classes related to asyncio Queue implementations.
"""

from . import core


class QueueEmpty(Exception):
    """Raised when Queue.get_nowait() is called on an empty Queue."""


class QueueFull(Exception):
    """Raised when the Queue.put_nowait() method is called on a full Queue."""


async def _wait_on_task_queue(task_queue: core.TaskQueue):
    task_queue.push(core.cur_task)
    # Set calling task's data to the TaskQueue so it can be removed if needed
    core.cur_task.data = task_queue
    # Send control back
    await core._never()


def _release_task_queue(task_queue: core.TaskQueue):
    while task_queue.peek():
        core._task_queue.push(task_queue.pop())


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

        self._active_tasks = 0

        self._waiting_for_completion = core.TaskQueue()
        self._waiting_for_put = core.TaskQueue()
        self._waiting_for_get = core.TaskQueue()

    def _get(self):
        value = self._queue.pop(0)
        _release_task_queue(self._waiting_for_get)
        return value

    def _put(self, val):
        self._queue.append(val)
        self._active_tasks += 1
        _release_task_queue(self._waiting_for_put)

    async def get(self):
        """
        Remove and return an item from the queue.

        If queue is empty, wait until an item is available.
        """
        while self.empty():
            await _wait_on_task_queue(self._waiting_for_put)
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
            await _wait_on_task_queue(self._waiting_for_get)
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
        if self._active_tasks == 0:
            # Can't have less than 0
            raise ValueError("task_done() called too many times")

        self._active_tasks -= 1

        if self._active_tasks == 0:
            _release_task_queue(self._waiting_for_completion)

    async def join(self):
        """
        Block until all items in the queue have been gotten and processed.
        """
        await _wait_on_task_queue(self._waiting_for_completion)
