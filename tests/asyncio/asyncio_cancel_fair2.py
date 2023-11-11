# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test fairness of cancelling a task
# That tasks which keeps being cancelled by multiple other tasks gets a chance to run
import asyncio


async def task_a():
    try:
        while True:
            print("sleep a")
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        print("cancelled a")


async def task_b(id, other):
    while other.cancel():
        print("sleep b", id)
        await asyncio.sleep(0)
    print("done b", id)


async def main():
    t = asyncio.create_task(task_a())
    for i in range(3):
        asyncio.create_task(task_b(i, t))
    await t


asyncio.run(main())
