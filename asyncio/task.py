# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019-2020 Damien P. George
#
# This code comes from MicroPython, and has not been run through black or pylint there.
# Altering these files significantly would make merging difficult, so we will not use
# pylint or black.
# pylint: skip-file
# fmt: off
"""
Tasks
=====
"""

# This file contains the core TaskQueue based on a pairing heap, and the core Task class.
# They can optionally be replaced by C implementations.

from . import core


class CancelledError(BaseException):
    """Injected into a task when calling `Task.cancel()`"""

    pass


class InvalidStateError(Exception):
    """Can be raised in situations like setting a result value for a task object that already has a result value set."""

    pass


# pairing-heap meld of 2 heaps; O(1)
def ph_meld(h1, h2):
    if h1 is None:
        return h2
    if h2 is None:
        return h1
    lt = core.ticks_diff(h1.ph_key, h2.ph_key) < 0
    if lt:
        if h1.ph_child is None:
            h1.ph_child = h2
        else:
            h1.ph_child_last.ph_next = h2
        h1.ph_child_last = h2
        h2.ph_next = None
        h2.ph_rightmost_parent = h1
        return h1
    else:
        h1.ph_next = h2.ph_child
        h2.ph_child = h1
        if h1.ph_next is None:
            h2.ph_child_last = h1
            h1.ph_rightmost_parent = h2
        return h2


# pairing-heap pairing operation; amortised O(log N)
def ph_pairing(child):
    heap = None
    while child is not None:
        n1 = child
        child = child.ph_next
        n1.ph_next = None
        if child is not None:
            n2 = child
            child = child.ph_next
            n2.ph_next = None
            n1 = ph_meld(n1, n2)
        heap = ph_meld(heap, n1)
    return heap


# pairing-heap delete of a node; stable, amortised O(log N)
def ph_delete(heap, node):
    if node is heap:
        child = heap.ph_child
        node.ph_child = None
        return ph_pairing(child)
    # Find parent of node
    parent = node
    while parent.ph_next is not None:
        parent = parent.ph_next
    parent = parent.ph_rightmost_parent
    # Replace node with pairing of its children
    if node is parent.ph_child and node.ph_child is None:
        parent.ph_child = node.ph_next
        node.ph_next = None
        return heap
    elif node is parent.ph_child:
        child = node.ph_child
        next = node.ph_next
        node.ph_child = None
        node.ph_next = None
        node = ph_pairing(child)
        parent.ph_child = node
    else:
        n = parent.ph_child
        while node is not n.ph_next:
            n = n.ph_next
        child = node.ph_child
        next = node.ph_next
        node.ph_child = None
        node.ph_next = None
        node = ph_pairing(child)
        if node is None:
            node = n
        else:
            n.ph_next = node
    node.ph_next = next
    if next is None:
        node.ph_rightmost_parent = parent
        parent.ph_child_last = node
    return heap


# TaskQueue class based on the above pairing-heap functions.
class TaskQueue:
    def __init__(self):
        self.heap = None

    def peek(self):
        return self.heap

    def push(self, v, key=None):
        assert v.ph_child is None
        assert v.ph_next is None
        v.data = None
        v.ph_key = key if key is not None else core.ticks()
        self.heap = ph_meld(v, self.heap)

    def pop(self):
        v = self.heap
        assert v.ph_next is None
        self.heap = ph_pairing(v.ph_child)
        v.ph_child = None
        return v

    def remove(self, v):
        self.heap = ph_delete(self.heap, v)

    # Compatibility aliases, remove after they are no longer used
    push_head = push
    push_sorted = push
    pop_head = pop

