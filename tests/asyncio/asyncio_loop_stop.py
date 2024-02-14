# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test Loop.stop() to stop the event loop
import asyncio


async def task():
    print("task")


async def main():
    print("start")

    # Stop the loop after next yield
    loop.stop()

    # Check that calling stop() again doesn't do/break anything
    loop.stop()

    # This await should stop
    print("sleep")
    await asyncio.sleep(0)

    # Schedule stop, then create a new task, then yield
    loop.stop()
    asyncio.create_task(task())
    await asyncio.sleep(0)

    # Final stop
    print("end")
    loop.stop()


loop = asyncio.get_event_loop()
loop.create_task(main())

for i in range(3):
    print("run", i)
    loop.run_forever()
