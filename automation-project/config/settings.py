"""
Layer 1 — CONFIG
Central settings loaded from environment / .env file.
All other layers import from here — no os.getenv() scattered elsewhere.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]   # langgraph-project/
PROJ = Path(__file__).resolve().parent.parent  # automation-project/


class Settings:
    # ── Browser ───────────────────────────────────────────────────────────────
    BROWSER: str  = os.getenv("BROWSER", "chromium")
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "60000"))

    # ── URLs ──────────────────────────────────────────────────────────────────
    BASE_URL: str     = os.getenv("BASE_URL", "https://the-internet.herokuapp.com")
    AMAZON_URL: str   = os.getenv("AMAZON_URL", "https://www.amazon.in")
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://api.github.com")

    # ── Report paths ──────────────────────────────────────────────────────────
    REPORT_DIR          = ROOT / "report"
    ALLURE_RESULTS_DIR  = REPORT_DIR / "allure" / "results"
    ALLURE_HTML_DIR     = REPORT_DIR / "allure" / "html"
    PLAYWRIGHT_DIR      = REPORT_DIR / "playwright"
    SCREENSHOT_DIR      = PLAYWRIGHT_DIR / "screenshots"
    VIDEO_DIR           = PLAYWRIGHT_DIR / "videos"
    PDF_DIR             = PLAYWRIGHT_DIR / "pdf"
    ANALYTICS_DIR       = REPORT_DIR / "analytics"
