"""
Layer 6 — TEST: GitHub Public API
Target: https://api.github.com

Demonstrates all 7 layers:
  L1 Config      — Settings (API_BASE_URL, report paths)
  L2 Core        — (no browser; API tests are pure HTTP)
  L3 Utils       — get_logger, AllureHelper (attach JSON responses)
  L4 Service     — GitHubApiService (wraps ApiClient → requests.Session)
  L5 Data        — Test users / queries from data/api/github_users.json
  L6 Test        — This file (class-based, data-driven with parametrize)
  L7 Reporting   — @allure decorators, JSON attachments, conftest hooks

Interview talking point:
  "No auth token needed for read-only GitHub endpoints. The service
  layer encapsulates all URL building — tests stay clean and readable."
"""
import json
from pathlib import Path

import allure
import pytest
import requests

from services.github_api_service import GitHubApiService
from utils.allure_helper import AllureHelper
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Layer 5: Test data ────────────────────────────────────────────────────────
_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "api" / "github_users.json"
_DATA = json.loads(_DATA_FILE.read_text())


@allure.suite("API — GitHub Suite")
@allure.feature("GitHub User API")
class TestGitHubUserProfile:
    """Validate public user profile endpoint schema and business data."""

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = GitHubApiService()

    @allure.story("GET /users/{username} returns valid profile schema")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("user_data", _DATA["test_users"])
    def test_user_profile_schema(self, user_data: dict):
        username = user_data["username"]

        with allure.step(f"Fetch GitHub profile for: {username}"):
            AllureHelper.attach_json(user_data, "Test Input")
            user = self.svc.get_user(username)

        with allure.step("Validate login and required fields"):
            AllureHelper.attach_json(user, "User Profile Response")
            assert user["login"] == user_data["expected_login"]
            for field in user_data["required_fields"]:
                assert field in user, f"Missing required field: {field}"
            logger.info(f"User {username}: id={user['id']}, repos={user['public_repos']}")

    @allure.story("GET /users/{username}/repos returns a list of repos")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_user_repos_returns_list(self):
        user_data = _DATA["test_users"][0]

        with allure.step(f"Fetch repos for: {user_data['username']}"):
            repos = self.svc.get_user_repos(user_data["username"])

        with allure.step("Validate repo list structure"):
            AllureHelper.attach_json(repos[:2], "Repos Sample (first 2)")
            assert isinstance(repos, list), "Repos response must be a list"
            if repos:
                assert "name"      in repos[0], "Repo must have 'name'"
                assert "full_name" in repos[0], "Repo must have 'full_name'"
            logger.info(f"Found {len(repos)} repos for {user_data['username']}")

    @allure.story("Unknown username raises HTTP 404")
    @allure.severity(allure.severity_level.NORMAL)
    def test_nonexistent_user_raises_404(self):
        username = _DATA["nonexistent_user"]

        with allure.step(f"Request profile for nonexistent user: {username}"):
            with pytest.raises(requests.HTTPError) as exc_info:
                self.svc.get_user(username)

        with allure.step("Verify 404 status code"):
            assert "404" in str(exc_info.value) or exc_info.value.response.status_code == 404
            AllureHelper.attach_text(f"404 confirmed for '{username}'", "Error Verification")


@allure.suite("API — GitHub Suite")
@allure.feature("GitHub Search API")
class TestGitHubSearch:
    """Validate GitHub search endpoint returns relevant results."""

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = GitHubApiService()

    @allure.story("Search returns non-empty result list with 'name' field")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("query_data", _DATA["search_queries"])
    def test_search_repos_returns_results(self, query_data: dict):
        with allure.step(f"Search repos: q={query_data['q']}"):
            AllureHelper.attach_json(query_data, "Search Input")
            results = self.svc.search_repos(query_data["q"], limit=5)

        with allure.step("Validate results are non-empty and correctly structured"):
            AllureHelper.attach_json(
                {"count": len(results), "first_result": results[0] if results else None},
                "Search Result Summary"
            )
            assert isinstance(results, list)
            assert len(results) >= query_data["min_results"]
            assert "name" in results[0], "Each result must have a 'name' field"
            logger.info(f"Search '{query_data['q']}' → {len(results)} results")

    @allure.story("Rate limit endpoint returns valid resource structure")
    @allure.severity(allure.severity_level.NORMAL)
    def test_rate_limit_schema(self):
        with allure.step("Fetch rate limit info"):
            data = self.svc.get_rate_limit()

        with allure.step("Validate top-level rate limit schema"):
            AllureHelper.attach_json(data, "Rate Limit Response")
            assert "rate" in data or "resources" in data, (
                "Rate limit response must contain 'rate' or 'resources'"
            )
            if "resources" in data:
                assert "core" in data["resources"]
            logger.info("Rate limit schema validated")
