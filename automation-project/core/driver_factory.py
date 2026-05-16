"""
Layer 2 — CORE: DriverFactory
Playwright browser / context / page factory.
Single place to control browser launch options, viewport, video recording.
"""
from playwright.sync_api import Playwright, Browser, BrowserContext, Page
from config.settings import Settings


class DriverFactory:

    @staticmethod
    def create_browser(playwright: Playwright) -> Browser:
        browser_type = getattr(playwright, Settings.BROWSER)
        return browser_type.launch(headless=Settings.HEADLESS)

    @staticmethod
    def create_context(browser: Browser) -> BrowserContext:
        Settings.VIDEO_DIR.mkdir(parents=True, exist_ok=True)
        return browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(Settings.VIDEO_DIR),
            ignore_https_errors=True,
        )

    @staticmethod
    def create_page(context: BrowserContext) -> Page:
        page = context.new_page()
        page.set_default_timeout(Settings.DEFAULT_TIMEOUT)
        page.set_default_navigation_timeout(Settings.PAGE_LOAD_TIMEOUT)
        return page
