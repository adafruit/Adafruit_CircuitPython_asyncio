# CIRCUITPY-CHANGE: SPDX
# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT

# MicroPython asyncio module
# MIT license; Copyright (c) 2019-2020 Damien P. George
#
# CIRCUITPY-CHANGE
# This code comes from MicroPython, and has not been run through black or pylint there.
# Altering these files significantly would make merging difficult, so we will not use
# pylint or black.
# pylint: skip-file
# fmt: off

from . import core


# Event class for primitive events that can be waited on, set, and cleared
class Event:
    # CIRCUITPY-CHANGE: doc
    """Create a new event which can be used to synchronize tasks. Events
    start in the cleared state.
    """

    def __init__(self):
        self.state = False  # False=unset; True=set
        self.waiting = core.TaskQueue()  # Queue of Tasks waiting on completion of this event

    def is_set(self):
        # CIRCUITPY-CHANGE: doc
        """Returns ``True`` if the event is set, ``False`` otherwise."""

        return self.state

    def set(self):
        # CIRCUITPY-CHANGE: doc
        """Set the event. Any tasks waiting on the event will be scheduled to run.
        """

        # Event becomes set, schedule any tasks waiting on it
        # Note: This must not be called from anything except the thread running
        # the asyncio loop (i.e. neither hard or soft IRQ, or a different thread).
        while self.waiting.peek():
             # CIRCUITPY-CHANGE: when 8.x support is discontinued, change to .push() and .pop()
            core._task_queue.push_head(self.waiting.pop_head())
        self.state = True

    def clear(self):
        # CIRCUITPY-CHANGE: doc
        """Clear the event."""

        self.state = False

    # CIRCUITPY-CHANGE: async
    async def wait(self):
        # CIRCUITPY-CHANGE: doc
        """Wait for the event to be set. If the event is already set then it returns
        immediately.
        """

        if not self.state:
            # Event not set, put the calling task on the event's waiting queue
             # CIRCUITPY-CHANGE: when 8.x support is discontinued, change to .push()
            self.waiting.push_head(core.cur_task)
            # Set calling task's data to the event's queue so it can be removed if needed
            core.cur_task.data = self.waiting
             # CIRCUITPY-CHANGE: use await; never reschedule
            await core._never()
        return True


# CIRCUITPY: remove ThreadSafeFlag; non-standard extension.
