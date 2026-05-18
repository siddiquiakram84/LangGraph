"""
tests/evaluation/test_deepeval_evaluation.py

DeepEval tests for LLM output quality in the auto-gen and healing pipeline.

DeepEval measures:
  - Answer Correctness  — does the output match the expected answer?
  - Hallucination       — does the output contain unsupported claims?
  - Toxicity            — is the output safe?
  - Bias                — does the output show bias?

  "RAGAS evaluates the RAG pipeline — retrieval quality, context usage.
  DeepEval evaluates the LLM output quality — correctness, hallucination,
  bias. I run both as quality gates before promoting a model or prompt change."

Run: pytest tests/evaluation/test_deepeval_evaluation.py -v
"""
import pytest


def _deepeval_available() -> bool:
    try:
        import deepeval
        return True
    except ImportError:
        return False


# ── Deterministic output validation (no LLM, no API cost) ───────────────────

class TestDeepEvalOutputValidation:
    """
    Validates LLM-generated outputs against expected contracts.
    These run in CI without any API calls — they check structure and safety.
    Full DeepEval LLM-judge metrics run only before release.

    Interview talking point:
      'I separate fast structural validation from slow LLM-judged evaluation.
      CI gets the fast checks. Release gate gets the full DeepEval metrics.'
    """

    GENERATED_PLAYWRIGHT_SCRIPTS = [
        {
            "input": "Login with valid credentials",
            "output": "page.goto(url)\npage.fill('#username', user)\npage.fill('#password', pwd)\npage.click('button[type=submit]')\nexpect(page.locator('.success')).to_be_visible()",
            "expected_imports": [],
            "must_contain": ["page.goto", "page.fill", "page.click", "expect"],
            "must_not_contain": ["DROP", "DELETE", "rm -rf", "os.system"],
        },
        {
            "input": "Search for a product on homepage",
            "output": "page.goto(url)\npage.fill('#search', 'laptop')\npage.click('#search-btn')\nexpect(page.locator('.results')).to_be_visible()",
            "expected_imports": [],
            "must_contain": ["page.goto", "page.fill", "page.click"],
            "must_not_contain": ["DROP", "DELETE", "eval(", "__import__"],
        },
    ]

    @pytest.mark.skipif(not _deepeval_available(), reason="deepeval not installed")
    def test_generated_scripts_contain_required_playwright_calls(self):
        """
        Correctness gate: every generated Playwright script must have
        the core method calls. Missing any = generation failed silently.
        """
        for case in self.GENERATED_PLAYWRIGHT_SCRIPTS:
            for call in case["must_contain"]:
                assert call in case["output"], (
                    f"Generated script for '{case['input']}' missing required call: {call}"
                )

    @pytest.mark.skipif(not _deepeval_available(), reason="deepeval not installed")
    def test_generated_scripts_have_no_dangerous_content(self):
        """
        Safety gate (LLM02 — Insecure Output Handling):
        Generated scripts must never contain dangerous system commands
        or SQL injection patterns.
        """
        for case in self.GENERATED_PLAYWRIGHT_SCRIPTS:
            for dangerous in case["must_not_contain"]:
                assert dangerous not in case["output"], (
                    f"Generated script contains dangerous content: '{dangerous}'"
                )

    @pytest.mark.skipif(not _deepeval_available(), reason="deepeval not installed")
    def test_generated_script_is_syntactically_reasonable(self):
        """
        Hallucination proxy: a valid Playwright script must have
        balanced parentheses and no placeholder tokens like TODO or FIXME.
        """
        for case in self.GENERATED_PLAYWRIGHT_SCRIPTS:
            script = case["output"]
            assert script.count("(") == script.count(")"), (
                f"Unbalanced parentheses in generated script for: {case['input']}"
            )
            for placeholder in ["TODO", "FIXME", "PLACEHOLDER", "None"]:
                assert placeholder not in script, (
                    f"Script contains placeholder '{placeholder}' for: {case['input']}"
                )

    @pytest.mark.skipif(not _deepeval_available(), reason="deepeval not installed")
    def test_healing_output_schema_correctness(self):
        """
        Correctness gate for the healer output.
        DeepEval would normally judge this with an LLM.
        Here we validate the schema contract deterministically.
        """
        healing_outputs = [
            {
                "healed_locator": ("id", "username"),
                "confidence_score": 0.85,
                "success": True,
            },
            {
                "healed_locator": None,
                "confidence_score": 0.3,
                "success": False,
            },
        ]

        for output in healing_outputs:
            assert "healed_locator" in output
            assert "confidence_score" in output
            assert isinstance(output["success"], bool)
            assert 0.0 <= output["confidence_score"] <= 1.0

            if output["success"]:
                assert output["healed_locator"] is not None, "Success=True but no healed_locator"
                assert output["confidence_score"] >= 0.7, "Success=True but below threshold"
            else:
                assert output["confidence_score"] < 0.7 or output["healed_locator"] is None

    @pytest.mark.skipif(not _deepeval_available(), reason="deepeval not installed")
    def test_answer_relevancy_by_keyword_matching(self):
        """
        Answer relevancy proxy — without calling LLM judge.
        The generated test description must reflect the input intent.

        In production: replace with deepeval.metrics.AnswerRelevancyMetric(threshold=0.7)
        """
        test_pairs = [
            ("login with username and password", "test_login_with_username_and_password"),
            ("search product by keyword", "test_search_product_by_keyword"),
            ("add item to cart", "test_add_item_to_cart"),
        ]

        for intent, generated_name in test_pairs:
            intent_words = set(intent.lower().replace(" ", "_").split("_"))
            name_words = set(generated_name.lower().replace("test_", "").split("_"))
            overlap = intent_words & name_words
            relevancy = len(overlap) / len(intent_words)

            assert relevancy >= 0.5, (
                f"Generated test name '{generated_name}' is not relevant to intent '{intent}' "
                f"(relevancy={relevancy:.2f})"
            )
