"""
auto_generator/file_writer.py

Writes generated Playwright Python files to the automation-project.
Handles directory creation, backup of existing files, and
appending to existing test files rather than overwriting.
"""
import os
import shutil
import time
from pathlib import Path


class FileWriter:

    def __init__(self):
        self.pages_dir    = Path("automation-project/pages/generated")
        self.locators_dir = Path("automation-project/locators/generated")
        self.tests_dir    = Path("automation-project/tests/ui/generated")

    def write(self, files: dict) -> dict:
        """
        files = {
          "page":    (filename, content),
          "locator": (filename, content),
          "test":    (filename, content),
        }
        Returns dict of absolute paths that were written.
        """
        written = {}
        mapping = {
            "page":    self.pages_dir,
            "locator": self.locators_dir,
            "test":    self.tests_dir,
        }

        for key, (filename, content) in files.items():
            target_dir = mapping[key]
            target_dir.mkdir(parents=True, exist_ok=True)

            init_file = target_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")

            target_path = target_dir / filename

            if target_path.exists():
                backup = target_path.with_suffix(f".bak_{int(time.time())}.py")
                shutil.copy(target_path, backup)

            target_path.write_text(content, encoding="utf-8")
            written[key] = str(target_path.resolve())
            print(f"[FileWriter] wrote {key}: {target_path}")

        return written
