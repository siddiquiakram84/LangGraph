import allure
import pytest
from playwright.sync_api import Page
from src.pages.generated.amazon_search_page import AmazonSearchPage


@allure.suite('Generated — amazon_search_page')
@allure.feature('Amazon Search Page')
def test_amazon_search_page(page: Page):
    po = AmazonSearchPage(page)
    po.click_search_button()
    po.click_first_product()
    po.click_add_to_cart_button()
