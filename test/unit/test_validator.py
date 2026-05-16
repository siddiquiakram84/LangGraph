"""
Node-level unit tests for the validator agent node.

LLM mocking strategy: Selenium WebDriver is replaced with MagicMock.
We never touch a real browser — the test is fully deterministic.

Interview talking point: validator has a strict contract —
it MUST call find_element with exactly the healed locator tuple,
and it MUST set both validation_success AND success consistently.
"""
from unittest.mock import MagicMock
from selenium.common.exceptions import NoSuchElementException
from ai.agents.validator import validator


def test_returns_success_when_element_found():
    mock_driver = MagicMock()
    mock_driver.find_element.return_value = MagicMock()

    state = {
        "driver": mock_driver,
        "healed_locator": ("id", "twotabsearchtextbox"),
    }

    result = validator(state)

    assert result["validation_success"] is True
    assert result["success"] is True
    mock_driver.find_element.assert_called_once_with("id", "twotabsearchtextbox")


def test_returns_failure_when_element_not_found():
    mock_driver = MagicMock()
    mock_driver.find_element.side_effect = NoSuchElementException()

    state = {
        "driver": mock_driver,
        "healed_locator": ("id", "nonexistent-element"),
    }

    result = validator(state)

    assert result["validation_success"] is False
    assert result["success"] is False


def test_returns_failure_without_calling_driver_when_no_healed_locator():
    mock_driver = MagicMock()

    state = {
        "driver": mock_driver,
        "healed_locator": None,
    }

    result = validator(state)

    assert result["success"] is False
    mock_driver.find_element.assert_not_called()


def test_uses_correct_locator_strategy():
    """Validates that validator passes BOTH by-strategy and value to find_element."""
    mock_driver = MagicMock()
    mock_driver.find_element.return_value = MagicMock()

    state = {
        "driver": mock_driver,
        "healed_locator": ("name", "field-keywords"),
    }

    validator(state)

    args = mock_driver.find_element.call_args[0]
    assert args[0] == "name"
    assert args[1] == "field-keywords"
