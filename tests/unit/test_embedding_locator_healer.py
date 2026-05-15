"""
Node-level unit tests for embedding_locator_healer.

LLM/embedding mocking strategy:
  - We patch the module-level `engine` instance in embedding_locator_healer.
  - engine.embed() returns a fixed numpy-like MagicMock (direction doesn't matter
    because similarity() is also mocked to return our controlled scores).
  - engine.similarity() uses side_effect to return scores in the exact order
    the node calls it — one score per candidate attribute found in the DOM.

Interview talking point:
  - This proves the CONFIDENCE_THRESHOLD gate (0.7) works correctly.
  - Tests cover: best match above threshold, all matches below threshold,
    and empty DOM with no candidates.
"""
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
from agents.embedding_locator_healer import embedding_locator_healer, CONFIDENCE_THRESHOLD

SAMPLE_DOM = """
<html>
  <body>
    <input id="twotabsearchtextbox" name="field-keywords" placeholder="Search Amazon"/>
    <button id="nav-search-submit-button" aria-label="Go"/>
  </body>
</html>
"""

EMPTY_DOM = "<html><body></body></html>"

FIXED_VECTOR = np.array([1.0, 0.0, 0.0])


def _mock_engine(similarity_scores: list):
    """Helper: return a patched engine with controlled similarity scores."""
    mock = MagicMock()
    mock.embed.return_value = FIXED_VECTOR
    mock.similarity.side_effect = similarity_scores
    return mock


@patch("agents.embedding_locator_healer.engine")
def test_returns_best_match_above_confidence_threshold(mock_engine):
    """
    SAMPLE_DOM has 5 attribute values across two elements.
    We control scores so twotabsearchtextbox scores highest at 0.785 (> 0.7 threshold).
    """
    mock_engine.embed.return_value = FIXED_VECTOR
    # Scores align to DOM attribute extraction order:
    # id="twotabsearchtextbox", name="field-keywords", placeholder="Search Amazon",
    # id="nav-search-submit-button", aria-label="Go"
    mock_engine.similarity.side_effect = [0.785, 0.30, 0.20, 0.10, 0.05]

    state = {
        "failed_locator": ("id", "twotabsearchtextbox_wrong"),
        "dom_snapshot": SAMPLE_DOM,
    }

    result = embedding_locator_healer(state)

    assert result["success"] is True
    assert result["healed_locator"] == ("id", "twotabsearchtextbox")
    assert result["confidence_score"] == pytest.approx(0.785)
    assert result["confidence_score"] >= CONFIDENCE_THRESHOLD


@patch("agents.embedding_locator_healer.engine")
def test_rejects_all_candidates_below_confidence_threshold(mock_engine):
    """
    All similarity scores below 0.7 — healer must return success=False
    and healed_locator=None. This is the critical gate test.
    """
    mock_engine.embed.return_value = FIXED_VECTOR
    mock_engine.similarity.side_effect = [0.45, 0.30, 0.20, 0.10, 0.05]

    state = {
        "failed_locator": ("id", "completely_unrelated_locator"),
        "dom_snapshot": SAMPLE_DOM,
    }

    result = embedding_locator_healer(state)

    assert result["success"] is False
    assert result["healed_locator"] is None
    assert result["confidence_score"] < CONFIDENCE_THRESHOLD


@patch("agents.embedding_locator_healer.engine")
def test_returns_failure_on_empty_dom_with_no_candidates(mock_engine):
    """
    No elements in the DOM → no candidates → nothing to embed or compare.
    Healer must return success=False without calling similarity.
    """
    mock_engine.embed.return_value = FIXED_VECTOR

    state = {
        "failed_locator": ("id", "some_locator"),
        "dom_snapshot": EMPTY_DOM,
    }

    result = embedding_locator_healer(state)

    assert result["success"] is False
    mock_engine.similarity.assert_not_called()


@patch("agents.embedding_locator_healer.engine")
def test_candidate_locators_always_populated_in_output(mock_engine):
    """
    Even when healing fails, candidate_locators must be returned so downstream
    nodes and reports can inspect what was found in the DOM.
    """
    mock_engine.embed.return_value = FIXED_VECTOR
    mock_engine.similarity.side_effect = [0.40, 0.30, 0.20, 0.10, 0.05]

    state = {
        "failed_locator": ("id", "bad_locator"),
        "dom_snapshot": SAMPLE_DOM,
    }

    result = embedding_locator_healer(state)

    assert "candidate_locators" in result
    assert isinstance(result["candidate_locators"], list)
    assert len(result["candidate_locators"]) > 0
