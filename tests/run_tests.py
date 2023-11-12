#! /usr/bin/env python3

# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
#
# MicroPython uasyncio module
# MIT license; Copyright (c) 2019 Damien P. George
#

import sys
import os

try:
    from typing import List, Tuple
except ImportError:
    pass

AVAILABLE_SUITES = ["asyncio"]


LICENSE_PREFIX = """# SPDX-FileCopyrightText: 2019 Damien P. George
#
# SPDX-License-Identifier: MIT
"""


def get_interpreter():
    interpreter = os.getenv("MICROPY_MICROPYTHON")

    if interpreter:
        return interpreter

    if sys.platform == "win32":
        return "micropython.exe"

    return "micropython"


def get_testcases(suite: str) -> List[str]:
    if sys.platform == "win32":
        # dir /b prints only contained filenames, one on a line
        # http://www.microsoft.com/resources/documentation/windows/xp/all/proddocs/en-us/dir.mspx
        result = os.system("dir /b %s/*.py >tests.lst" % suite)
    else:
        result = os.system("ls %s/*.py | xargs -n1 basename >tests.lst" % suite)

    assert result == 0

    with open("tests.lst") as test_list_file:
        testcases = test_list_file.readlines()
        testcases = [l[:-1] for l in testcases]

    os.system("rm tests.lst")
    assert testcases, "No tests found in dir '%s', which is implausible" % suite

    return testcases


def run_testcase(suite: str, testcase: str):
    qtest = "%s/%s" % (suite, testcase)

    try:
        with open("%s.exp" % qtest) as expected_output_file:
            expected_output = expected_output_file.read()
    except OSError as exc:
        raise RuntimeError("SKIP") from exc

    with open("{0}.out".format(qtest), "w") as actual_output_file:
        actual_output_file.write(LICENSE_PREFIX)

    result = os.system(
        "{0} {1} 2>> {1}.out >> {1}.out".format(get_interpreter(), qtest)
    )

    with open("%s.out" % qtest) as actual_output_file:
        actual_output = actual_output_file.read()

    if result != 0:
        actual_output += "\n\nCRASH\n"

    if actual_output == LICENSE_PREFIX + "SKIP\n":
        print("skip %s" % qtest)
        raise RuntimeError("SKIP")

    if actual_output != expected_output:
        print("FAIL %s" % qtest)
        os.system("diff -u {0}.exp {0}.out".format(qtest))
        return False

    print("pass %s" % qtest)
    return True


def run_suite(suite: str) -> Tuple[int, int, int]:
    test_count = 0
    passed_count = 0
    skip_count = 0

    testcases = get_testcases(suite)

    for testcase in testcases:
        try:
            if run_testcase(suite, testcase):
                passed_count += 1

            test_count += 1
        except RuntimeError as exc:
            if str(exc) == "SKIP":
                skip_count += 1

    return test_count, passed_count, skip_count


def main():
    test_count = 0
    passed_count = 0
    skip_count = 0

    for suite in AVAILABLE_SUITES:
        suite_test_count, suite_passed_count, suite_skip_count = run_suite(suite)

        test_count += suite_test_count
        passed_count += suite_passed_count
        skip_count += suite_skip_count

    print("-" * 20)
    print("%s tests performed" % test_count)
    print("%s tests passed" % passed_count)
    if test_count != passed_count:
        print("%s tests failed" % (test_count - passed_count))
    if skip_count:
        print("%s tests skipped" % skip_count)

    if test_count - passed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
