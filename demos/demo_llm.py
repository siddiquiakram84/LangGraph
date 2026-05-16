from ai.auto_generator.llm_client import OllamaClient

client = OllamaClient()

prompt = """
You are an automation intent extractor.

Return ONLY valid JSON.
Do NOT explain.
Do NOT return code.
Do NOT add markdown.

Format strictly like this:
{
  "action_type": "",
  "field_name": "",
  "value": ""
}

Sentence:
Enter product name as iphone 15 in search box
"""

response = client.generate(prompt)

print("\nLLM Response:\n")
print(response)
