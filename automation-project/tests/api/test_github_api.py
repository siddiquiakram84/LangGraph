"""
Layer 6 — TEST: API Tests
GitHub REST API contract tests using GitHubApiService (Layer 4).

Interview talking point:
  "Service layer handles HTTP. Tests only assert on business data —
  they never construct URLs or parse raw responses."
"""
import allure
import pytest

from services.github_api_service import GitHubApiService
from utils.allure_helper import AllureHelper


@allure.suite("API — GitHub Service Suite")
@allure.feature("GitHub User API")
class TestGitHubUserAPI:

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = GitHubApiService()

    @allure.story("GET user returns 200 with valid schema")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_schema(self):
        with allure.step("Fetch public user: octocat"):
            user = self.svc.get_user("octocat")

        with allure.step("Validate required fields"):
            AllureHelper.attach_json(user, "User Response")
            assert user["login"] == "octocat"
            assert "id" in user
            assert "avatar_url" in user
            assert "public_repos" in user

    @allure.story("GET user repos returns list")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_user_repos_returns_list(self):
        with allure.step("Fetch repos for: octocat"):
            repos = self.svc.get_user_repos("octocat")

        with allure.step("Validate list structure"):
            AllureHelper.attach_json(repos[:2], "Repos Sample")
            assert isinstance(repos, list)
            if repos:
                assert "name" in repos[0]
                assert "full_name" in repos[0]

    @allure.story("Unknown user raises HTTP error")
    @allure.severity(allure.severity_level.NORMAL)
    def test_unknown_user_raises_error(self):
        import requests
        with allure.step("Request non-existent user"):
            with pytest.raises(requests.HTTPError):
                self.svc.get_user("__totally_nonexistent_user_xyz__")


@allure.suite("API — GitHub Search Suite")
@allure.feature("GitHub Search API")
class TestGitHubSearchAPI:

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = GitHubApiService()

    @allure.story("Search repos returns relevant results")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_repos_returns_results(self):
        with allure.step("Search for: playwright"):
            results = self.svc.search_repos("playwright+language:python", limit=5)

        with allure.step("Validate results are non-empty and have name field"):
            AllureHelper.attach_json({"count": len(results)}, "Search Result Count")
            assert isinstance(results, list)
            assert len(results) > 0
            assert "name" in results[0]

    @allure.story("Rate limit endpoint returns valid structure")
    @allure.severity(allure.severity_level.NORMAL)
    def test_rate_limit_schema(self):
        with allure.step("Fetch rate limit info"):
            data = self.svc.get_rate_limit()
        with allure.step("Validate schema"):
            AllureHelper.attach_json(data, "Rate Limit")
            assert "rate" in data or "resources" in data
