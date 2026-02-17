class PagePlanner:
    """
    Plans page structure based on structured test steps.
    Follows:
    - One page per module
    - POM
    - KISS
    - DRY
    """

    def plan(self, test_case: dict, structured_steps: list) -> dict:
        module_name = test_case["module"]

        page_name = f"{module_name}_page"
        locator_name = f"{module_name}_locators"
        test_name = f"test_{module_name}"

        methods = []
        locators = set()

        for step in structured_steps:
            action_type = step.get("action_type")
            field_name = step.get("field_name")

            if action_type == "enter_text":
                method_name = f"enter_{field_name}"
                locator_name_key = f"{field_name.upper()}_LOCATOR"

            elif action_type == "click":
                clean_field = field_name.replace(" ", "_")
                method_name = f"click_{clean_field}"
                locator_name_key = f"{clean_field.upper()}_LOCATOR"

            else:
                continue

            methods.append({
                "method_name": method_name,
                "action_type": action_type,
                "field_name": field_name
            })

            locators.add(locator_name_key)

        return {
            "page_name": page_name,
            "locator_file": locator_name,
            "test_file": test_name,
            "methods": methods,
            "locators": list(locators)
        }
