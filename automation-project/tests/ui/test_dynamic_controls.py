"""
Layer 6 — TEST: Dynamic Controls Interaction
Target: https://the-internet.herokuapp.com/dynamic_controls

Demonstrates all 7 layers:
  L1 Config      — Settings (BASE_URL, timeouts)
  L2 Core        — DriverFactory via conftest fixtures
  L3 Utils       — get_logger, AllureHelper, ScreenshotHelper
  L4 Data        — TestData loaded from data/ui/dynamic_controls.json
  L5 Pages       — DynamicControlsPage (extends BasePage)
  L6 Test        — This file (two independent test classes)
  L7 Reporting   — @allure decorators + conftest auto-screenshot hook

Interview talking point:
  "Dynamic Controls tests cover async UI patterns — we wait for DOM
  mutations (element detach/attach, attribute changes) rather than fixed
  sleeps, which makes tests fast and resilient."
"""
import json
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from pages.dynamic_controls_page import DynamicControlsPage
from utils.allure_helper import AllureHelper
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Layer 4: Test data ────────────────────────────────────────────────────────
_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "ui" / "dynamic_controls.json"
_DATA = json.loads(_DATA_FILE.read_text())


# ── Layer 6: Test classes ─────────────────────────────────────────────────────

@allure.suite("UI — Dynamic Controls Suite")
@allure.feature("Checkbox Toggle")
class TestCheckboxToggle:
    """Verify that the checkbox can be removed and re-added via AJAX."""

    @allure.story("Checkbox can be removed from the page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_checkbox(self, page: Page):
        with allure.step("Load test data"):
            AllureHelper.attach_json(_DATA, "Dynamic Controls Config")

        with allure.step("Open Dynamic Controls page"):
            dcp = DynamicControlsPage(page).open()
            assert dcp.is_checkbox_visible(), "Checkbox should exist on page load"
            logger.info("Checkbox confirmed visible before remove")

        with allure.step("Click Remove and wait for checkbox to disappear"):
            dcp.click_toggle_checkbox().wait_for_checkbox_removed()
            assert not dcp.is_checkbox_visible(), "Checkbox should be gone after Remove"
            logger.info("Checkbox successfully removed")

        with allure.step("Verify status message"):
            dcp.verify_message(_DATA["removed_message"])
            AllureHelper.attach_text("Checkbox removed and message verified", "Result")

    @allure.story("Checkbox can be re-added to the page")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_checkbox_back(self, page: Page):
        with allure.step("Open page and remove checkbox first"):
            dcp = DynamicControlsPage(page).open()
            dcp.click_toggle_checkbox().wait_for_checkbox_removed()
            assert not dcp.is_checkbox_visible()

        with allure.step("Click Add and wait for checkbox to reappear"):
            dcp.click_toggle_checkbox().wait_for_checkbox_added()
            assert dcp.is_checkbox_visible(), "Checkbox should reappear after Add"
            logger.info("Checkbox successfully added back")

        with allure.step("Verify status message"):
            dcp.verify_message(_DATA["added_message"])
            AllureHelper.attach_text("Checkbox re-added and message verified", "Result")


@allure.suite("UI — Dynamic Controls Suite")
@allure.feature("Input Enable / Disable")
class TestInputToggle:
    """Verify input field can be enabled and disabled via AJAX."""

    @allure.story("Input field can be enabled for user input")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_enable_input(self, page: Page):
        with allure.step("Open Dynamic Controls page"):
            dcp = DynamicControlsPage(page).open()
            assert not dcp.is_input_enabled(), "Input should start disabled"
            logger.info("Confirmed input is disabled on load")

        with allure.step("Click Enable and wait for input to become active"):
            dcp.click_toggle_input().wait_for_input_enabled()
            assert dcp.is_input_enabled(), "Input should be enabled after clicking Enable"
            logger.info("Input successfully enabled")

        with allure.step("Type text into enabled input and verify message"):
            dcp.type_into_input("AI automation test")
            dcp.verify_message(_DATA["enabled_message"])
            AllureHelper.attach_text("Input enabled and accepts text input", "Result")

    @allure.story("Input field can be disabled after being enabled")
    @allure.severity(allure.severity_level.NORMAL)
    def test_disable_input_after_enable(self, page: Page):
        with allure.step("Enable input first"):
            dcp = DynamicControlsPage(page).open()
            dcp.click_toggle_input().wait_for_input_enabled()
            assert dcp.is_input_enabled()

        with allure.step("Click Disable and wait for input to become inactive"):
            dcp.click_toggle_input().wait_for_input_disabled()
            assert not dcp.is_input_enabled(), "Input should be disabled after clicking Disable"
            logger.info("Input successfully disabled")

        with allure.step("Verify disabled message"):
            dcp.verify_message(_DATA["disabled_message"])
            AllureHelper.attach_text("Input disabled and message verified", "Result")
