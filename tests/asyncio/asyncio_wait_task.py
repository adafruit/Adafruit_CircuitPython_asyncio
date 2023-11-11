# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# Test waiting on a task
import asyncio


import time

if hasattr(time, "ticks_ms"):
    ticks = time.ticks_ms
    ticks_diff = time.ticks_diff
else:

    def ticks():
        return int(time.time() * 1000)

    def ticks_diff(ticks_a, ticks_b):
        return ticks_b - ticks_a


async def task(task_id):
    print("task", task_id)


async def delay_print(delay_time, task_id):
    await asyncio.sleep(delay_time)
    print(task_id)


async def task_raise():
    print("task_raise")
    raise ValueError


async def main():
    print("start")

    # Wait on a task
    task_1 = asyncio.create_task(task(1))
    await task_1

    # Wait on a task that's already done
    task_1 = asyncio.create_task(task(2))
    await asyncio.sleep(0.001)
    await task_1

    # Wait again on same task
    await task_1

    print("----")

    # Create 2 tasks
    task_1 = asyncio.create_task(delay_print(0.2, "hello"))
    task_2 = asyncio.create_task(delay_print(0.4, "world"))

    # Time how long the tasks take to finish, they should execute in parallel
    print("start")
    ticks_1 = ticks()
    await task_1
    ticks_2 = ticks()
    await task_2
    ticks_3 = ticks()
    print(
        "took {} {}".format(
            round(ticks_diff(ticks_2, ticks_1), -2),
            round(ticks_diff(ticks_3, ticks_2), -2),
        )
    )

    # Wait on a task that raises an exception
    task_1 = asyncio.create_task(task_raise())
    try:
        await task_1
    except ValueError:
        print("ValueError")


asyncio.run(main())
