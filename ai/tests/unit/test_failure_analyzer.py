"""
Node-level unit tests for failure_analyzer.

No mocking needed — pure deterministic logic.
Interview talking point: this is the simplest node test;
it proves the classification contract holds across all failure types.
"""
import pytest
from ai.auto_heal.agents.failure_analyzer import failure_analyzer


def test_classifies_locator_failure_by_default():
    state = {"error_message": "NoSuchElementException: Unable to locate element"}
    result = failure_analyzer(state)
    assert result["failure_type"] == "locator"


def test_classifies_timeout_failure():
    state = {"error_message": "TimeoutException: Timed out waiting for element"}
    result = failure_analyzer(state)
    assert result["failure_type"] == "timeout"


def test_classifies_assertion_failure():
    state = {"error_message": "AssertionError: expected 'Submit' but got 'Cancel'"}
    result = failure_analyzer(state)
    assert result["failure_type"] == "assertion"


def test_defaults_to_locator_on_empty_error():
    state = {"error_message": ""}
    result = failure_analyzer(state)
    assert result["failure_type"] == "locator"


def test_defaults_to_locator_on_missing_error_key():
    state = {}
    result = failure_analyzer(state)
    assert result["failure_type"] == "locator"


@pytest.mark.parametrize("error,expected_type", [
    ("TimeoutException: element not visible after 10s", "timeout"),
    ("AssertionError: 0 != 1", "assertion"),
    ("StaleElementReferenceException: element no longer in DOM", "locator"),
    ("ElementClickInterceptedException", "locator"),
])
def test_failure_type_parametrized(error, expected_type):
    result = failure_analyzer({"error_message": error})
    assert result["failure_type"] == expected_type
