# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test cancelling a task that is waiting on a task that just finishes.
import asyncio


async def sleep_task():
    print("sleep_task sleep")
    await asyncio.sleep(0)
    print("sleep_task wake")


async def wait_task(t):
    print("wait_task wait")
    await t
    print("wait_task wake")


async def main():
    waiting_task = asyncio.create_task(wait_task(asyncio.create_task(sleep_task())))

    print("main sleep")
    await asyncio.sleep(0)
    print("main sleep")
    await asyncio.sleep(0)

    waiting_task.cancel()
    print("main wait")
    try:
        await waiting_task
    except asyncio.CancelledError as er:
        print(repr(er))


asyncio.run(main())
