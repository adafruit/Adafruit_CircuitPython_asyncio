# SPDX-FileCopyrightText: 2019-2020 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019-2022 Damien P. George
#
# This code comes from MicroPython, and has not been run through black or pylint there.
# Altering these files significantly would make merging difficult, so we will not use
# pylint or black.
# pylint: skip-file
# fmt: off
"""
Functions
=========
"""
try:
    from typing import List, Tuple, Optional, Union

    from .task import TaskQueue, Task
except ImportError:
    pass

from . import core


ALL_COMPLETED = 'ALL_COMPLETED'
FIRST_COMPLETED = 'FIRST_COMPLETED'
FIRST_EXCEPTION = 'FIRST_EXCEPTION'


async def wait(
        *aws,
        timeout: Optional[Union[int, float]]=None,
        return_when: Union[ALL_COMPLETED, FIRST_COMPLETED, FIRST_EXCEPTION]=ALL_COMPLETED
) -> Tuple[List[Task], List[Task]]:
    """
    Wait for the awaitables given by aws to complete.

    Returns two lists of tasks: (done, pending)

    Usage:

        done, pending = await asyncio.wait(aws)

    If a timeout is set and occurs, any tasks that haven't completed will be returns
    in the second list of tasks (pending)

    This is a coroutine.
    """
    if not aws:
        raise ValueError('Set of awaitable is empty.')

    if return_when not in (FIRST_COMPLETED, FIRST_EXCEPTION, ALL_COMPLETED):
        raise ValueError(f'Invalid return_when value: {return_when}')

    aws = [core._promote_to_task(aw) for aw in aws]
    task_self = core.cur_task

    tasks_done: List[Task] = [aw for aw in aws if aw.done()]
    tasks_pending: List[Task] = [aw for aw in aws if not aw.done()]

    if len(done) > 0 and return_when == FIRST_COMPLETED:
        return tasks_done, tasks_pending

    if len(pending) == 0 and return_when == ALL_COMPLETED:
        return tasks_done, tasks_pending

    if return_when == FIRST_EXCEPTION:
        has_exception = any([
            (
                not isinstance(t.data, core.CancelledError) and
                not isinstance(t.data, StopIteration) and
                isinstance(t.data, Exception)
            )
            for t in tasks_done
        ])

        if has_exception:
            return tasks_done, tasks_pending

    def _done_callback(t: Task, er):
        tasks_pending.remove(t)
        tasks_done.add(t)

        if len(pending) == 0:
            core._task_queue.push_head(task_self)
        elif return_when == FIRST_COMPLETED:
            core._task_queue.push_head(task_self)
        elif er is not None and return_when == FIRST_EXCEPTION:
            core._task_queue.push_head(task_self)
            return

    for t in pending:
        t.state = _done_callback

    task_timeout = None
    if timeout is not None:
        def _timeout_callback():
            core._task_queue.push_head(task_self)

        task_timeout = core._promote_to_task(core.sleep(timeout))
        task_timeout.state = _timeout_callback

    # Pass back to the task queue until needed
    await core._never()

    if task_timeout is not None:
        task_timeout.cancel()

    # Clean up and remove the callback from pending tasks
    for t in pending:
        if t.state is _done_callback:
            t.state = True

    return tasks_done, tasks_pending


async def wait_for(aw, timeout: Union[int, float]):
    """Wait for the *aw* awaitable to complete, but cancel if it takes longer
    than *timeout* seconds. If *aw* is not a task then a task will be created
    from it.

    If a timeout occurs, it cancels the task and raises ``asyncio.TimeoutError``:
    this should be trapped by the caller.

    Returns the return value of *aw*.

    This is a coroutine.
    """

    task_aw = core._promote_to_task(aw)

    try:
        # Wait for the timeout to elapse.
        done, pending = await wait(aw, timeout=timeout)

        if len(pending) > 0:
            # If our tasks are still pending we timed out
            # Per the Python 3.11 docs
            # > If a timeout occurs, it cancels the task and raises TimeoutError.
            for t in pending:
                t.cancel()
            raise core.TimeoutError()
    except core.CancelledError:
        # Per the Python 3.11 docs
        # > If the wait is cancelled, the future aw is also cancelled.
        task_aw.cancel()
        raise

    # This should be completed, so it should immediately return the value or exception when awaiting it.
    return await task_aw


def wait_for_ms(aw, timeout):
    """Similar to `wait_for` but *timeout* is an integer in milliseconds.

    This is a coroutine, and a MicroPython extension.
    """
    return wait_for(aw, timeout / 1000)


async def gather(*aws, return_exceptions=False):
    """Run all *aws* awaitables concurrently. Any *aws* that are not tasks
    are promoted to tasks.

    Returns a list of return values of all *aws*
    """
    if not aws:
        return []

    tasks = [core._promote_to_task(aw) for aw in aws]

    try:
        if not return_exceptions:
            await wait(tasks, return_when=FIRST_EXCEPTION)
        else:
            await wait(tasks, return_when=ALL_COMPLETED)
    except core.CancelledError:
        for task in tasks:
            task.cancel()
        raise

    results = []
    for task in tasks:
        if not task.done():
            results.append(None)
            continue

        try:
            results.append(task.result())
        except BaseException as e:
            if not return_exceptions:
                raise e

            results.append(e)

    return results
