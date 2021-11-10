# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# This list of frozen files doesn't include task.py because that's provided by the C module.
freeze(
    "..",
    (
        "uasyncio/__init__.py",
        "uasyncio/core.py",
        "uasyncio/event.py",
        "uasyncio/funcs.py",
        "uasyncio/lock.py",
        "uasyncio/stream.py",
    ),
    opt=3,
)
