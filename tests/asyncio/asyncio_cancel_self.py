# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test a task cancelling itself (currently unsupported)
import asyncio


async def task():
    print("task start")
    global_task.cancel()


async def main():
    global global_task
    global_task = asyncio.create_task(task())
    try:
        await global_task
    except asyncio.CancelledError:
        print("main cancel")
    print("main done")


try:
    asyncio.run(main())
except RuntimeError as er:
    print(er)
