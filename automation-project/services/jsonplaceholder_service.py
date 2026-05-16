"""
Layer 4 — SERVICE: JSONPlaceholderService
Encapsulates all JSONPlaceholder REST API calls.
Tests never construct URLs or parse raw responses directly.

JSONPlaceholder is a free, public REST API for testing:
  https://jsonplaceholder.typicode.com
"""
from services.api_client import ApiClient
from utils.logger import get_logger

logger = get_logger(__name__)

_BASE_URL = "https://jsonplaceholder.typicode.com"


class JSONPlaceholderService:

    def __init__(self):
        self.client = ApiClient(_BASE_URL)

    # ── Posts ──────────────────────────────────────────────────────────────────

    def get_all_posts(self) -> list:
        resp = self.client.get("posts")
        resp.raise_for_status()
        logger.info(f"get_all_posts → {len(resp.json())} posts")
        return resp.json()

    def get_post(self, post_id: int) -> dict:
        resp = self.client.get(f"posts/{post_id}")
        resp.raise_for_status()
        return resp.json()

    def create_post(self, title: str, body: str, user_id: int = 1) -> dict:
        payload = {"title": title, "body": body, "userId": user_id}
        resp = self.client.post("posts", payload)
        resp.raise_for_status()
        logger.info(f"create_post → id={resp.json().get('id')}")
        return resp.json()

    def update_post(self, post_id: int, title: str, body: str, user_id: int = 1) -> dict:
        payload = {"id": post_id, "title": title, "body": body, "userId": user_id}
        resp = self.client.put(f"posts/{post_id}", payload)
        resp.raise_for_status()
        return resp.json()

    def delete_post(self, post_id: int) -> bool:
        resp = self.client.delete(f"posts/{post_id}")
        resp.raise_for_status()
        return resp.status_code == 200

    # ── Users ──────────────────────────────────────────────────────────────────

    def get_user(self, user_id: int) -> dict:
        resp = self.client.get(f"users/{user_id}")
        resp.raise_for_status()
        return resp.json()

    def get_user_posts(self, user_id: int) -> list:
        resp = self.client.get(f"users/{user_id}/posts")
        resp.raise_for_status()
        return resp.json()

    # ── Comments ─────────────────────────────────────────────────────────────

    def get_post_comments(self, post_id: int) -> list:
        resp = self.client.get(f"posts/{post_id}/comments")
        resp.raise_for_status()
        return resp.json()
