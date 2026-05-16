"""
Layer 4 — SERVICE: GitHubApiService
Encapsulates GitHub REST API calls. Tests import only this service —
no raw requests in test files.

Interview talking point:
  "Service layer decouples tests from HTTP. Swap URL in Settings and
  every test that uses GitHubApiService works against a different env."
"""
from config.settings import Settings
from services.api_client import ApiClient


class GitHubApiService:

    def __init__(self):
        self.client = ApiClient(Settings.API_BASE_URL)

    def get_user(self, username: str) -> dict:
        resp = self.client.get(f"users/{username}")
        resp.raise_for_status()
        return resp.json()

    def get_user_repos(self, username: str) -> list:
        resp = self.client.get(f"users/{username}/repos?per_page=10")
        resp.raise_for_status()
        return resp.json()

    def search_repos(self, query: str, limit: int = 5) -> list:
        resp = self.client.get(f"search/repositories?q={query}&per_page={limit}")
        resp.raise_for_status()
        return resp.json().get("items", [])

    def get_rate_limit(self) -> dict:
        resp = self.client.get("rate_limit")
        resp.raise_for_status()
        return resp.json()
