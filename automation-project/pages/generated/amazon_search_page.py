# RAG context: similar script retrieved from FAISS store
# Source: amazon_search — TC_AMAZON_SEARCH_01 (score=0.48)

from locators.generated.amazon_search_locators import AmazonSearchLocators


class AmazonSearchPage:

    def __init__(self, page):
        self.page = page
        self.loc  = AmazonSearchLocators

    def click_search_button(self, value: str = ""):
        self.page.locator(self.loc.SEARCH_BUTTON_LOCATOR[0]).click()

    def click_first_product(self, value: str = ""):
        self.page.locator(self.loc.FIRST_PRODUCT_LOCATOR[0]).click()

    def click_add_to_cart_button(self, value: str = ""):
        self.page.locator(self.loc.ADD_TO_CART_BUTTON_LOCATOR[0]).click()
