# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test current_task() function
import asyncio


async def task(result):
    result[0] = asyncio.current_task()


async def main():
    result = [None]
    t = asyncio.create_task(task(result))
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    print(t is result[0])


asyncio.run(main())
