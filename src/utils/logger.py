import json
import time
import os
import allure


def log_healing_report(report):

    os.makedirs("healing_reports", exist_ok=True)

    path = f"healing_reports/healing_{int(time.time())}.json"

    with open(path, "w") as f:

        json.dump(report, f, indent=4)

    # Attach to Allure
    if report.get("screenshot_path"):

        allure.attach.file(

            report["screenshot_path"],

            name="Healing Screenshot",

            attachment_type=allure.attachment_type.PNG
        )

    allure.attach(

        json.dumps(report, indent=4),

        name="Healing Report",

        attachment_type=allure.attachment_type.JSON
    )
