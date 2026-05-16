from selenium.webdriver.common.by import By


def test_self_healing_login(driver):
    driver.get('https://the-internet.herokuapp.com/login')
    driver.type(By.ID, 'username', 'tomsmith')
    driver.type(By.ID, 'password', 'SuperSecretPassword!')
    driver.click(By.CSS_SELECTOR, "button[type='submit']")
