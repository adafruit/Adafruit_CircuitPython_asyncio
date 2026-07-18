# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file

import asyncio


async def forever():
    print("forever start")
    await asyncio.sleep(10)


async def main():
    print("main start")
    asyncio.create_task(forever())
    await asyncio.sleep(0.001)
    print("main done")
    return 42


print(asyncio.run(main()))
