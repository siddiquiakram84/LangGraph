"""
Playwright fixtures for UI tests.
Uses sync_playwright so tests stay compatible with standard pytest (no asyncio needed).
"""
import pytest
import allure
from playwright.sync_api import sync_playwright, Page, Browser


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture
def page(browser: Browser):
    context = browser.new_context(
        record_video_dir="healing_reports/videos/",
    )
    pg = context.new_page()
    pg.on("console", lambda msg: None)
    yield pg
    # Attach screenshot to Allure on failure
    screenshot = pg.screenshot()
    allure.attach(screenshot, name="screenshot", attachment_type=allure.attachment_type.PNG)
    context.close()
