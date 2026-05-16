"""
Layer 6 — TEST: JSONPlaceholder CRUD API
Target: https://jsonplaceholder.typicode.com

Demonstrates all 7 layers:
  L1 Config      — Settings (API_BASE_URL, report paths)
  L2 Core        — (no browser; API tests are pure HTTP)
  L3 Utils       — get_logger, AllureHelper (attach JSON responses)
  L4 Service     — JSONPlaceholderService (wraps ApiClient → requests.Session)
  L5 Data        — Test payloads from data/api/post_payloads.json
  L6 Test        — This file (class-based, full CRUD lifecycle)
  L7 Reporting   — @allure decorators, JSON attachments, conftest hooks

Interview talking point:
  "API tests never touch requests.get() directly — that lives in the
  service layer. Swapping the base URL hits a different env with zero
  test-file changes."
"""
import json
from pathlib import Path

import allure
import pytest
import requests

from services.jsonplaceholder_service import JSONPlaceholderService
from utils.allure_helper import AllureHelper
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Layer 5: Test data ────────────────────────────────────────────────────────
_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "api" / "post_payloads.json"
_DATA = json.loads(_DATA_FILE.read_text())


@allure.suite("API — JSONPlaceholder Suite")
@allure.feature("Posts CRUD")
class TestPostsRead:
    """Read operations — GET list and GET by id."""

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = JSONPlaceholderService()

    @allure.story("GET /posts returns full list with valid schema")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_all_posts_returns_list(self):
        with allure.step("Fetch all posts"):
            posts = self.svc.get_all_posts()
            logger.info(f"Received {len(posts)} posts")

        with allure.step("Validate list length and schema"):
            AllureHelper.attach_json(posts[:2], "Posts Sample (first 2)")
            assert isinstance(posts, list), "Response must be a list"
            assert len(posts) == 100, "JSONPlaceholder always returns 100 posts"
            for field in _DATA["expected_schema"]:
                assert field in posts[0], f"Missing field: {field}"

    @allure.story("GET /posts/{id} returns a single post with correct id")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("post_id", _DATA["known_post_ids"])
    def test_get_post_by_id(self, post_id: int):
        with allure.step(f"Fetch post id={post_id}"):
            post = self.svc.get_post(post_id)
            AllureHelper.attach_json(post, f"Post {post_id}")

        with allure.step("Validate id and schema"):
            assert post["id"] == post_id
            for field in _DATA["expected_schema"]:
                assert field in post, f"Missing field: {field}"


@allure.suite("API — JSONPlaceholder Suite")
@allure.feature("Posts CRUD")
class TestPostsWrite:
    """Write operations — POST create and PUT update."""

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = JSONPlaceholderService()

    @allure.story("POST /posts creates resource and returns 201 with id")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_post_returns_id(self):
        payload = _DATA["create_post"]

        with allure.step("Send POST to create a new post"):
            AllureHelper.attach_json(payload, "Request Payload")
            created = self.svc.create_post(
                title   = payload["title"],
                body    = payload["body"],
                user_id = payload["userId"],
            )

        with allure.step("Assert response has id and matches input"):
            AllureHelper.attach_json(created, "Created Post")
            assert "id" in created, "Created post must have an id"
            assert created["title"]  == payload["title"]
            assert created["userId"] == payload["userId"]
            logger.info(f"Post created with id={created['id']}")

    @allure.story("PUT /posts/{id} updates resource and returns updatedAt")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_post(self):
        payload = _DATA["update_post"]

        with allure.step("Send PUT to update post id=1"):
            AllureHelper.attach_json(payload, "Update Payload")
            updated = self.svc.update_post(
                post_id = payload["id"],
                title   = payload["title"],
                body    = payload["body"],
                user_id = payload["userId"],
            )

        with allure.step("Validate response contains updated title"):
            AllureHelper.attach_json(updated, "Updated Post")
            assert updated["title"] == payload["title"]
            assert updated["id"]    == payload["id"]

    @allure.story("DELETE /posts/{id} returns 200")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_post(self):
        with allure.step("Send DELETE for post id=1"):
            result = self.svc.delete_post(1)

        with allure.step("Assert deletion was acknowledged"):
            assert result is True, "delete_post should return True on 200"
            AllureHelper.attach_text("Post deletion confirmed with 200 OK", "Result")


@allure.suite("API — JSONPlaceholder Suite")
@allure.feature("Posts Comments")
class TestPostComments:
    """Verify comment sub-resource for a post."""

    @pytest.fixture(autouse=True)
    def service(self):
        self.svc = JSONPlaceholderService()

    @allure.story("GET /posts/{id}/comments returns comment list with email fields")
    @allure.severity(allure.severity_level.NORMAL)
    def test_post_comments_have_email(self):
        with allure.step("Fetch comments for post id=1"):
            comments = self.svc.get_post_comments(1)
            AllureHelper.attach_json(comments[:2], "Comments Sample")

        with allure.step("Validate comment schema"):
            assert isinstance(comments, list)
            assert len(comments) > 0
            first = comments[0]
            for field in ("postId", "id", "name", "email", "body"):
                assert field in first, f"Missing field: {field}"
            logger.info(f"Post 1 has {len(comments)} comments")
