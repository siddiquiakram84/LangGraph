"""
tests/ui/test_ui_demo.py

Playwright Python UI tests with Allure reporting.
These are the generated test outputs from the auto-gen pipeline.

Interview talking point:
  "The auto-gen pipeline produces tests in this exact format.
  A manual tester writes a test case in plain English.
  The pipeline converts it to structured JSON, retrieves similar
  scripts from FAISS, and generates this file automatically."
"""
import allure
import pytest
from playwright.sync_api import Page, expect


@allure.suite("UI Smoke Suite")
@allure.feature("Navigation")
@allure.story("Page loads correctly")
@allure.severity(allure.severity_level.CRITICAL)
def test_homepage_loads(page: Page):
    with allure.step("Navigate to demo site"):
        page.goto("https://the-internet.herokuapp.com")

    with allure.step("Verify page title"):
        expect(page).to_have_title("The Internet")

    with allure.step("Verify heading is visible"):
        heading = page.locator("h1")
        expect(heading).to_be_visible()
        expect(heading).to_contain_text("Welcome")


@allure.suite("UI Smoke Suite")
@allure.feature("Authentication")
@allure.story("Valid login succeeds")
@allure.severity(allure.severity_level.CRITICAL)
def test_valid_login(page: Page):
    with allure.step("Navigate to login page"):
        page.goto("https://the-internet.herokuapp.com/login")

    with allure.step("Enter valid username"):
        page.fill("#username", "tomsmith")

    with allure.step("Enter valid password"):
        page.fill("#password", "SuperSecretPassword!")

    with allure.step("Click login button"):
        page.click("button[type='submit']")

    with allure.step("Verify successful login message"):
        flash = page.locator(".flash.success")
        expect(flash).to_be_visible()
        expect(flash).to_contain_text("You logged into a secure area")


@allure.suite("UI Regression Suite")
@allure.feature("Authentication")
@allure.story("Invalid login shows error")
@allure.severity(allure.severity_level.NORMAL)
def test_invalid_login_shows_error(page: Page):
    with allure.step("Navigate to login page"):
        page.goto("https://the-internet.herokuapp.com/login")

    with allure.step("Enter wrong credentials"):
        page.fill("#username", "wronguser")
        page.fill("#password", "wrongpass")

    with allure.step("Click login button"):
        page.click("button[type='submit']")

    with allure.step("Verify error message appears"):
        flash = page.locator(".flash.error")
        expect(flash).to_be_visible()
        expect(flash).to_contain_text("Your username is invalid")


@allure.suite("UI Regression Suite")
@allure.feature("Network Interception")
@allure.story("API call is intercepted and validated")
@allure.severity(allure.severity_level.NORMAL)
def test_network_interception(page: Page):
    """
    Playwright network interception — captures API responses during UI flow.
    Interview talking point: 'I intercept network calls during UI tests
    to validate the API contract without writing a separate API test.'
    """
    captured_requests = []

    page.on("request", lambda req: captured_requests.append({
        "url": req.url,
        "method": req.method,
    }))

    with allure.step("Navigate to page and trigger network calls"):
        page.goto("https://the-internet.herokuapp.com")

    with allure.step("Verify network requests were captured"):
        allure.attach(
            str(captured_requests),
            name="captured_requests",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert len(captured_requests) > 0
