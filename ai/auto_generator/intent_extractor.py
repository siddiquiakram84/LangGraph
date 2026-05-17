import json
from ai.auto_generator.llm_client import get_llm_client


class IntentExtractor:
    """
    Converts plain-English test steps into structured JSON intent.
    Uses Claude (if ANTHROPIC_API_KEY is set) or Ollama as fallback.
    """

    def __init__(self):
        self.llm = get_llm_client()

    def extract_from_step(self, step_text: str) -> dict:
        prompt = f"""
You are an automation intent extractor for UI test steps.

Return ONLY valid JSON. No explanation, no markdown, no code blocks.

Strict format:
{{
  "action_type": "<enter_text or click>",
  "field_name": "<short snake_case element name>",
  "value": "<text to type, or empty string>"
}}

Rules:
- action_type MUST be exactly "enter_text" (filling an input) or "click" (pressing a button/link)
- field_name MUST be a short snake_case word: username, password, login_button, search_box
- NEVER add "_locator" or "_field" or "_input" to field_name
- value: the text to type for enter_text, empty string "" for click actions
- Navigate/open/go to steps: treat as "click" on the page link element

Sentence:
{step_text}
"""

        response = self.llm.generate(prompt)

        return json.loads(response)

    def extract_from_test_case(self, test_case: dict) -> list:
        structured_steps = []

        for step in test_case["steps"]:
            step_text = step["tc_msg_action"]
            structured = self.extract_from_step(step_text)
            structured_steps.append(structured)

        return structured_steps
