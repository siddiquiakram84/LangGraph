from langsmith import traceable


@traceable(name="logic-healer")
def logic_healer(state):

    error = state.get("error_message", "")

    suggestion = None

    if "AssertionError" in error:
        suggestion = "Verify expected assertion value."

    return {

        "logic_suggestion": suggestion
    }
