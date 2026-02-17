import pytest
from src.pages.amazon_search_page import AmazonSearchPage


@pytest.mark.smoke
def test_amazon_search_page(driver):
    page = AmazonSearchPage(driver)

    page.enter_search_box()
    page.click_search_button()
    page.click_first_product()
    page.click_add_to_cart_button()
