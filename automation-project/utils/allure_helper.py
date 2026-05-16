"""
Layer 3 — UTILS: AllureHelper
Centralised Allure attachment helpers — keeps test files clean.
"""
import json
import allure
from playwright.sync_api import Page


class AllureHelper:

    @staticmethod
    def attach_screenshot(data: bytes, name: str = "Screenshot"):
        allure.attach(data, name=name, attachment_type=allure.attachment_type.PNG)

    @staticmethod
    def attach_text(text: str, name: str = "Log"):
        allure.attach(text, name=name, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_json(data: dict | list | str, name: str = "Response"):
        body = json.dumps(data, indent=2) if not isinstance(data, str) else data
        allure.attach(body, name=name, attachment_type=allure.attachment_type.JSON)

    @staticmethod
    def attach_html(html: str, name: str = "Page Source"):
        allure.attach(html, name=name, attachment_type=allure.attachment_type.HTML)

    @staticmethod
    def attach_page_source(page: Page, name: str = "Page Source"):
        AllureHelper.attach_html(page.content(), name)

    @staticmethod
    def step(description: str):
        return allure.step(description)
