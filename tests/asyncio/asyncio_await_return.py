# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test that tasks return their value correctly to the caller

import asyncio


async def example():
    return 42


async def main():
    # Call function directly via an await
    print(await example())

    # Create a task and await on it
    task = asyncio.create_task(example())
    print(await task)


asyncio.run(main())
