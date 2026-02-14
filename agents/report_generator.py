def report_generator(state):

    report = {

        "failed_locator": state.get("failed_locator"),

        "healed_locator": state.get("healed_locator"),

        "confidence_score": state.get("confidence_score"),

        "success": state.get("success"),

        "screenshot_path": state.get("screenshot_path"),

        "logic_suggestion": state.get("logic_suggestion")
    }

    return {

        "report": report
    }
