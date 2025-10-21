# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test fairness of scheduler
import asyncio


async def task(id, t):
    print("task start", id)
    while True:
        if t > 0:
            print("task work", id)
        await asyncio.sleep(t)


async def main():
    t1 = asyncio.create_task(task(1, -0.01))
    t2 = asyncio.create_task(task(2, 0.1))
    t3 = asyncio.create_task(task(3, 0.18))
    t4 = asyncio.create_task(task(4, -100))
    await asyncio.sleep(0.5)
    t1.cancel()
    t2.cancel()
    t3.cancel()
    t4.cancel()
    print("finish")


asyncio.run(main())
