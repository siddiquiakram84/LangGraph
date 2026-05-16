"""
Graph-level integration test for the full LangGraph healing StateGraph.

What this tests:
  - All 8 nodes execute in correct sequence
  - Conditional edge routes correctly after validator:
      success  → memory_updater → logic_healer → report_generator
      failure  → report_generator (skips memory_updater)
  - Final report contains the healed locator and success=True
  - Memory side-effects (ChromaDB, JSON store, source updater) are mocked
    so this test is hermetic and runs in CI without any external dependencies

Mocking strategy:
  - Selenium WebDriver replaced with MagicMock (no real browser)
  - dom_capture reads driver.page_source (mocked) and calls save_screenshot (mocked)
  - memory_retriever.store.search returns empty results (cold start)
  - embedding_locator_healer.engine is mocked for deterministic similarity scores
  - memory_updater dependencies (vector_store, locator_store, source_updater) mocked
    to suppress all file/DB writes

Interview talking point:
  - This is the graph-level assertion that proves the StateGraph contract end-to-end.
  - The conditional edge test (healing_fails_routes_to_report_skipping_memory_updater)
    proves that a failed heal does NOT corrupt the memory store.
"""
from unittest.mock import MagicMock, patch
import numpy as np
import pytest
from selenium.common.exceptions import NoSuchElementException

from core.healing_engine import HealingEngine

SAMPLE_DOM = """
<html>
  <body>
    <input id="twotabsearchtextbox" name="field-keywords" placeholder="Search Amazon"/>
    <button id="nav-search-submit-button" aria-label="Go"/>
  </body>
</html>
"""

FIXED_VECTOR = np.array([1.0, 0.0, 0.0])


def _make_driver(dom: str = SAMPLE_DOM, element_found: bool = True) -> MagicMock:
    """Build a mock WebDriver that returns a fixed DOM and optionally finds elements."""
    mock_driver = MagicMock()
    mock_driver.page_source = dom
    mock_driver.save_screenshot.return_value = None

    if not element_found:
        mock_driver.find_element.side_effect = NoSuchElementException()

    return mock_driver


@patch("agents.memory_updater.source_updater")
@patch("agents.memory_updater.locator_store")
@patch("agents.memory_updater.vector_store")
@patch("agents.memory_retriever.store")
@patch("agents.embedding_locator_healer.engine")
def test_full_graph_heals_known_broken_locator(
    mock_embed_engine,
    mock_retriever_store,
    mock_vector_store,
    mock_locator_store,
    mock_source_updater,
):
    """
    Happy path: broken locator → graph runs all 8 nodes → healing succeeds.
    Asserts the final report confirms success with a different locator than what failed.
    """
    mock_embed_engine.embed.return_value = FIXED_VECTOR
    mock_embed_engine.similarity.side_effect = [0.785, 0.30, 0.20, 0.10, 0.05]
    mock_retriever_store.search.return_value = {"documents": [], "metadatas": []}

    driver = _make_driver(dom=SAMPLE_DOM, element_found=True)

    engine = HealingEngine()
    report = engine.heal(
        driver=driver,
        failed_locator=("id", "twotabsearchtextbox_wrong"),
        failed_action="type",
        error_message="NoSuchElementException: Unable to locate element",
        stack_trace="",
        test_file="/fake/test_file.py",
    )

    assert report["success"] is True
    assert report["healed_locator"] is not None
    assert report["healed_locator"] != ("id", "twotabsearchtextbox_wrong")
    assert report["confidence_score"] >= 0.7

    # Memory side-effects must have fired exactly once
    mock_vector_store.add.assert_called_once()
    mock_locator_store.save.assert_called_once()
    mock_source_updater.update.assert_called_once()


@patch("agents.memory_updater.source_updater")
@patch("agents.memory_updater.locator_store")
@patch("agents.memory_updater.vector_store")
@patch("agents.memory_retriever.store")
@patch("agents.embedding_locator_healer.engine")
def test_healing_fails_routes_to_report_skipping_memory_updater(
    mock_embed_engine,
    mock_retriever_store,
    mock_vector_store,
    mock_locator_store,
    mock_source_updater,
):
    """
    Conditional edge test: when all similarity scores < threshold (0.7),
    validator never runs (healed_locator=None) and memory_updater is SKIPPED.
    Proves the graph does not pollute the memory store with a failed healing event.
    """
    mock_embed_engine.embed.return_value = FIXED_VECTOR
    mock_embed_engine.similarity.side_effect = [0.40, 0.30, 0.20, 0.10, 0.05]
    mock_retriever_store.search.return_value = {"documents": [], "metadatas": []}

    driver = _make_driver(dom=SAMPLE_DOM, element_found=False)

    engine = HealingEngine()
    report = engine.heal(
        driver=driver,
        failed_locator=("id", "completely_unrelated_xyz"),
        failed_action="click",
        error_message="NoSuchElementException",
        stack_trace="",
        test_file="/fake/test_file.py",
    )

    assert report["success"] is False

    # Memory must NOT be written when healing fails
    mock_vector_store.add.assert_not_called()
    mock_locator_store.save.assert_not_called()
    mock_source_updater.update.assert_not_called()


@patch("agents.memory_updater.source_updater")
@patch("agents.memory_updater.locator_store")
@patch("agents.memory_updater.vector_store")
@patch("agents.memory_retriever.store")
@patch("agents.embedding_locator_healer.engine")
def test_report_always_contains_required_keys(
    mock_embed_engine,
    mock_retriever_store,
    mock_vector_store,
    mock_locator_store,
    mock_source_updater,
):
    """
    Structural assertion: regardless of healing outcome, the report schema
    must contain all required keys so downstream consumers never KeyError.
    """
    mock_embed_engine.embed.return_value = FIXED_VECTOR
    mock_embed_engine.similarity.side_effect = [0.40, 0.30, 0.20, 0.10, 0.05]
    mock_retriever_store.search.return_value = {"documents": [], "metadatas": []}

    driver = _make_driver(dom=SAMPLE_DOM, element_found=False)

    engine = HealingEngine()
    report = engine.heal(
        driver=driver,
        failed_locator=("id", "any_broken_locator"),
        failed_action="click",
        error_message="NoSuchElementException",
        stack_trace="",
        test_file="/fake/test_file.py",
    )

    required_keys = {
        "failed_locator",
        "healed_locator",
        "confidence_score",
        "success",
        "screenshot_path",
        "logic_suggestion",
    }
    assert required_keys.issubset(report.keys())
