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
You are an automation intent extractor.

Return ONLY valid JSON.
Do NOT explain.
Do NOT return code.
Do NOT add markdown.

Format strictly like this:
{{
  "action_type": "",
  "field_name": "",
  "value": ""
}}

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
