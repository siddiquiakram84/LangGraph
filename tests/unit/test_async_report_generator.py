"""
tests/unit/test_async_report_generator.py

pytest-asyncio tests for the async report generator node.

Interview talking point:
  - asyncio_mode = auto in pytest.ini means no decorator needed on each test.
  - async def test_* functions are picked up automatically.
  - This is exactly what the JD means by "pytest-asyncio" experience.
"""
import pytest
from agents.async_report_generator import async_report_generator


async def test_async_report_contains_all_required_keys():
    state = {
        "failed_locator": ("id", "broken-btn"),
        "healed_locator": ("id", "submit-btn"),
        "confidence_score": 0.88,
        "success": True,
        "screenshot_path": "healing_reports/shot.png",
        "logic_suggestion": None,
    }

    result = await async_report_generator(state)

    assert "report" in result
    assert set(result["report"].keys()) == {
        "failed_locator", "healed_locator", "confidence_score",
        "success", "screenshot_path", "logic_suggestion",
    }


async def test_async_report_success_true_when_healed():
    state = {
        "failed_locator": ("id", "old-id"),
        "healed_locator": ("id", "new-id"),
        "confidence_score": 0.91,
        "success": True,
        "screenshot_path": None,
        "logic_suggestion": None,
    }

    result = await async_report_generator(state)
    assert result["report"]["success"] is True
    assert result["report"]["healed_locator"] == ("id", "new-id")


async def test_async_report_success_false_when_not_healed():
    state = {
        "failed_locator": ("id", "unknown-element"),
        "healed_locator": None,
        "confidence_score": 0.3,
        "success": False,
        "screenshot_path": None,
        "logic_suggestion": None,
    }

    result = await async_report_generator(state)
    assert result["report"]["success"] is False
    assert result["report"]["healed_locator"] is None


async def test_async_report_confidence_score_preserved():
    state = {
        "failed_locator": ("name", "q"),
        "healed_locator": ("name", "search"),
        "confidence_score": 0.76,
        "success": True,
        "screenshot_path": "healing_reports/s.png",
        "logic_suggestion": "Verify expected assertion value.",
    }

    result = await async_report_generator(state)
    assert result["report"]["confidence_score"] == pytest.approx(0.76)
    assert result["report"]["logic_suggestion"] == "Verify expected assertion value."
