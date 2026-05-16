"""
pipeline_reporter.py — Layer 10 (Reporting) of the AI pipeline

Writes a structured JSON report to report/analytics/ and prints a
human-readable console summary with pass/fail symbols per metric.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ai.auto_generator.ai_validator import ValidationReport
    from ai.auto_generator.test_executor import ExecutionResult


REPORT_DIR = Path("report/analytics")
PASS = "✅"
FAIL = "❌"
WARN = "⚠️ "


class PipelineReporter:

    def __init__(self, test_case: dict, generated: dict):
        self.test_case = test_case
        self.generated = generated

    # ── Public API ─────────────────────────────────────────────────────────────

    def report(
        self,
        validation: "ValidationReport",
        execution:  Optional["ExecutionResult"] = None,
    ) -> str:
        payload = self._build_payload(validation, execution)
        path    = self._write_json(payload)
        self._print_console(payload)
        return path

    # ── JSON report ────────────────────────────────────────────────────────────

    def _build_payload(self, v: "ValidationReport", e: Optional["ExecutionResult"]) -> dict:
        metrics_data = [
            {
                "name":        m.name,
                "score":       round(m.score, 4),
                "threshold":   m.threshold,
                "passed":      m.passed,
                "description": m.description,
                "category":    m.category,
            }
            for m in v.metrics
        ]

        exec_data: dict = {}
        if e:
            exec_data = {
                "status":          "PASS" if e.passed else "FAIL",
                "returncode":      e.returncode,
                "attempts":        e.attempts,
                "healing_applied": e.healed,
                "errors":          e.errors[:10],
            }

        return {
            "pipeline":      "AI Auto-Generator",
            "test_case":     self.test_case.get("test_case_id", "unknown"),
            "module":        self.test_case.get("module", ""),
            "timestamp":     datetime.utcnow().isoformat() + "Z",
            "generated_files": self.generated,
            "ai_validation": {
                "overall_pass":  v.overall_pass,
                "passed_count":  v.passed_count,
                "failed_count":  v.failed_count,
                "summary":       v.summary,
                "recommendations": v.recommendations,
                "metrics":       metrics_data,
            },
            "execution": exec_data,
            "summary": self._build_summary(v, e),
        }

    def _write_json(self, payload: dict) -> str:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        ts   = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        tc   = payload["test_case"].replace(" ", "_")
        path = REPORT_DIR / f"pipeline_report_{tc}_{ts}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(path)

    # ── Console output ─────────────────────────────────────────────────────────

    def _print_console(self, payload: dict) -> None:
        v = payload["ai_validation"]
        e = payload.get("execution", {})

        width = 64
        print(f"\n{'═' * width}")
        print(f"  AI Pipeline Report — {payload['test_case']}")
        print(f"{'═' * width}")
        print(f"\n  {'AI VALIDATION':─<54}")

        for m in v["metrics"]:
            sym   = PASS if m["passed"] else FAIL
            score = f"{m['score']:.2f}"
            thr   = f"(≥{m['threshold']:.2f})" if m["threshold"] <= 0.5 or m["name"] not in (
                "hallucination_detection", "probabilistic_consistency", "non_determinism_tolerance"
            ) else f"(≤{m['threshold']:.2f})"
            print(f"  {sym} {m['name']:<38} {score} {thr}")

        print(f"\n  Validation : {PASS if v['overall_pass'] else FAIL} "
              f"{v['passed_count']}/{v['passed_count'] + v['failed_count']} passed")

        if v["recommendations"]:
            print(f"\n  {WARN}Recommendations:")
            for rec in v["recommendations"][:5]:
                print(f"     • {rec}")

        if e:
            sym = PASS if e.get("status") == "PASS" else FAIL
            print(f"\n  {'EXECUTION':─<54}")
            print(f"  {sym} Status  : {e.get('status', 'n/a')}")
            print(f"  {'':3}Attempts : {e.get('attempts', 1)}")
            if e.get("healing_applied"):
                print(f"  {WARN}Auto-heal was applied on attempt 2")
            if e.get("errors"):
                print(f"  Errors:")
                for err in e["errors"][:3]:
                    print(f"     {err}")

        print(f"\n  {'SUMMARY':─<54}")
        print(f"  {payload['summary']}")
        print(f"{'═' * width}\n")

    @staticmethod
    def _build_summary(v: "ValidationReport", e: Optional["ExecutionResult"]) -> str:
        parts = [v.summary]
        if e is None:
            parts.append("Execution skipped (AI validation failed).")
        elif e.passed:
            heal = " (with auto-heal)" if e.healed else ""
            parts.append(f"Test PASSED{heal} in {e.attempts} attempt(s).")
        else:
            parts.append(f"Test FAILED after {e.attempts} attempt(s). Check errors in report.")
        return " ".join(parts)
