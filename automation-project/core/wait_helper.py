"""
Layer 2 — CORE: WaitHelper
Smart waits that wrap Playwright's built-in mechanisms.
Centralises timeout strategy so tests never call page.wait_for_* directly.
"""
from playwright.sync_api import Page, Locator, expect
from config.settings import Settings


class WaitHelper:

    @staticmethod
    def for_element(page: Page, selector: str, timeout: int = None) -> Locator:
        t = timeout or Settings.DEFAULT_TIMEOUT
        locator = page.locator(selector)
        locator.wait_for(state="visible", timeout=t)
        return locator

    @staticmethod
    def for_network_idle(page: Page, timeout: int = None):
        page.wait_for_load_state("networkidle", timeout=timeout or Settings.PAGE_LOAD_TIMEOUT)

    @staticmethod
    def for_url(page: Page, pattern: str, timeout: int = None):
        page.wait_for_url(pattern, timeout=timeout or Settings.DEFAULT_TIMEOUT)

    @staticmethod
    def for_text(page: Page, selector: str, text: str):
        expect(page.locator(selector)).to_contain_text(text)

    @staticmethod
    def for_hidden(page: Page, selector: str, timeout: int = None):
        page.locator(selector).wait_for(state="hidden", timeout=timeout or Settings.DEFAULT_TIMEOUT)
