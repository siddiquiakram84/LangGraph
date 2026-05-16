"""
Layer 5 — PAGE OBJECT: BasePage
Root of the page hierarchy. Wraps Playwright Page with Allure steps,
screenshot capture, and structured logging. All page classes extend this.

Interview talking point:
  "BasePage follows the Page Object Model pattern. Tests never call
  page.locator() directly — they go through typed page methods, which
  makes tests readable and locators easy to maintain in one place."
"""
import allure
from playwright.sync_api import Page, expect
from utils.logger import get_logger
from utils.screenshot_helper import ScreenshotHelper
from utils.allure_helper import AllureHelper

logger = get_logger(__name__)


class BasePage:

    def __init__(self, page: Page):
        self.page = page

    # ── Navigation ────────────────────────────────────────────────────────────

    def navigate(self, url: str):
        with allure.step(f"Navigate to {url}"):
            logger.info(f"→ {url}")
            self.page.goto(url)
            self.page.wait_for_load_state("domcontentloaded")

    # ── Interactions ─────────────────────────────────────────────────────────

    def click(self, selector: str, label: str = ""):
        with allure.step(f"Click '{label or selector}'"):
            self.page.locator(selector).click()

    def fill(self, selector: str, value: str, label: str = ""):
        with allure.step(f"Fill '{label or selector}' → '{value}'"):
            self.page.locator(selector).fill(value)

    def press(self, selector: str, key: str):
        self.page.locator(selector).press(key)

    def select_option(self, selector: str, value: str):
        self.page.locator(selector).select_option(value)

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_text(self, selector: str) -> str:
        return self.page.locator(selector).inner_text().strip()

    def is_visible(self, selector: str) -> bool:
        return self.page.locator(selector).is_visible()

    def get_title(self) -> str:
        return self.page.title()

    # ── Assertions ────────────────────────────────────────────────────────────

    def expect_visible(self, selector: str, label: str = ""):
        with allure.step(f"Assert visible: {label or selector}"):
            expect(self.page.locator(selector)).to_be_visible()

    def expect_text(self, selector: str, text: str):
        with allure.step(f"Assert text contains: '{text}'"):
            expect(self.page.locator(selector)).to_contain_text(text)

    def expect_title(self, title: str):
        with allure.step(f"Assert page title: '{title}'"):
            expect(self.page).to_have_title(title)

    def expect_url(self, pattern: str):
        with allure.step(f"Assert URL contains: '{pattern}'"):
            expect(self.page).to_have_url(pattern)

    # ── Screenshots ───────────────────────────────────────────────────────────

    def take_screenshot(self, name: str = "screenshot") -> bytes:
        data = ScreenshotHelper.capture(self.page, name)
        AllureHelper.attach_screenshot(data, name)
        return data
