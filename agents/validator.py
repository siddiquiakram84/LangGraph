from langsmith import traceable


@traceable(name="validator")
def validator(state):

    driver = state["driver"]

    locator = state.get("healed_locator")

    if not locator:
        return {"success": False}

    try:

        driver.find_element(locator[0], locator[1])

        return {

            "validation_success": True,

            "success": True
        }

    except:

        return {

            "validation_success": False,

            "success": False
        }
