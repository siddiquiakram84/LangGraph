import requests
import json


class OllamaClient:
    def __init__(self, model="deepseek-coder:6.7b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        print("Sending request to Ollama...")

        response = requests.post(self.url, json=payload)

        print("Status code:", response.status_code)

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        result = response.json()
        print("Raw response:", result)

        result = response.json()
        raw_output = result["response"].strip()

        # Remove markdown code blocks if present
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`")
            raw_output = raw_output.replace("json", "").strip()

        return raw_output




