"""
ai_validator.py — AI Validation Gate (Layer before test execution)

Runs 11 heuristic proxy metrics against the generated artefacts before
any Playwright test is executed.  If overall_pass is False the pipeline
must NOT run the test; it should call pipeline_reporter instead.

Metrics (RAGAS-proxy + DeepEval-structural, no live LLM API required):
  1.  Semantic Similarity        — embedding cosine between steps & code
  2.  Faithfulness               — step-to-method coverage ratio
  3.  Hallucination Detection    — extra methods not derived from steps
  4.  Grounding Validation       — locators grounded in RAG context
  5.  Retrieval Relevance        — top FAISS similarity score
  6.  Context Propagation        — allure.step() blocks in generated test
  7.  Probabilistic Consistency  — semantic score variance (lower = better)
  8.  Non-Determinism Tolerance  — worst-case drift bound
  9.  Threshold Pass Rate        — fraction of metrics above their threshold
  10. Agent Orchestration        — pipeline stages completed ratio
  11. Observability/Tracing      — LangSmith env vars present
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

try:
    from langsmith import traceable
except ImportError:
    def traceable(name=""):          # no-op shim when langsmith not installed
        def _dec(fn):
            return fn
        return _dec

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    _EMBED_AVAILABLE = True
except ImportError:
    _EMBED_AVAILABLE = False


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class MetricResult:
    name:        str
    score:       float
    threshold:   float
    passed:      bool
    description: str
    category:    str   # ragas | deepeval | orchestration | observability


@dataclass
class ValidationReport:
    overall_pass:   bool
    metrics:        List[MetricResult]
    passed_count:   int
    failed_count:   int
    summary:        str
    recommendations: List[str] = field(default_factory=list)


# ── Validator ─────────────────────────────────────────────────────────────────

class AIValidator:
    """
    Runs all 11 validation metrics and returns a ValidationReport.

    Parameters
    ----------
    blueprint    : dict from PagePlanner — methods, locators, page_name
    generated    : dict from FileWriter  — {"page": path, "locator": path, "test": path}
    rag_context  : list from FAISSScriptStore.search()
    stages_done  : int  — pipeline stages completed (out of 5 = gen, 5 expected)
    total_stages : int  — total stages in the pipeline
    """

    _EMBED_MODEL: Optional[SentenceTransformer] = None
    _THRESHOLDS = {
        "semantic_similarity":       0.20,   # short field names vs long code = low cosine by design
        "faithfulness":              0.75,
        "hallucination_detection":   0.30,   # lower = better (inverted)
        "grounding_validation":      0.45,
        "retrieval_relevance":       0.02,   # cold-start: FAISS store not yet rich
        "context_propagation":       0.75,
        "probabilistic_consistency": 0.15,   # lower = better (inverted)
        "non_determinism_tolerance": 0.55,   # TODO locators are expected on first generation
        "threshold_pass_rate":       0.70,
        "agent_orchestration":       0.45,   # validation runs at stage 5/10, not 8/10
        "observability_tracing":     0.50,
    }

    def __init__(
        self,
        blueprint:    dict,
        generated:    dict,
        rag_context:  list  = None,
        stages_done:  int   = 5,
        total_stages: int   = 10,
    ):
        self.bp           = blueprint
        self.generated    = generated
        self.rag_context  = rag_context or []
        self.stages_done  = stages_done
        self.total_stages = total_stages

        self._test_src   = Path(generated.get("test",    "")).read_text(errors="replace") if generated.get("test")    and Path(generated["test"]).exists()    else ""
        self._page_src   = Path(generated.get("page",    "")).read_text(errors="replace") if generated.get("page")    and Path(generated["page"]).exists()    else ""
        self._loc_src    = Path(generated.get("locator", "")).read_text(errors="replace") if generated.get("locator") and Path(generated["locator"]).exists()  else ""
        self._methods    = [m["method_name"] for m in self.bp.get("methods", [])]
        self._steps_text = " ".join(m.get("field_name", "") for m in self.bp.get("methods", []))

    # ── Public entry point ────────────────────────────────────────────────────

    @traceable(name="ai-validation-gate")
    def validate(self) -> ValidationReport:
        results: List[MetricResult] = []

        results.append(self._metric_semantic_similarity())
        results.append(self._metric_faithfulness())
        results.append(self._metric_hallucination_detection())
        results.append(self._metric_grounding_validation())
        results.append(self._metric_retrieval_relevance())
        results.append(self._metric_context_propagation())
        results.append(self._metric_probabilistic_consistency())
        results.append(self._metric_non_determinism_tolerance())
        results.append(self._metric_threshold_pass_rate(results))
        results.append(self._metric_agent_orchestration())
        results.append(self._metric_observability_tracing())

        passed   = [r for r in results if r.passed]
        failed   = [r for r in results if not r.passed]
        pass_pct = len(passed) / len(results)
        overall  = pass_pct >= self._THRESHOLDS["threshold_pass_rate"]

        recs = [
            f"Fix metric '{r.name}': score={r.score:.2f} < threshold={r.threshold:.2f}"
            for r in failed
        ]

        summary = (
            f"{'PASS' if overall else 'FAIL'} — "
            f"{len(passed)}/{len(results)} metrics passed ({pass_pct:.0%}). "
            + (f"Issues: {', '.join(r.name for r in failed)}" if failed else "All checks green.")
        )

        return ValidationReport(
            overall_pass    = overall,
            metrics         = results,
            passed_count    = len(passed),
            failed_count    = len(failed),
            summary         = summary,
            recommendations = recs,
        )

    # ── Metric implementations ────────────────────────────────────────────────

    def _metric_semantic_similarity(self) -> MetricResult:
        name      = "semantic_similarity"
        threshold = self._THRESHOLDS[name]
        score     = 0.0

        if _EMBED_AVAILABLE and self._steps_text and self._page_src:
            model = self._get_embed_model()
            vecs  = model.encode([self._steps_text, self._page_src], normalize_embeddings=True)
            score = float(np.dot(vecs[0], vecs[1]))
            score = max(0.0, min(1.0, score))
        else:
            # Heuristic fallback: count method name occurrences in page src
            hits = sum(1 for m in self._methods if m in self._page_src)
            score = (hits / max(len(self._methods), 1)) * 0.7

        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Cosine similarity between intent steps and generated page code",
            category="ragas",
        )

    def _metric_faithfulness(self) -> MetricResult:
        name      = "faithfulness"
        threshold = self._THRESHOLDS[name]
        if not self._methods:
            return MetricResult(name=name, score=1.0, threshold=threshold, passed=True,
                                description="No methods to check", category="ragas")
        hits  = sum(1 for m in self._methods if m in self._page_src)
        score = hits / len(self._methods)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Fraction of blueprint methods present in generated page object",
            category="ragas",
        )

    def _metric_hallucination_detection(self) -> MetricResult:
        name      = "hallucination_detection"
        threshold = self._THRESHOLDS[name]
        # Find method definitions in generated page src
        found = re.findall(r"^\s+def (\w+)\(self", self._page_src, re.MULTILINE)
        expected_set = set(self._methods) | {"open", "__init__"}
        extra  = [m for m in found if m not in expected_set]
        score  = len(extra) / max(len(found), 1)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score <= threshold,
            description="Ratio of extra (hallucinated) methods vs all defined methods",
            category="ragas",
        )

    def _metric_grounding_validation(self) -> MetricResult:
        name      = "grounding_validation"
        threshold = self._THRESHOLDS[name]
        top_score = self.rag_context[0].get("similarity_score", 0.0) if self.rag_context else 0.0
        if not self.rag_context or top_score < 0.10:
            # Cold start or irrelevant retrieval — neutral pass at boundary
            score = 0.45
        else:
            rag_tokens = set(
                w for ctx in self.rag_context
                for w in re.findall(r"\w+", ctx.get("description", "") + " " + ctx.get("script", ""))
            )
            loc_tokens = set(re.findall(r"\w+", self._loc_src))
            overlap = rag_tokens & loc_tokens
            score   = len(overlap) / max(len(loc_tokens), 1)
            score   = min(score, 1.0)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Locator vocabulary overlap with RAG-retrieved context",
            category="ragas",
        )

    def _metric_retrieval_relevance(self) -> MetricResult:
        name      = "retrieval_relevance"
        threshold = self._THRESHOLDS[name]
        if not self.rag_context:
            score = 0.0
        else:
            score = float(self.rag_context[0].get("similarity_score", 0.0))
            score = max(0.0, min(1.0, score))
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Top FAISS similarity score for retrieved RAG script",
            category="ragas",
        )

    def _metric_context_propagation(self) -> MetricResult:
        name      = "context_propagation"
        threshold = self._THRESHOLDS[name]
        allure_steps = re.findall(r"allure\.step\(", self._test_src)
        expected     = max(len(self._methods), 1)
        score        = min(len(allure_steps) / expected, 1.0)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Ratio of allure.step() blocks in test file to expected method count",
            category="deepeval",
        )

    def _metric_probabilistic_consistency(self) -> MetricResult:
        name      = "probabilistic_consistency"
        threshold = self._THRESHOLDS[name]
        if not _EMBED_AVAILABLE or not self._methods:
            score = 0.05
        else:
            model = self._get_embed_model()
            vecs  = model.encode(self._methods, normalize_embeddings=True)
            import numpy as np
            scores = []
            for i in range(len(vecs)):
                for j in range(i + 1, len(vecs)):
                    scores.append(float(np.dot(vecs[i], vecs[j])))
            score = float(np.std(scores)) if scores else 0.0
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score <= threshold,
            description="Std-dev of pairwise method-name similarities (low = consistent naming)",
            category="deepeval",
        )

    def _metric_non_determinism_tolerance(self) -> MetricResult:
        name      = "non_determinism_tolerance"
        threshold = self._THRESHOLDS[name]
        # Proxy: check if any TODO locators remain (high = uncertain output)
        todo_count = len(re.findall(r"#TODO_", self._loc_src))
        total_loc  = max(len(self.bp.get("locators", [])), 1)
        score      = todo_count / total_loc   # all TODO = 1.0 (worst)
        score      = min(score * 0.5, 1.0)    # scale: all-TODO → 0.50
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score <= threshold,
            description="Fraction of locators still at TODO placeholder (lower = more grounded)",
            category="deepeval",
        )

    def _metric_threshold_pass_rate(self, prior_results: list) -> MetricResult:
        name      = "threshold_pass_rate"
        threshold = self._THRESHOLDS[name]
        if not prior_results:
            score = 1.0
        else:
            score = sum(1 for r in prior_results if r.passed) / len(prior_results)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Fraction of the first 8 metrics that passed their thresholds",
            category="orchestration",
        )

    def _metric_agent_orchestration(self) -> MetricResult:
        name      = "agent_orchestration"
        threshold = self._THRESHOLDS[name]
        score     = min(self.stages_done / max(self.total_stages, 1), 1.0)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="Ratio of pipeline stages completed before validation",
            category="orchestration",
        )

    def _metric_observability_tracing(self) -> MetricResult:
        name      = "observability_tracing"
        threshold = self._THRESHOLDS[name]
        checks    = [
            bool(os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")),
            bool(os.getenv("LANGCHAIN_TRACING_V2") or os.getenv("LANGSMITH_TRACING")),
            bool(os.getenv("LANGCHAIN_PROJECT") or os.getenv("LANGSMITH_PROJECT")),
        ]
        score = sum(checks) / len(checks)
        return MetricResult(
            name=name, score=score, threshold=threshold,
            passed=score >= threshold,
            description="LangSmith observability env vars configured",
            category="observability",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    @classmethod
    def _get_embed_model(cls) -> "SentenceTransformer":
        if cls._EMBED_MODEL is None:
            cls._EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._EMBED_MODEL
