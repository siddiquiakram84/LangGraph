"""
Layer 5 — PAGE OBJECT: HomePage
Represents the-internet.herokuapp.com home page.
Locators are CSS selectors defined as class-level constants.

Interview talking point:
  "I keep all selectors in the page class, not in tests. When Amazon
  changes a selector, I update one line here — all tests using this
  page automatically pick up the fix."
"""
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage
from config.settings import Settings


class HomePage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────────────
    HEADING      = "h1"
    SUBHEADING   = "h2"
    EXAMPLE_LINK = lambda _, text: f'a:has-text("{text}")'

    def __init__(self, page: Page):
        super().__init__(page)

    # ── Actions ───────────────────────────────────────────────────────────────

    @allure.step("Open home page")
    def open(self) -> "HomePage":
        self.navigate(Settings.BASE_URL)
        return self

    @allure.step("Get main heading text")
    def get_heading(self) -> str:
        return self.get_text(self.HEADING)

    @allure.step("Click example link: {link_text}")
    def click_example(self, link_text: str):
        self.click(self.EXAMPLE_LINK(link_text), f"Example: {link_text}")

    @allure.step("Verify home page loaded")
    def verify_loaded(self) -> "HomePage":
        self.expect_visible(self.HEADING)
        self.expect_text(self.HEADING, "Welcome")
        return self
