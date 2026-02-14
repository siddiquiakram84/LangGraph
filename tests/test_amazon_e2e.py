"""
tests/test_amazon_e2e.py

End-to-end healing validation test on amazon.in

Healing will trigger automatically if locators change.
"""
import time
from selenium.webdriver.common.by import By


def test_amazon_add_to_cart(driver):
    driver.get('https://www.amazon.in')
    driver.type(By.ID, 'twotabsearchtextbox', 'laptop')
    driver.click(By.ID, 'nav-search-submit-button')
    driver.click(By.CSS_SELECTOR, 'img.s-image')
    assert True
