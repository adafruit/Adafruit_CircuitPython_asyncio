# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#
# pylint: skip-file
#
# Test general exception handling
import asyncio


# main task raising an exception
async def main():
    print("main start")
    raise ValueError(1)


try:
    asyncio.run(main())
except ValueError as er:
    print("ValueError", er.args[0])


# sub-task raising an exception
async def task():
    print("task start")
    raise ValueError(2)
    print("task done")


async def main():
    print("main start")
    t = asyncio.create_task(task())
    await t
    print("main done")


try:
    asyncio.run(main())
except ValueError as er:
    print("ValueError", er.args[0])


# main task raising an exception with sub-task not yet scheduled
# TODO not currently working, task is never scheduled
async def task():
    # print('task run') uncomment this line when it works
    pass


async def main():
    print("main start")
    asyncio.create_task(task())
    raise ValueError(3)
    print("main done")


try:
    asyncio.run(main())
except ValueError as er:
    print("ValueError", er.args[0])
