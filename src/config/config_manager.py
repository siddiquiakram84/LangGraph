"""
Layer: Config
Responsibility: Environment-aware configuration. Single source of truth.
Tests never read env vars directly — they go through this class.
"""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    base_url_amazon: str
    base_url_linkedin: str
    base_url_linkedin_api: str
    headless: bool
    slow_mo: int
    timeout: int
    viewport_width: int
    viewport_height: int
    allure_results_dir: str


def get_config() -> Config:
    env = os.getenv("ENV", "staging")
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    urls = {
        "prod": {
            "amazon":        "https://www.amazon.in",
            "linkedin":      "https://www.linkedin.com",
            "linkedin_api":  "https://api.linkedin.com/v2",
        },
        "staging": {
            "amazon":        "https://www.amazon.in",
            "linkedin":      "https://www.linkedin.com",
            "linkedin_api":  "https://api.linkedin.com/v2",
        },
    }

    env_urls = urls.get(env, urls["staging"])

    return Config(
        base_url_amazon=env_urls["amazon"],
        base_url_linkedin=env_urls["linkedin"],
        base_url_linkedin_api=env_urls["linkedin_api"],
        headless=headless,
        slow_mo=int(os.getenv("SLOW_MO", "0")),
        timeout=int(os.getenv("TIMEOUT_MS", "15000")),
        viewport_width=1280,
        viewport_height=800,
        allure_results_dir="allure-results",
    )
