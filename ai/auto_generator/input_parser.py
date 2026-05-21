"""
ai/auto_generator/input_parser.py

Parses manual test case files from input_manual_test_case/ into the
standard test-case dict that the rest of the pipeline expects.

Supported formats:
  .json          — structured JSON (existing format)
  .csv           — CSV (Excel-compatible, 6-column format)
  .xlsx          — Excel workbook (requires openpyxl)
  .txt / .text   — structured plain-text (KEY: VALUE / STEP: / EXPECTED:)

Standard output dict:
  {
    "test_case_id": str,
    "module":       str,
    "base_url":     str,
    "steps": [
      {"tc_msg_action": str, "tc_msg_expected": str},
      ...
    ]
  }
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import List


class InputParser:

    @staticmethod
    def parse(file_path: str | Path) -> dict:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".json":
            return InputParser._parse_json(path)
        elif suffix == ".csv":
            return InputParser._parse_csv(path)
        elif suffix == ".xlsx":
            return InputParser._parse_xlsx(path)
        elif suffix in (".txt", ".text"):
            return InputParser._parse_text(path)
        else:
            raise ValueError(
                f"Unsupported file format '{suffix}'. "
                f"Supported: .json, .csv, .xlsx, .txt"
            )

    @staticmethod
    def scan_directory(directory: str | Path) -> List[Path]:
        """Return all parseable files found recursively under directory."""
        root = Path(directory)
        found = []
        for ext in ("*.json", "*.csv", "*.xlsx", "*.txt", "*.text"):
            found.extend(root.rglob(ext))
        return sorted(found)

    # ── Format parsers ────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(path: Path) -> dict:
        data = json.loads(path.read_text(encoding="utf-8"))
        InputParser._validate(data, path)
        return data

    @staticmethod
    def _parse_csv(path: Path) -> dict:
        """
        Expected CSV columns (header row required):
          test_case_id, module, base_url, step_action, step_expected

        All rows with the same test_case_id belong to one test case.
        """
        rows = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

        if not rows:
            raise ValueError(f"CSV file is empty: {path}")

        first = rows[0]
        steps = [
            {
                "tc_msg_action":   r.get("step_action", "").strip(),
                "tc_msg_expected": r.get("step_expected", "").strip(),
            }
            for r in rows
            if r.get("step_action", "").strip()
        ]

        return {
            "test_case_id": first.get("test_case_id", path.stem).strip(),
            "module":       first.get("module",        path.stem).strip(),
            "base_url":     first.get("base_url",      "").strip(),
            "steps":        steps,
        }

    @staticmethod
    def _parse_xlsx(path: Path) -> dict:
        """
        Excel workbook (.xlsx) — same column layout as CSV.
        Sheet 1 is used; header row on row 1.
        Requires openpyxl (pip install openpyxl).
        """
        try:
            import openpyxl
        except ImportError:
            raise ImportError(
                "openpyxl is required to parse .xlsx files. "
                "Install with: pip install openpyxl"
            )

        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows_iter = ws.iter_rows(values_only=True)
        headers = [str(h).strip().lower() if h else "" for h in next(rows_iter)]

        rows = []
        for row in rows_iter:
            rows.append(dict(zip(headers, (str(c).strip() if c else "" for c in row))))
        wb.close()

        if not rows:
            raise ValueError(f"Excel file has no data rows: {path}")

        first = rows[0]
        steps = [
            {
                "tc_msg_action":   r.get("step_action",   "").strip(),
                "tc_msg_expected": r.get("step_expected",  "").strip(),
            }
            for r in rows
            if r.get("step_action", "").strip()
        ]

        return {
            "test_case_id": first.get("test_case_id", path.stem).strip(),
            "module":       first.get("module",        path.stem).strip(),
            "base_url":     first.get("base_url",      "").strip(),
            "steps":        steps,
        }

    @staticmethod
    def _parse_text(path: Path) -> dict:
        """
        Plain-text format:
          TEST_CASE_ID: TC_XXX
          MODULE: module_name
          BASE_URL: https://...
          ---
          STEP: action text
          EXPECTED: expected result
          ---
          STEP: next action
          EXPECTED: next expected
        """
        text = path.read_text(encoding="utf-8")
        meta: dict = {}
        steps: list = []

        header_re = re.compile(
            r"^(TEST_CASE_ID|MODULE|BASE_URL)\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE
        )
        for m in header_re.finditer(text):
            meta[m.group(1).lower()] = m.group(2).strip()

        blocks = re.split(r"^---+\s*$", text, flags=re.MULTILINE)
        for block in blocks[1:]:  # skip header block
            step_m    = re.search(r"^STEP\s*:\s*(.+)$",     block, re.IGNORECASE | re.MULTILINE)
            expect_m  = re.search(r"^EXPECTED\s*:\s*(.+)$", block, re.IGNORECASE | re.MULTILINE)
            if step_m:
                steps.append({
                    "tc_msg_action":   step_m.group(1).strip(),
                    "tc_msg_expected": expect_m.group(1).strip() if expect_m else "",
                })

        # Fallback: free-form file — treat each non-empty, non-header line as a step
        if not steps:
            header_keys = {"test_case_id", "module", "base_url"}
            for line in text.splitlines():
                line = line.strip()
                if not line:
                    continue
                key = line.split(":")[0].strip().lower()
                if key in header_keys or line.startswith("---"):
                    continue
                steps.append({"tc_msg_action": line, "tc_msg_expected": ""})

        return {
            "test_case_id": meta.get("test_case_id", path.stem),
            "module":       meta.get("module",        path.stem),
            "base_url":     meta.get("base_url",      ""),
            "steps":        steps,
        }

    # ── Validation ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate(data: dict, path: Path) -> None:
        required = ("test_case_id", "module", "steps")
        for key in required:
            if key not in data:
                raise ValueError(
                    f"Missing required key '{key}' in test case file: {path}"
                )
        if not isinstance(data["steps"], list) or not data["steps"]:
            raise ValueError(f"'steps' must be a non-empty list in: {path}")
