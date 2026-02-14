"""
agents/failure_analyzer.py
"""


def failure_analyzer(state):

    error = state.get("error_message", "")

    failure_type = "locator"

    if "TimeoutException" in error:
        failure_type = "timeout"

    if "AssertionError" in error:
        failure_type = "assertion"

    return {

        "failure_type": failure_type
    }
