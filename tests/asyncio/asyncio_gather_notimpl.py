# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test asyncio.gather() function, features that are not implemented.
import asyncio


def custom_handler(loop, context):
    print(repr(context["exception"]))


async def task(id):
    print("task start", id)
    await asyncio.sleep(0.01)
    print("task end", id)
    return id


async def gather_task(t0, t1):
    print("gather_task start")
    await asyncio.gather(t0, t1)
    print("gather_task end")


async def main():
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(custom_handler)

    # Test case where can't wait on a task being gathered.
    print("=" * 10)
    tasks = [asyncio.create_task(task(1)), asyncio.create_task(task(2))]
    gt = asyncio.create_task(gather_task(tasks[0], tasks[1]))
    await asyncio.sleep(0)  # let the gather start
    try:
        await tasks[0]  # can't await because this task is part of the gather
    except RuntimeError as er:
        print(repr(er))
    await gt

    # Test case where can't gather on a task being waited.
    print("=" * 10)
    tasks = [asyncio.create_task(task(1)), asyncio.create_task(task(2))]
    asyncio.create_task(gather_task(tasks[0], tasks[1]))
    await tasks[0]  # wait on this task before the gather starts
    await tasks[1]

    # Can't gather after a task has completed
    print("=" * 10)
    task_1 = asyncio.create_task(task(1))

    try:
        # Wait for task_1 to complete
        await task_1

        await asyncio.gather(task_1)
    except RuntimeError as er:
        print(repr(er))


asyncio.run(main())
