"""
Layer 5 — PAGE OBJECT: SearchResultsPage
Represents the login / results page of the-internet.herokuapp.com.
Follows the same POM pattern as HomePage.

Interview talking point:
  "Page classes return 'self' or another page object from action methods.
  This enables fluent chaining: home.open().navigate_to_login().login(...)"
"""
import allure
from playwright.sync_api import Page
from pages.base_page import BasePage


class LoginPage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────────────
    USERNAME_INPUT = "#username"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON   = "button[type='submit']"
    SUCCESS_FLASH  = ".flash.success"
    ERROR_FLASH    = ".flash.error"

    URL = "https://the-internet.herokuapp.com/login"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Open login page")
    def open(self) -> "LoginPage":
        self.navigate(self.URL)
        return self

    @allure.step("Login with username='{username}'")
    def login(self, username: str, password: str) -> "LoginPage":
        self.fill(self.USERNAME_INPUT, username, "Username")
        self.fill(self.PASSWORD_INPUT, password, "Password")
        self.click(self.LOGIN_BUTTON, "Login button")
        return self

    @allure.step("Verify login success")
    def expect_success(self) -> "LoginPage":
        self.expect_visible(self.SUCCESS_FLASH)
        self.expect_text(self.SUCCESS_FLASH, "You logged into a secure area")
        return self

    @allure.step("Verify login error")
    def expect_error(self, message: str = "") -> "LoginPage":
        self.expect_visible(self.ERROR_FLASH)
        if message:
            self.expect_text(self.ERROR_FLASH, message)
        return self


class SearchResultsPage(LoginPage):
    """Alias kept so the 7-layer diagram naming is accurate in test imports."""
    pass
