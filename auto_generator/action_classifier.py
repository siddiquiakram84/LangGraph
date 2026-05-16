import re


class ActionClassifier:
    """
    Converts manual test step text into structured automation intent.
    """

    def classify(self, step: dict) -> dict:
        action_text = step["tc_msg_action"].lower()

        if "enter" in action_text and "search box" in action_text:
            return self._handle_input(action_text, field="search_box")

        if "enter" in action_text:
            return self._handle_input(action_text)

        if "click" in action_text:
            return self._handle_click(action_text)

        return {
            "action_type": "unknown",
            "raw_text": action_text
        }

    def _handle_input(self, action_text: str, field: str = None) -> dict:
        # Extract value between "as" and "in"
        value_match = re.search(r"as (.+?) in", action_text)

        # Fallback if "in" not present
        if not value_match:
            value_match = re.search(r"as (.+)", action_text)

        value = value_match.group(1).strip() if value_match else None

        return {
            "action_type": "input",
            "field_name": field,
            "value": value
        }

    def _handle_click(self, action_text: str) -> dict:
        if "first product" in action_text:
            target = "first_product"
        elif "search button" in action_text:
            target = "search_button"
        elif "add to cart" in action_text:
            target = "add_to_cart_button"
        else:
            target = "generic_click"

        return {
            "action_type": "click",
            "target": target
        }
