"""
ai/auto_heal/framework/config.py
Shared utilities for the SmartDriver healing framework.
"""
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def log_healing_report(report: dict) -> None:
    """Write a healing report to report/healing/ and log to console."""
    report_dir = Path("report/healing/healing_reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    import time
    path = report_dir / f"healing_{int(time.time())}.json"
    path.write_text(json.dumps(report, indent=2, default=str))
    logger.info(f"Healing report written: {path}")
