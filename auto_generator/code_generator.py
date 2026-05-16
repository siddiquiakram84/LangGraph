import os
from pathlib import Path


class CodeGenerator:
    """
    Generates POM-based automation files inside automation-project.
    Uses placeholder locators.
    """

    def __init__(self, blueprint: dict):
        self.blueprint = blueprint

        self.project_root = Path("automation-project")
        self.pages_path = self.project_root / "src/pages"
        self.locators_path = self.project_root / "src/locators"
        self.tests_path = self.project_root / "tests"

    def generate(self):
        self._generate_locator_file()
        self._generate_page_file()
        self._generate_test_file()

    # ----------------------------
    # Locator File
    # ----------------------------
    def _generate_locator_file(self):
        file_name = f"{self.blueprint['locator_file']}.py"
        file_path = self.locators_path / file_name

        locator_constants = "\n".join(
            [f"{loc} = ('ID', 'TODO_{loc}')" for loc in self.blueprint["locators"]]
        )

        content = f"""from selenium.webdriver.common.by import By


class {self.blueprint['locator_file'].title().replace('_', '')}:

{locator_constants}
"""

        self._write_file(file_path, content)

    # ----------------------------
    # Page File
    # ----------------------------
    def _generate_page_file(self):
        file_name = f"{self.blueprint['page_name']}.py"
        file_path = self.pages_path / file_name

        methods = ""

        for method in self.blueprint["methods"]:
            locator_name = method["field_name"].upper().replace(" ", "_") + "_LOCATOR"

            action_body = ""

            if method["action_type"] in ["enter_text"]:
                action_body = f"""
        element = self.driver.find_element(*self.locators.{locator_name})
        element.clear()
        element.send_keys(value)
"""
            else:
                action_body = f"""
        element = self.driver.find_element(*self.locators.{locator_name})
        element.click()
"""

            method_block = f"""
    def {method['method_name']}(self, value=None):
{action_body}
"""
            methods += method_block

        content = f"""from src.pages.base_page import BasePage
from src.locators.{self.blueprint['locator_file']} import {self.blueprint['locator_file'].title().replace('_', '')}


class {self.blueprint['page_name'].title().replace('_', '')}(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.locators = {self.blueprint['locator_file'].title().replace('_', '')}

{methods}
"""

        self._write_file(file_path, content)

    # ----------------------------
    # Test File
    # ----------------------------
    def _generate_test_file(self):
        file_name = f"{self.blueprint['test_file']}.py"
        file_path = self.tests_path / file_name

        page_class = self.blueprint['page_name'].title().replace('_', '')

        method_calls = "\n".join(
            [f"    page.{method['method_name']}()" for method in self.blueprint["methods"]]
        )

        content = f"""import pytest
from src.pages.{self.blueprint['page_name']} import {page_class}


@pytest.mark.smoke
def test_{self.blueprint['page_name']}(driver):
    page = {page_class}(driver)

{method_calls}
"""

        self._write_file(file_path, content)

    # ----------------------------
    # Write Utility
    # ----------------------------
    def _write_file(self, path, content):
        os.makedirs(path.parent, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        print(f"Generated: {path}")
