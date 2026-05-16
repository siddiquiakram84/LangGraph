SUPPORTED_ACTIONS = {
    "click": "click",
    "enter_text": "enter_text",
    "get_text": "get_text",
    "wait_for_element": "wait_for_element"
}


class FrameworkCapabilityException(Exception):
    pass


def validate_action(action_type: str):
    if action_type not in SUPPORTED_ACTIONS:
        raise FrameworkCapabilityException(
            f"Unsupported action type: {action_type}. "
            f"Extend BasePage before generating code."
        )
