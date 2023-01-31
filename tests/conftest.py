"""Load tango-specific pytest fixtures."""

from tango.test_utils import state, command_typed_values, attribute_typed_values
from tango.test_utils import server_green_mode, attr_data_format
from tango.test_utils import extract_as, base_type
import pytest

import sys
import os
import json

__all__ = ("state", "command_typed_values", "attribute_typed_values",
           "server_green_mode", "attr_data_format", "extract_as", "base_type")


@pytest.hookimpl()
def pytest_sessionfinish(session):
    """ Collects all tests to be run and outputs to bat script """
    if "--collect-only" in sys.argv and "-q" in sys.argv and "nt" in os.name:
        print("Generating windows test script...")
        script_path = os.path.join(os.path.dirname(__file__), "run_tests_win.bat")
        with open(script_path, "w") as f:
            f.write("REM this script will run all tests separately.\n")
            for item in session.items:
                f.write(
                    "pytest -c pytest_empty_config.txt -v "
                )  # this empty file is created by appveyor
                f.write(f'"{item.nodeid}"\n')
                # Abort if pytest could not execute properly
                # From: https://docs.pytest.org/en/7.1.x/reference/exit-codes.html
                #   Exit code 0: All tests were collected and passed successfully
                #   Exit code 1: Tests were collected and run but some of the tests failed
                #   Exit code 2: Test execution was interrupted by the user
                #   Exit code 3: Internal error happened while executing tests
                #   Exit code 4: pytest command line usage error
                #   Exit code 5: No tests were collected
                f.write("if %ERRORLEVEL% geq 2 if %ERRORLEVEL% leq 5 exit /b %ERRORLEVEL%\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport():
    """ Produces summary.json file for quick windows test summary """
    summary_path = "summary.json"

    outcome = yield  # Run all other pytest_runtest_makereport non wrapped hooks
    result = outcome.get_result()
    if result.when == "call" and "nt" in os.name and os.path.isfile(summary_path):
        with open(summary_path, "r+") as f:
            summary = f.read()
            try:
                summary = json.loads(summary)
            except Exception:
                summary = []
            finally:
                outcome = str(result.outcome).capitalize()
                test = {
                    "testName": result.nodeid,
                    "outcome": outcome,
                    "durationMilliseconds": result.duration,
                    "StdOut": result.capstdout,
                    "StdErr": result.capstderr,
                }
                summary.append(test)
                f.seek(0)
                f.write(json.dumps(summary))
                f.truncate()
