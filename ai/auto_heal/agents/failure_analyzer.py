"""
agents/failure_analyzer.py
"""
from langsmith import traceable


@traceable(name="failure-analyzer")
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
