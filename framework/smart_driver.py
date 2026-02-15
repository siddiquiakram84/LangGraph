import traceback
import inspect

from core.healing_engine import HealingEngine
from utils.logger import log_healing_report
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



class SmartDriver:

    def __init__(self, driver):

        self.driver = driver

        self.healer = HealingEngine()

        self._healing_context = {}

    def get(self, url):

        self.driver.get(url)

        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def find_element(self, by, value):

        return self.driver.find_element(by, value)

    def click(self, by, value):

        self._execute_with_healing("click", by, value)

    def type(self, by, value, text):

        # store text in instance state so retry can reuse it safely
        self._healing_context = {

            "action": "type",

            "text": text
        }

        self._execute_with_healing("type", by, value)

    def _execute_with_healing(self, action_name, by, value):

        def execute(locator):

            wait = WebDriverWait(self.driver, 15)

            # ACTION-SPECIFIC WAIT
            if action_name == "click":

                element = wait.until(
                    EC.element_to_be_clickable(locator)
                )

                # scroll into view (VERY IMPORTANT for Amazon)
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});",
                    element
                )

                element.click()

            elif action_name == "type":

                element = wait.until(
                    EC.visibility_of_element_located(locator)
                )

                text = self._healing_context.get("text")

                tag = element.tag_name.lower()

                if tag in ["input", "textarea"]:

                    element.clear()
                    element.send_keys(text)

                else:
                    raise Exception(f"Element not typeable: {locator}")

            else:

                element = wait.until(
                    EC.presence_of_element_located(locator)
                )

        try:

            execute((by, value))

            return

        except Exception as original_error:

            report = self.healer.heal(

                driver=self.driver,

                failed_locator=(by, value),

                failed_action=action_name,

                error_message=str(original_error),

                stack_trace=traceback.format_exc(),

                test_file=inspect.stack()[2].filename
            )

            log_healing_report(report)

            if report.get("success"):

                healed = report["healed_locator"]

                execute(healed)

            else:

                raise original_error

    def quit(self):

        self.driver.quit()
