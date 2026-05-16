"""
Layer 6 — TEST: Authentication Flow
Target: https://the-internet.herokuapp.com/login

Demonstrates all 7 layers:
  L1 Config      — Settings (BASE_URL, timeouts)
  L2 Core        — DriverFactory via conftest fixtures
  L3 Utils       — get_logger, AllureHelper, ScreenshotHelper (via conftest)
  L4 Data        — LoginCredentials loaded from data/ui/login_credentials.json
  L5 Pages       — LoginPage (extends BasePage)
  L6 Test        — This file (class-based, data-driven)
  L7 Reporting   — @allure decorators + conftest auto-screenshot hook
"""
import json
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Page

from pages.search_results_page import LoginPage
from utils.allure_helper import AllureHelper
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Layer 4: Test data loaded from data/ ──────────────────────────────────────
_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "ui" / "login_credentials.json"
_CREDS = json.loads(_DATA_FILE.read_text())


# ── Layer 6: Test classes ─────────────────────────────────────────────────────

@allure.suite("UI — Authentication Suite")
@allure.feature("Login Page")
class TestValidLogin:
    """Happy path: valid credentials → secure area."""

    @allure.story("Valid user lands on secure area")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("cred", _CREDS["valid"])
    def test_valid_login_reaches_secure_area(self, page: Page, cred: dict):
        with allure.step("Load test data"):
            AllureHelper.attach_json(cred, "Credentials")
            logger.info(f"Testing valid login: user={cred['username']}")

        with allure.step("Open login page and submit credentials"):
            lp = LoginPage(page).open().login(cred["username"], cred["password"])

        with allure.step("Assert success message is visible"):
            lp.expect_success()
            lp.expect_text(LoginPage.SUCCESS_FLASH, cred["expected_text"])
            AllureHelper.attach_text(
                f"Login succeeded for user: {cred['username']}", "Login Result"
            )

    @allure.story("Logout returns user to login page")
    @allure.severity(allure.severity_level.NORMAL)
    def test_logout_returns_to_login(self, page: Page):
        cred = _CREDS["valid"][0]

        with allure.step("Login with valid credentials"):
            lp = LoginPage(page).open().login(cred["username"], cred["password"])
            lp.expect_success()

        with allure.step("Click logout link"):
            lp.click("a[href='/logout']", "Logout link")

        with allure.step("Verify redirect back to login page"):
            import re
            lp.expect_url(re.compile(r".*/login"))
            logger.info("Logout successful — redirected to login")


@allure.suite("UI — Authentication Suite")
@allure.feature("Login Page")
class TestInvalidLogin:
    """Negative path: wrong credentials → error flash messages."""

    @allure.story("Invalid credentials show specific error message")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("cred", _CREDS["invalid"])
    def test_invalid_login_shows_error(self, page: Page, cred: dict):
        with allure.step("Load negative test data"):
            safe_cred = {k: v for k, v in cred.items() if k != "password"}
            AllureHelper.attach_json(safe_cred, "Test Input (password redacted)")
            logger.info(f"Testing invalid login: user='{cred['username']}'")

        with allure.step("Submit invalid credentials"):
            lp = LoginPage(page).open().login(cred["username"], cred["password"])

        with allure.step("Assert error flash is visible with correct message"):
            lp.expect_error(cred["expected_error"])
            AllureHelper.attach_text(
                f"Error verified: {cred['expected_error']}", "Validation Result"
            )
