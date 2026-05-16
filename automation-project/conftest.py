"""
Layer 7 — REPORTING: conftest.py
Root conftest for the automation-project.

Responsibilities:
  1. Adds automation-project/ to sys.path so all 7 layers import cleanly.
  2. Provides session-scoped Playwright fixtures (browser, context, page).
  3. Auto-captures screenshots + attaches to Allure on every test failure.
  4. Writes per-test PDF summary via PDFHelper.
"""
import sys
from pathlib import Path

# Make 'config', 'core', 'pages', 'services', 'utils' importable from tests.
sys.path.insert(0, str(Path(__file__).parent))

import allure
import pytest
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from core.driver_factory import DriverFactory
from utils.allure_helper import AllureHelper
from utils.screenshot_helper import ScreenshotHelper
from utils.pdf_helper import PDFHelper
from utils.logger import get_logger

logger = get_logger("conftest")


# ── Playwright fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance) -> Browser:
    b = DriverFactory.create_browser(playwright_instance)
    logger.info("Browser launched")
    yield b
    b.close()


@pytest.fixture(scope="session")
def context(browser) -> BrowserContext:
    ctx = DriverFactory.create_context(browser)
    yield ctx
    ctx.close()


@pytest.fixture
def page(context) -> Page:
    p = DriverFactory.create_page(context)
    yield p
    p.close()


# ── Auto-screenshot on failure (Layer 7) ──────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page:
            try:
                data = ScreenshotHelper.capture(page, item.name)
                AllureHelper.attach_screenshot(data, "Failure Screenshot")
                AllureHelper.attach_page_source(page)
            except Exception:
                pass
        PDFHelper.write_summary(item.name, "failed", [],
                                str(rep.longrepr) if rep.longrepr else "")
    elif rep.when == "call" and rep.passed:
        PDFHelper.write_summary(item.name, "passed", [])
