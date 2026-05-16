"""
Layer 5 — PAGE OBJECT: DynamicControlsPage
Represents the-internet.herokuapp.com/dynamic_controls.
Demonstrates async UI interactions — checkbox add/remove, input enable/disable.
"""
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.settings import Settings


class DynamicControlsPage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────────────
    CHECKBOX           = "#checkbox"
    CHECKBOX_FORM      = "#checkbox-example"
    TOGGLE_BTN         = "#checkbox-example button"
    INPUT_FIELD        = "#input-example input"
    INPUT_TOGGLE_BTN   = "#input-example button"
    LOADING_BAR        = "#loading-bar"
    MESSAGE            = "#message"

    URL = f"{Settings.BASE_URL}/dynamic_controls"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Open Dynamic Controls page")
    def open(self) -> "DynamicControlsPage":
        self.navigate(self.URL)
        return self

    # ── Checkbox actions ──────────────────────────────────────────────────────

    @allure.step("Click toggle checkbox button (Remove/Add)")
    def click_toggle_checkbox(self) -> "DynamicControlsPage":
        self.click(self.TOGGLE_BTN, "Remove/Add button")
        return self

    @allure.step("Wait for checkbox to be removed")
    def wait_for_checkbox_removed(self) -> "DynamicControlsPage":
        self.page.wait_for_selector(self.CHECKBOX, state="detached", timeout=10000)
        return self

    @allure.step("Wait for checkbox to be added back")
    def wait_for_checkbox_added(self) -> "DynamicControlsPage":
        self.page.wait_for_selector(self.CHECKBOX, state="visible", timeout=10000)
        return self

    @allure.step("Verify toggle message: '{expected_text}'")
    def verify_message(self, expected_text: str) -> "DynamicControlsPage":
        self.expect_visible(self.MESSAGE)
        self.expect_text(self.MESSAGE, expected_text)
        return self

    def is_checkbox_visible(self) -> bool:
        return self.is_visible(self.CHECKBOX)

    # ── Input enable/disable actions ─────────────────────────────────────────

    @allure.step("Click toggle input button (Enable/Disable)")
    def click_toggle_input(self) -> "DynamicControlsPage":
        self.click(self.INPUT_TOGGLE_BTN, "Enable/Disable button")
        return self

    @allure.step("Wait for input to be enabled")
    def wait_for_input_enabled(self) -> "DynamicControlsPage":
        self.page.wait_for_selector(
            f"{self.INPUT_FIELD}:not([disabled])", timeout=10000
        )
        return self

    @allure.step("Wait for input to be disabled")
    def wait_for_input_disabled(self) -> "DynamicControlsPage":
        self.page.wait_for_selector(
            f"{self.INPUT_FIELD}[disabled]", timeout=10000
        )
        return self

    def is_input_enabled(self) -> bool:
        return self.page.locator(self.INPUT_FIELD).is_enabled()

    @allure.step("Type '{text}' into input field")
    def type_into_input(self, text: str) -> "DynamicControlsPage":
        self.fill(self.INPUT_FIELD, text, "Dynamic input")
        return self
