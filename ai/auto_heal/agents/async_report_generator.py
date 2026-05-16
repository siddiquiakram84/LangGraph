"""
agents/async_report_generator.py

Async version of report_generator — used when the pipeline runs in an
async context (e.g., FastAPI endpoint or async LangGraph execution).

Interview talking point:
  "The JD asks for pytest-asyncio. I made the report generator async
  because in production it could call an async Jira API to post results.
  Tests use @pytest.mark.asyncio with asyncio_mode=auto in pytest.ini."
"""
from langsmith import traceable


@traceable(name="async-report-generator")
async def async_report_generator(state: dict) -> dict:
    report = {
        "failed_locator": state.get("failed_locator"),
        "healed_locator": state.get("healed_locator"),
        "confidence_score": state.get("confidence_score"),
        "success": state.get("success"),
        "screenshot_path": state.get("screenshot_path"),
        "logic_suggestion": state.get("logic_suggestion"),
    }
    return {"report": report}
