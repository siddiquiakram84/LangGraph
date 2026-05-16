"""
auto_generator/code_generator.py

Generates Playwright Python POM files from a page blueprint.
Output: locator file, page object file, pytest test file.
Uses FileWriter so all output goes to automation-project/src/.../generated/
"""
from ai.auto_generator.file_writer import FileWriter


class CodeGenerator:

    def __init__(self, blueprint: dict, rag_context: list = None):
        """
        blueprint   : dict from PagePlanner.plan()
        rag_context : list of similar past scripts from FAISSScriptStore (optional)
        """
        self.bp  = blueprint
        self.ctx = rag_context or []
        self.fw  = FileWriter()

    def generate(self) -> dict:
        """Generate all three files and return written paths."""
        locator_file  = self._build_locator_file()
        page_file     = self._build_page_file()
        test_file     = self._build_test_file()

        return self.fw.write({
            "locator": (f"{self.bp['locator_file']}.py",  locator_file),
            "page":    (f"{self.bp['page_name']}.py",     page_file),
            "test":    (f"{self.bp['test_file']}.py",     test_file),
        })

    # ── Locator file ────────────────────────────────────────────────────────

    def _build_locator_file(self) -> str:
        class_name = self._to_class(self.bp["locator_file"])
        lines = [f'class {class_name}:']
        for loc in self.bp["locators"]:
            # Generate a CSS selector placeholder — human fills real value
            lines.append(f'    {loc} = ("#TODO_{loc.lower()}",)')
        return "\n".join(lines) + "\n"

    # ── Page object file ─────────────────────────────────────────────────────

    def _build_page_file(self) -> str:
        page_class   = self._to_class(self.bp["page_name"])
        loc_class    = self._to_class(self.bp["locator_file"])
        loc_module   = f"src.locators.generated.{self.bp['locator_file']}"

        methods = []
        for m in self.bp["methods"]:
            loc_key = m["field_name"].upper().replace(" ", "_") + "_LOCATOR"
            if m["action_type"] == "enter_text":
                body = (
                    f'        self.page.locator(self.loc.{loc_key}[0]).fill(value)'
                )
            else:
                body = (
                    f'        self.page.locator(self.loc.{loc_key}[0]).click()'
                )
            methods.append(
                f'    def {m["method_name"]}(self, value: str = ""):\n{body}'
            )

        rag_comment = ""
        if self.ctx:
            rag_comment = (
                "# RAG context: similar script retrieved from FAISS store\n"
                f"# Source: {self.ctx[0].get('description', 'n/a')} "
                f"(score={self.ctx[0].get('similarity_score', 0):.2f})\n\n"
            )

        return (
            f"{rag_comment}"
            f"from {loc_module} import {loc_class}\n\n\n"
            f"class {page_class}:\n\n"
            f"    def __init__(self, page):\n"
            f"        self.page = page\n"
            f"        self.loc  = {loc_class}\n\n"
            + "\n\n".join(methods) + "\n"
        )

    # ── Test file ────────────────────────────────────────────────────────────

    def _build_test_file(self) -> str:
        page_class  = self._to_class(self.bp["page_name"])
        page_module = f"src.pages.generated.{self.bp['page_name']}"
        fixture_var = self.bp["page_name"]

        method_calls = "\n".join(
            [f'    po.{m["method_name"]}()' for m in self.bp["methods"]]
        )

        return (
            f"import allure\n"
            f"import pytest\n"
            f"from playwright.sync_api import Page\n"
            f"from {page_module} import {page_class}\n\n\n"
            f"@allure.suite('Generated — {self.bp['page_name']}')\n"
            f"@allure.feature('{self.bp['page_name'].replace('_', ' ').title()}')\n"
            f"def test_{self.bp['page_name']}(page: Page):\n"
            f"    po = {page_class}(page)\n"
            f"{method_calls}\n"
        )

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _to_class(snake: str) -> str:
        return "".join(w.title() for w in snake.split("_"))
