import os
import time
from langsmith import traceable


@traceable(name="dom-capture")
def dom_capture(state):

    driver = state["driver"]

    dom = driver.page_source

    os.makedirs("healing_reports", exist_ok=True)

    screenshot_path = f"healing_reports/screenshot_{int(time.time())}.png"

    driver.save_screenshot(screenshot_path)

    return {

        "dom_snapshot": dom,

        "screenshot_path": screenshot_path
    }
