import os
import requests
from dataclasses import dataclass
from langsmith import traceable


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class AnthropicClient:
    """
    Claude-based LLM client for production use.
    Activated automatically when ANTHROPIC_API_KEY is set in .env.
    Tracks token usage per session for cost monitoring.
    """

    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self.session_usage = TokenUsage()

    @traceable(name="anthropic-generate")
    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

        self.session_usage.prompt_tokens += message.usage.input_tokens
        self.session_usage.completion_tokens += message.usage.output_tokens

        raw_output = message.content[0].text.strip()

        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`")
            raw_output = raw_output.replace("json", "").strip()

        return raw_output

    def get_session_usage(self) -> TokenUsage:
        return self.session_usage

    def reset_session_usage(self) -> None:
        self.session_usage = TokenUsage()


class OllamaClient:
    """
    Local Ollama client — fallback when no ANTHROPIC_API_KEY is set.
    Good for CI and local dev without API costs.
    """

    def __init__(self, model: str = "deepseek-coder:6.7b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"
        self.session_usage = TokenUsage()

    @traceable(name="ollama-generate")
    def generate(self, prompt: str, temperature: float = 0.1) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        response = requests.post(self.url, json=payload)

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        result = response.json()

        usage = TokenUsage(
            prompt_tokens=result.get("prompt_eval_count", 0),
            completion_tokens=result.get("eval_count", 0),
        )
        self.session_usage.prompt_tokens += usage.prompt_tokens
        self.session_usage.completion_tokens += usage.completion_tokens

        raw_output = result["response"].strip()

        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`")
            raw_output = raw_output.replace("json", "").strip()

        return raw_output

    def get_session_usage(self) -> TokenUsage:
        return self.session_usage

    def reset_session_usage(self) -> None:
        self.session_usage = TokenUsage()


def get_llm_client():
    """
    Router — returns AnthropicClient if ANTHROPIC_API_KEY is set,
    falls back to OllamaClient for local dev and CI.
    This is the tiered model routing pattern from the JD.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicClient()
    return OllamaClient()




