"""
Layer 3 — UTILS: ScreenshotHelper
Saves screenshots to report/playwright/screenshots/ and returns bytes for Allure.
"""
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page
from config.settings import Settings


class ScreenshotHelper:

    @staticmethod
    def capture(page: Page, name: str = "screenshot") -> bytes:
        Settings.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Settings.SCREENSHOT_DIR / f"{name}_{ts}.png"
        return page.screenshot(path=str(path))

    @staticmethod
    def capture_full_page(page: Page, name: str = "full_page") -> bytes:
        Settings.SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = Settings.SCREENSHOT_DIR / f"{name}_{ts}.png"
        return page.screenshot(path=str(path), full_page=True)
