# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test Loop.new_event_loop()
import asyncio


async def task():
    for i in range(4):
        print("task", i)
        await asyncio.sleep(0)
        await asyncio.sleep(0)


async def main():
    print("start")
    loop.create_task(task())
    await asyncio.sleep(0)
    print("stop")
    loop.stop()


# Use default event loop to run some tasks
loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()

# Create new event loop, old one should not keep running
loop = asyncio.new_event_loop()
loop.create_task(main())
loop.run_forever()
