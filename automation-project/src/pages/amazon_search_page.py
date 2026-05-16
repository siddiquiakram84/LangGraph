from src.pages.base_page import BasePage
from src.locators.amazon_search_locators import AmazonSearchLocators


class AmazonSearchPage(BasePage):

    def __init__(self, driver):
        super().__init__(driver)
        self.locators = AmazonSearchLocators


    def enter_search_box(self, value=None):

        element = self.driver.find_element(*self.locators.SEARCH_BOX_LOCATOR)
        element.clear()
        element.send_keys(value)


    def click_search_button(self, value=None):

        element = self.driver.find_element(*self.locators.SEARCH_BUTTON_LOCATOR)
        element.click()


    def click_first_product(self, value=None):

        element = self.driver.find_element(*self.locators.FIRST_PRODUCT_LOCATOR)
        element.click()


    def click_add_to_cart_button(self, value=None):

        element = self.driver.find_element(*self.locators.ADD_TO_CART_BUTTON_LOCATOR)
        element.click()