# Task class representing a coroutine, can be waited on and cancelled.
class Task:
    """This object wraps a coroutine into a running task. Tasks can be waited on
    using ``await task``, which will wait for the task to complete and return the
    return value of the task.

    Tasks should not be created directly, rather use ``create_task`` to create them.
    """

    def __init__(self, coro, globals=None):
        self.coro = coro  # Coroutine of this Task
        self.data = None  # General data for queue it is waiting on
        self.state = True  # None, False, True, a callable, or a TaskQueue instance
        self.ph_key = 0  # Pairing heap
        self.ph_child = None  # Paring heap
        self.ph_child_last = None  # Paring heap
        self.ph_next = None  # Paring heap
        self.ph_rightmost_parent = None  # Paring heap

    def __iter__(self):
        if not self.state:
            # Task finished, signal that is has been await'ed on.
            self.state = False
        elif self.state is True:
            # Allocated head of linked list of Tasks waiting on completion of this task.
            self.state = TaskQueue()
        elif type(self.state) is not TaskQueue:
            # Task has state used for another purpose, so can't also wait on it.
            raise RuntimeError("can't wait")
        return self

    # CircuitPython needs __await()__.
    __await__ = __iter__

    def __next__(self):
        if not self.state:
            if self.data is None:
                # Task finished but has already been sent to the loop's exception handler.
                raise StopIteration
            else:
                # Task finished, raise return value to caller so it can continue.
                raise self.data
        else:
            # Put calling task on waiting queue.
            self.state.push(core.cur_task)
            # Set calling task's data to this task that it waits on, to double-link it.
            core.cur_task.data = self

    def done(self):
        """Whether the task is complete."""

        return not self.state

    def cancel(self, msg=None):
        """Cancel the task by injecting a ``CancelledError`` into it. The task
        may or may not ignore this exception.
        """

        # Check if task is already finished.
        if not self.state:
            return False
        # Can't cancel self (not supported yet).
        if self is core.cur_task:
            raise RuntimeError("can't cancel self")
        # If Task waits on another task then forward the cancel to the one it's waiting on.
        while isinstance(self.data, Task):
            self = self.data
        # Reschedule Task as a cancelled task.
        if hasattr(self.data, "remove"):
            # Not on the main running queue, remove the task from the queue it's on.
            self.data.remove(self)
            core._task_queue.push(self)
        elif core.ticks_diff(self.ph_key, core.ticks()) > 0:
            # On the main running queue but scheduled in the future, so bring it forward to now.
            core._task_queue.remove(self)
            core._task_queue.push(self)
        self.data = CancelledError(msg) if msg else CancelledError()
        return True

    def get_coro(self):
        return self.coro

    def add_done_callback(self, callback):
        raise NotImplementedError()

    def remove_done_callback(self, callback):
        raise NotImplementedError()

    def set_result(self, result):
        raise RuntimeError('Task does not support set_result operation')

    def result(self):
        """
        Return the result of the Task.

        If the Task is done, the result of the wrapped coroutine is returned (or if the coroutine raised an exception, that exception is re-raised.)

        If the Task has been cancelled, this method raises a CancelledError exception.

        If the Task’s result isn’t yet available, this method raises a InvalidStateError exception.

        """
        if not self.done():
            raise InvalidStateError()

        exception = self.exception()

        if exception is not None:
            raise exception

        if not isinstance(self.data, StopIteration):
            # If this isn't the case then we're in an odd state.
            return None

        return self.data.value

    def set_exception(self, exception):
        raise RuntimeError('Task does not support set_exception operation')

    def exception(self):
        """
        Return the exception that was set on this Task.

        The exception (or None if no exception was set) is returned only if the Task is done.

        If the Task has been cancelled, this method raises a CancelledError exception.

        If the Task isn’t done yet, this method raises an InvalidStateError exception.
        """
        if not self.done():
            raise InvalidStateError()

        if isinstance(self.data, core.CancelledError):
            raise self.data

        if isinstance(self.data, StopIteration):
            # If the data is a stop iteration we can assume this
            # was a successful run rather than any possible exception
            return None

        if not isinstance(self.data, BaseException):
            # If the data is not any type of exception we can treat it as
            # something else we don't understand but not an exception.
            return None

        return self.data

    def cancelled(self) -> bool:
        """
        Return True if the Task is cancelled.

        The Task is cancelled when the cancellation was requested with cancel() and
        the wrapped coroutine propagated the CancelledError exception thrown into it.
        """
        if not self.done():
            return False

        return isinstance(self.data, core.CancelledError)
