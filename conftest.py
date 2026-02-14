import pytest
from selenium import webdriver

from framework.smart_driver import SmartDriver


@pytest.fixture
def driver():

    raw_driver = webdriver.Chrome()

    driver = SmartDriver(raw_driver)

    yield driver

    driver.quit()
