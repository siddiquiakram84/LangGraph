"""
Layer 3 — UTILS: PDFHelper
Writes per-test JSON summaries to report/playwright/pdf/.
Swap write_summary() body for reportlab/weasyprint to get real PDFs.
"""
import json
from datetime import datetime
from config.settings import Settings


class PDFHelper:

    @staticmethod
    def write_summary(test_name: str, status: str, steps: list[str], error: str = "") -> str:
        Settings.PDF_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        record = {
            "test": test_name,
            "status": status,
            "timestamp": ts,
            "steps": steps,
            "error": error,
        }
        path = Settings.PDF_DIR / f"{test_name}_{ts}.json"
        path.write_text(json.dumps(record, indent=2))
        return str(path)
