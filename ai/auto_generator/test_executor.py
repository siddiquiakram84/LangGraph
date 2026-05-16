"""
test_executor.py — Layer 8 (Execution) of the AI pipeline

Runs the generated pytest test in automation-project/ context.
If Playwright raises a TimeoutError on a #TODO_ locator, the executor
performs a single auto-heal pass: it patches the locator file with a
heuristic CSS selector and re-runs the test.
"""
from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class ExecutionResult:
    passed:   bool
    returncode: int
    stdout:   str
    stderr:   str
    healed:   bool  = False
    attempts: int   = 1
    errors:   List[str] = field(default_factory=list)


# ── Heuristic selector map ────────────────────────────────────────────────────

_SELECTOR_HINTS: dict[str, list[str]] = {
    "search":    ["#search", "[name='q']", "input[type='search']", "[aria-label*='search' i]"],
    "username":  ["#username", "[name='username']", "input[autocomplete='username']"],
    "password":  ["#password", "[name='password']", "input[type='password']"],
    "email":     ["#email", "[name='email']", "input[type='email']"],
    "login":     ["button[type='submit']", "#login-btn", ".login-btn"],
    "submit":    ["button[type='submit']", "input[type='submit']"],
    "button":    ["button[type='submit']", ".btn-primary", "button.action"],
    "add":       ["#add", ".add-to-cart", "button[data-action='add']"],
    "cart":      ["#cart", ".cart-icon", "[aria-label*='cart' i]"],
    "checkout":  ["#checkout", ".checkout-btn", "button[data-action='checkout']"],
    "click":     ["button", ".btn", "a.action-link"],
    "input":     ["input[type='text']", "textarea", ".input-field"],
    "name":      ["[name='name']", "#name", "input[placeholder*='name' i]"],
    "query":     ["input[type='search']", "#q", "[name='query']"],
    "box":       ["input[type='text']", "textarea"],
}


def _heuristic_selector(method_name: str) -> str:
    lower = method_name.lower()
    for keyword, selectors in _SELECTOR_HINTS.items():
        if keyword in lower:
            return selectors[0]
    return "button, input[type='submit']"


# ── Executor ──────────────────────────────────────────────────────────────────

class TestExecutor:
    """
    Parameters
    ----------
    test_path    : absolute path to the generated test file
    locator_path : absolute path to the generated locator file
    project_root : automation-project/ directory (conftest.py lives here)
    """

    def __init__(
        self,
        test_path:    str,
        locator_path: str,
        project_root: str = "automation-project",
    ):
        self.test_path    = Path(test_path)
        self.locator_path = Path(locator_path)
        self.project_root = Path(project_root)

    def run(self) -> ExecutionResult:
        result = self._execute()
        if not result.passed and self._has_todo_locator_error(result.stdout + result.stderr):
            healed = self._heal_locators(result.stdout + result.stderr)
            if healed:
                result = self._execute()
                result.healed   = True
                result.attempts = 2
        return result

    # ── Private ───────────────────────────────────────────────────────────────

    def _execute(self) -> ExecutionResult:
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_path),
            "-v", "--tb=short", "--no-header",
        ]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(self.project_root),
        )
        passed = proc.returncode == 0
        errors = self._parse_errors(proc.stdout + proc.stderr)
        return ExecutionResult(
            passed=passed,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            errors=errors,
        )

    @staticmethod
    def _has_todo_locator_error(output: str) -> bool:
        return bool(re.search(r"#TODO_", output) or
                    re.search(r"TimeoutError|Locator.*exceeded", output, re.IGNORECASE))

    @staticmethod
    def _parse_errors(output: str) -> List[str]:
        errors = []
        for line in output.splitlines():
            if any(kw in line for kw in ("FAILED", "ERROR", "TimeoutError", "AssertionError")):
                errors.append(line.strip())
        return errors

    def _heal_locators(self, output: str) -> bool:
        if not self.locator_path.exists():
            return False

        src = self.locator_path.read_text()
        # Find all TODO locators: #TODO_<name>
        todo_pattern = re.compile(r'#TODO_(\w+)')
        todos = todo_pattern.findall(src)
        if not todos:
            return False

        patched = src
        for todo_name in todos:
            new_selector = _heuristic_selector(todo_name)
            patched = patched.replace(f'"#TODO_{todo_name}"', f'"{new_selector}"')

        self.locator_path.write_text(patched)
        print(f"[TestExecutor] Auto-healed {len(todos)} locator(s) in {self.locator_path.name}")
        return True
