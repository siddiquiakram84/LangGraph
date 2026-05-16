"""
Layer 6 — TEST: UI Tests
Page Object tests against the-internet.herokuapp.com.

Architecture pattern:
  Test → PageObject → BasePage → Playwright
  Test never calls page.locator() directly — always goes through POM.

Allure decorators provide structured reporting (Layer 7).
"""
import allure
import pytest
from playwright.sync_api import Page

from pages.home_page import HomePage
from pages.search_results_page import LoginPage, SearchResultsPage


@allure.suite("UI — Navigation Suite")
@allure.feature("Home Page")
class TestHomePage:

    @allure.story("Home page loads correctly")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_homepage_loads(self, page: Page):
        home = HomePage(page)
        home.open().verify_loaded()

    @allure.story("Home page title is correct")
    @allure.severity(allure.severity_level.NORMAL)
    def test_homepage_title(self, page: Page):
        home = HomePage(page)
        home.open()
        home.expect_title("The Internet")

    @allure.story("Heading content is visible")
    @allure.severity(allure.severity_level.NORMAL)
    def test_heading_contains_welcome(self, page: Page):
        home = HomePage(page)
        home.open()
        heading = home.get_heading()
        assert "Welcome" in heading


@allure.suite("UI — Authentication Suite")
@allure.feature("Login Page")
class TestLoginPage:

    @allure.story("Valid credentials succeed")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_valid_login(self, page: Page):
        LoginPage(page).open().login("tomsmith", "SuperSecretPassword!").expect_success()

    @allure.story("Invalid credentials show error")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_login_shows_error(self, page: Page):
        LoginPage(page).open().login("wrong", "credentials").expect_error("Your username is invalid")

    @allure.story("Empty username shows error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_empty_username_shows_error(self, page: Page):
        LoginPage(page).open().login("", "password").expect_error()


@allure.suite("UI — Network Suite")
@allure.feature("Network Interception")
class TestNetworkInterception:

    @allure.story("Requests are captured during navigation")
    @allure.severity(allure.severity_level.NORMAL)
    def test_network_requests_captured(self, page: Page):
        captured = []
        page.on("request", lambda req: captured.append({"url": req.url, "method": req.method}))

        with allure.step("Navigate and trigger network calls"):
            page.goto("https://the-internet.herokuapp.com")

        with allure.step("Assert requests were captured"):
            allure.attach(str(captured), name="captured_requests",
                          attachment_type=allure.attachment_type.TEXT)
            assert len(captured) > 0
